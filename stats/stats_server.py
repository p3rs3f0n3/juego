#!/usr/bin/env python3
"""Contador de visitas y estadisticas de Ticket Rush.

Solo usa la libreria estandar de Python (sin pip). Guarda todo en SQLite.
No guarda IPs: cada navegador manda un identificador al azar. El apodo es opcional.

  POST /api/visit   {"v": id, "m": 1|0}                 se abrio el juego (m = celular)
  POST /api/start   {"v": id}                           empezo una partida
  POST /api/end     {"v": id, "g": partida, "score",    termino (o abandono, "a": 1) una partida
                     "tickets", "rank", "secs", "why", "dist", "n": apodo}
  POST /api/name    {"v": id, "n": apodo}               guardar apodo ("" = anonimo); 422 si no se permite
  GET  /api/board?v=id                                  tabla de lideres publica (semana e historica)
  GET  /stats       pagina de estadisticas (Caddy la protege con usuario y clave)
  POST /stats/hide  ocultar o mostrar el apodo de un jugador (desde /stats)
  POST /stats/season empezar una temporada nueva: la tabla arranca de cero y la anterior queda en el
                    salon de la fama (no se borra nada)

Variables de entorno: STATS_DB (ruta de la base), STATS_PORT (por defecto 8095),
STATS_STATIC (solo para probar en local: carpeta desde donde servir el juego).
"""
import html
import json
import mimetypes
import os
import re
import sqlite3
import unicodedata
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB = os.environ.get("STATS_DB", "stats.db")
PORT = int(os.environ.get("STATS_PORT", "8095"))
STATIC = os.environ.get("STATS_STATIC")
TZ = timezone(timedelta(hours=-5))  # hora de Colombia
RANKS = ["Practicante", "Analista", "Jefe de TI"]
VID = re.compile(r"^[a-z0-9-]{4,40}$")


def db():
    c = sqlite3.connect(DB, timeout=5)
    c.row_factory = sqlite3.Row
    return c


def init():
    with db() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS visits (ts INTEGER, visitor TEXT, mobile INTEGER);
            CREATE TABLE IF NOT EXISTS starts (ts INTEGER, visitor TEXT);
            CREATE TABLE IF NOT EXISTS games  (ts INTEGER, visitor TEXT, score INTEGER, tickets INTEGER,
                                               rank INTEGER, secs INTEGER, why TEXT);
            CREATE INDEX IF NOT EXISTS games_score ON games(score);
        """)
        cols = [r[1] for r in c.execute("PRAGMA table_info(games)")]
        if "gid" not in cols:  # bases creadas antes de registrar partidas abandonadas
            c.execute("ALTER TABLE games ADD COLUMN gid TEXT")
            c.execute("ALTER TABLE games ADD COLUMN abandoned INTEGER DEFAULT 0")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS games_gid ON games(gid)")
        if "dist" not in cols:  # veces que distrajo al jefe con la companera
            c.execute("ALTER TABLE games ADD COLUMN dist INTEGER DEFAULT 0")
        c.execute("CREATE TABLE IF NOT EXISTS players (visitor TEXT PRIMARY KEY, name TEXT, hidden INTEGER DEFAULT 0, ts INTEGER)")
        # Temporadas: la tabla de lideres solo cuenta desde el inicio de la temporada actual.
        c.execute("CREATE TABLE IF NOT EXISTS seasons (id INTEGER PRIMARY KEY AUTOINCREMENT, start INTEGER, name TEXT)")
        if not c.execute("SELECT COUNT(*) FROM seasons").fetchone()[0]:
            c.execute("INSERT INTO seasons (start, name) VALUES (0, 'Temporada 1')")


def seasons(c):
    return c.execute("SELECT id, start, name FROM seasons ORDER BY start").fetchall()


def fame(c, nm):
    """Campeon de cada temporada ya terminada (mejor puntaje entre su inicio y el de la siguiente)."""
    out, ss = [], seasons(c)
    for cur, nxt in zip(ss, ss[1:]):
        r = c.execute("""SELECT visitor, MAX(score) AS score FROM games WHERE ts >= ? AND ts < ?
                         GROUP BY visitor ORDER BY score DESC, MIN(ts) ASC LIMIT 1""", (cur["start"], nxt["start"])).fetchone()
        if r:
            out.append({"season": cur["name"], "n": shown(r["visitor"], nm), "s": r["score"]})
    return out


# ---------------------------------------------------------------- apodos

NAME_OK = re.compile(r"^[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ ._-]{2,12}$")
# Palabras largas: se rechazan aunque vengan pegadas a otras. Cortas: solo como palabra o inicio de palabra
# (para no rechazar nombres normales como "Penélope" o "Cómputo").
BAD_ANY = ["mierda", "marica", "malparid", "gonorrea", "hijueput", "pendej", "cabron", "zorra", "perra",
           "fuck", "shit", "bitch", "nigg", "hitler", "nazi", "porno", "violad", "estupid", "imbecil", "idiota"]
BAD_WORD = ["puta", "puto", "culo", "pene", "verga", "sexo", "hp", "ano", "teta"]
LEET = str.maketrans("013457@$", "oieastas")


def flat(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return s.translate(LEET)


def clean_name(n):
    """Devuelve el apodo limpio, "" si queda anonimo, o None si no se permite."""
    n = re.sub(r"\s+", " ", str(n or "")).strip()
    if not n:
        return ""
    if not NAME_OK.match(n):
        return None
    f = flat(n)
    joined = re.sub(r"[^a-z]", "", f)
    words = re.findall(r"[a-z]+", f)
    if any(b in joined for b in BAD_ANY):
        return None
    # corta: palabra exacta, o inicio de palabra si tiene 4+ letras ("putaa" no, "Penelope" si)
    if any(w == b or (len(b) >= 4 and w.startswith(b) and w not in ALLOWED) for w in words for b in BAD_WORD):
        return None
    return n


ALLOWED = {"penelope", "vergara"}  # nombres normales que empiezan como una palabra fea


def save_name(c, v, n):
    c.execute("""INSERT INTO players (visitor, name, ts) VALUES (?,?,?)
                 ON CONFLICT(visitor) DO UPDATE SET name=excluded.name, ts=excluded.ts""", (v, n or None, now()))


def names(c, admin=False):
    q = "SELECT visitor, name, hidden FROM players WHERE name IS NOT NULL" + ("" if admin else " AND hidden = 0")
    return {r["visitor"]: r["name"] for r in c.execute(q)}


def shown(v, nm):
    return nm.get(v) or "Anónimo " + v[:4]


def week_start():
    d = datetime.now(TZ)
    monday = (d - timedelta(days=d.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return int(monday.timestamp())


def board(me):
    """Tabla publica: mejor puntaje de cada persona (una linea por persona), semana y temporada actual."""
    with db() as c:
        nm = names(c)
        season = seasons(c)[-1]
        agg = {r["visitor"]: r for r in c.execute(
            """SELECT visitor, COUNT(*) AS games, MAX(rank) AS top, SUM(dist) AS dist FROM games
               WHERE ts >= ? GROUP BY visitor""", (season["start"],))}

        def best(since):
            # en SQLite, con MAX() las demas columnas salen de la fila del maximo
            return c.execute("""SELECT visitor, MAX(score) AS score, tickets, rank, MIN(ts) AS first FROM games
                                WHERE ts >= ? GROUP BY visitor ORDER BY score DESC, first ASC""", (since,)).fetchall()

        # Una línea por apodo: si alguien jugó desde dos navegadores (o desde el dominio viejo y el nuevo)
        # con el mismo apodo, se cuenta como una sola persona con su mejor puntaje.
        def who(v):
            return nm[v].strip().lower() if nm.get(v) else v
        grupo = {}
        for v in agg:
            grupo.setdefault(who(v), []).append(v)

        def stat(k, campo, f):
            return f(agg[v][campo] or 0 for v in grupo[k])

        out = {}
        for key, rows in (("week", best(max(week_start(), season["start"]))), ("all", best(season["start"]))):
            vistos, uno = set(), []
            for r in rows:  # ya vienen del mejor al peor: la primera de cada persona es su mejor
                if who(r["visitor"]) not in vistos:
                    vistos.add(who(r["visitor"])); uno.append(r)
            mios = set(grupo.get(who(me), [me]))
            out[key] = [{"n": shown(r["visitor"], nm), "s": r["score"], "t": r["tickets"], "r": r["rank"],
                         "g": stat(who(r["visitor"]), "games", sum), "top": stat(who(r["visitor"]), "top", max),
                         "d": stat(who(r["visitor"]), "dist", sum), "me": r["visitor"] in mios} for r in uno[:10]]
            pos = next((i for i, r in enumerate(uno, 1) if r["visitor"] in mios), 0)
            out[key + "Me"] = {"pos": pos, "of": len(uno), "best": uno[pos - 1]["score"] if pos else 0}
        out["name"] = nm.get(me, "")
        out["season"] = season["name"]
        out["fame"] = fame(c, nm)
        return out


def merge(c, new, old):
    """Une la ficha del navegador nuevo (`new`) con la de antes (`old`): pasa sus visitas y partidas a `old`.
    Solo quien tiene los dos ids (el de antes vive en el navegador de la persona, nunca se publica) puede unirlos."""
    if new == old or not c.execute("SELECT 1 FROM visits WHERE visitor = ? LIMIT 1", (old,)).fetchone():
        return False
    for t in ("visits", "starts", "games"):
        c.execute("UPDATE %s SET visitor = ? WHERE visitor = ?" % t, (old, new))
    nuevo = c.execute("SELECT name FROM players WHERE visitor = ?", (new,)).fetchone()
    if nuevo and nuevo["name"]:  # el apodo más reciente gana
        save_name(c, old, nuevo["name"])
    c.execute("DELETE FROM players WHERE visitor = ?", (new,))
    return True


def now():
    return int(datetime.now(timezone.utc).timestamp())


def num(d, k, hi):
    try:
        return max(0, min(hi, int(d.get(k, 0))))
    except (TypeError, ValueError):
        return 0


class Handler(BaseHTTPRequestHandler):
    server_version = "TicketRushStats"

    def log_message(self, *a):  # sin logs por peticion (no guardar IPs en el journal)
        pass

    def send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, code, obj):
        self.send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_POST(self):
        if self.path.split("?")[0].rstrip("/") == "/stats/hide":
            return self.hide()
        if self.path.split("?")[0].rstrip("/") == "/stats/season":
            return self.new_season()
        kind = self.path.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
        if not self.path.startswith("/api/") or kind not in ("visit", "start", "end", "name", "merge"):
            return self.send(404)
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > 2048:
            return self.send(400)
        try:
            d = json.loads(self.rfile.read(n))
        except ValueError:
            return self.send(400)
        if not isinstance(d, dict) or not VID.match(str(d.get("v", ""))):
            return self.send(400)
        v = d["v"]
        if kind == "merge":
            old = str(d.get("old", ""))
            if not VID.match(old):
                return self.send(400)
            with db() as c:
                return self.send_json(200, {"ok": merge(c, v, old)})
        if kind == "name":
            n = clean_name(d.get("n"))
            if n is None:
                return self.send_json(422, {"ok": False})
            with db() as c:
                save_name(c, v, n)
            return self.send_json(200, {"ok": True, "name": n})
        with db() as c:
            if kind == "visit":
                c.execute("INSERT INTO visits VALUES (?,?,?)", (now(), v, 1 if d.get("m") else 0))
            elif kind == "start":
                c.execute("INSERT INTO starts VALUES (?,?)", (now(), v))
            else:
                secs = num(d, "secs", 86400)
                # topes: nadie resuelve mas de un ticket cada 2 s, ni saca mas de 80 pts por ticket (servidor x combo)
                tickets = min(num(d, "tickets", 2000), secs // 2 + 3)
                score = min(num(d, "score", 10**6), tickets * 80)
                if "n" in d and clean_name(d["n"]) is not None:
                    save_name(c, v, clean_name(d["n"]))
                g = str(d.get("g", ""))
                row = (now(), v, score, tickets, num(d, "rank", 2), secs, str(d.get("why", ""))[:140],
                       g if VID.match(g) else None, 1 if d.get("a") else 0, num(d, "dist", 500))
                # Cada partida tiene su id: si llega "abandonó" (salió de la página) y después vuelve y
                # termina, el final real reemplaza al abandono; un abandono nunca pisa un final real.
                c.execute("""INSERT INTO games (ts, visitor, score, tickets, rank, secs, why, gid, abandoned, dist)
                             VALUES (?,?,?,?,?,?,?,?,?,?)
                             ON CONFLICT(gid) DO UPDATE SET ts=excluded.ts, score=excluded.score,
                               tickets=excluded.tickets, rank=excluded.rank, secs=excluded.secs,
                               why=excluded.why, abandoned=excluded.abandoned, dist=excluded.dist
                             WHERE excluded.abandoned = 0 OR games.abandoned = 1""", row)
        self.send(204)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path.rstrip("/") == "/api/board":
            me = (parse_qs(urlparse(self.path).query).get("v") or [""])[0]
            return self.send_json(200, board(me if VID.match(me) else ""))
        if path.rstrip("/") == "/stats":
            return self.send(200, stats_page().encode("utf-8"), "text/html; charset=utf-8")
        if STATIC:
            name = "ticket_rush.html" if path == "/" else path.lstrip("/")
            root = os.path.abspath(STATIC)
            f = os.path.abspath(os.path.join(root, name))
            if f.startswith(root) and os.path.isfile(f):
                with open(f, "rb") as fh:
                    ctype = mimetypes.guess_type(f)[0] or "application/octet-stream"
                    if ctype.startswith("text/"):
                        ctype += "; charset=utf-8"
                    return self.send(200, fh.read(), ctype)
        self.send(404)

    def hide(self):
        n = int(self.headers.get("Content-Length") or 0)
        f = parse_qs(self.rfile.read(min(n, 512)).decode("utf-8", "ignore")) if n > 0 else {}
        v = (f.get("v") or [""])[0]
        if VID.match(v):
            with db() as c:
                c.execute("UPDATE players SET hidden = ? WHERE visitor = ?",
                          (1 if (f.get("h") or ["0"])[0] == "1" else 0, v))
        self.send_response(303)
        self.send_header("Location", "/stats")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def new_season(self):
        n = int(self.headers.get("Content-Length") or 0)
        f = parse_qs(self.rfile.read(min(n, 512)).decode("utf-8", "ignore")) if n > 0 else {}
        name = re.sub(r"\s+", " ", (f.get("name") or [""])[0]).strip()[:40]
        with db() as c:
            if not name:
                name = "Temporada %d" % (len(seasons(c)) + 1)
            c.execute("INSERT INTO seasons (start, name) VALUES (?, ?)", (now(), name))
        self.send_response(303)
        self.send_header("Location", "/stats")
        self.send_header("Content-Length", "0")
        self.end_headers()


# ---------------------------------------------------------------- pagina de estadisticas

def day(ts):
    return datetime.fromtimestamp(ts, TZ)


def mins(secs):
    h, m = divmod(round(secs / 60), 60)
    return f"{h} h {m} min" if h else f"{m} min"


def stats_page():
    with db() as c:
        q = lambda sql, *a: c.execute(sql, a).fetchone()[0] or 0
        today = int(datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        visits, uniq = q("SELECT COUNT(*) FROM visits"), q("SELECT COUNT(DISTINCT visitor) FROM visits")
        v_today = q("SELECT COUNT(*) FROM visits WHERE ts >= ?", today)
        u_today = q("SELECT COUNT(DISTINCT visitor) FROM visits WHERE ts >= ?", today)
        mobile = q("SELECT COUNT(*) FROM visits WHERE mobile = 1")
        starts, ends = q("SELECT COUNT(*) FROM starts"), q("SELECT COUNT(*) FROM games")
        g_today = q("SELECT COUNT(*) FROM starts WHERE ts >= ?", today)
        players = q("SELECT COUNT(DISTINCT visitor) FROM starts")
        best, avg = q("SELECT MAX(score) FROM games"), q("SELECT AVG(score) FROM games WHERE abandoned = 0")
        max_t, played = q("SELECT MAX(tickets) FROM games"), q("SELECT SUM(secs) FROM games")
        boss = q("SELECT COUNT(*) FROM games WHERE abandoned = 0 AND why LIKE '%jefe%'")
        quit_ = q("SELECT COUNT(*) FROM games WHERE abandoned = 1")
        sla = ends - boss - quit_
        no_play = q("SELECT COUNT(DISTINCT visitor) FROM visits WHERE visitor NOT IN (SELECT visitor FROM starts)")
        lost = max(0, starts - ends)  # empezaron pero no llegó ni final ni abandono
        top = c.execute("SELECT * FROM games ORDER BY score DESC, ts ASC LIMIT 10").fetchall()
        season = seasons(c)[-1]
        champs = fame(c, names(c, admin=True))
        next_name = "Temporada %d" % (len(seasons(c)) + 1)
        nm = names(c, admin=True)
        hidden = {r[0] for r in c.execute("SELECT visitor FROM players WHERE hidden = 1")}
        people = c.execute("""SELECT visitor, COUNT(*) AS games, MAX(score) AS best, MAX(rank) AS top,
                                     SUM(dist) AS dist, MAX(ts) AS last
                              FROM games GROUP BY visitor ORDER BY best DESC""").fetchall()
        ranks = dict(c.execute("SELECT rank, COUNT(*) FROM games GROUP BY rank").fetchall())
        since = today - 13 * 86400
        per_v = dict(c.execute("SELECT (ts - ?) / 86400, COUNT(*) FROM visits WHERE ts >= ? GROUP BY 1",
                               (since, since)).fetchall())
        per_g = dict(c.execute("SELECT (ts - ?) / 86400, COUNT(*) FROM starts WHERE ts >= ? GROUP BY 1",
                               (since, since)).fetchall())

    def tile(label, value, sub=""):
        return f'<div class="tile"><span>{label}</span><b>{value}</b><small>{sub}</small></div>'

    tiles = "".join([
        tile("Visitas", visits, f"{v_today} hoy"),
        tile("Personas distintas", uniq, f"{u_today} hoy"),
        tile("Desde celular", f"{round(100 * mobile / visits) if visits else 0}%", f"{mobile} visitas"),
        tile("Partidas jugadas", starts, f"{g_today} hoy · {players} jugadores"),
        tile("Récord", best, f"máx. {max_t} tickets"),
        tile("Entraron sin jugar", no_play, f"de {uniq} personas"),
        tile("Puntaje promedio", round(avg), f"{ends - quit_} partidas terminadas"),
        tile("Tiempo jugado", mins(played), "entre todos"),
        tile("Perdieron por…", f"{boss} jefe", f"{sla} SLA vencido · {quit_} abandonaron"
             + (f" · {lost} sin dato" if lost else "")),
    ])

    rows = "".join(
        f"<tr><td>{i}</td><td>{html.escape(shown(g['visitor'], nm))}{' <em>(abandonó)</em>' if g['abandoned'] else ''}</td>"
        f"<td class=n>{g['score']}</td>"
        f"<td class=n>{g['tickets']}</td><td>{RANKS[g['rank']]}</td>"
        f"<td>{day(g['ts']).strftime('%d/%m %H:%M')}</td></tr>"
        for i, g in enumerate(top, 1)) or '<tr><td colspan=6 class=empty>Todavía nadie ha terminado una partida.</td></tr>'

    def hide_btn(v):
        h = v in hidden
        return (f'<form method=post action="/stats/hide"><input type=hidden name=v value="{v}">'
                f'<input type=hidden name=h value="{0 if h else 1}"><button>{"Mostrar" if h else "Ocultar"}</button></form>')

    people_rows = "".join(
        f"<tr><td>{html.escape(nm.get(p['visitor']) or '—')}{' <em>(oculto)</em>' if p['visitor'] in hidden else ''}"
        f"<br><small>{p['visitor'][:4]}</small></td><td class=n>{p['games']}</td><td class=n>{p['best']}</td>"
        f"<td>{RANKS[p['top']]}</td><td class=n>{p['dist'] or 0}</td><td>{day(p['last']).strftime('%d/%m')}</td>"
        f"<td>{hide_btn(p['visitor']) if nm.get(p['visitor']) else ''}</td></tr>"
        for p in people) or '<tr><td colspan=7 class=empty>Todavía no hay jugadores.</td></tr>'

    total_r = sum(ranks.values()) or 1
    rank_bars = "".join(
        f'<div class="hrow"><span>{name}</span><div class="track"><i style="width:{100 * ranks.get(i, 0) / total_r:.0f}%"></i></div>'
        f'<b>{ranks.get(i, 0)}</b></div>' for i, name in enumerate(RANKS))

    top_day = max([1] + list(per_v.values()) + list(per_g.values()))
    days = "".join(
        f'<div class="day"><div class="bars"><i class="v" style="height:{100 * per_v.get(i, 0) / top_day:.0f}%" '
        f'title="{per_v.get(i, 0)} visitas"></i><i class="g" style="height:{100 * per_g.get(i, 0) / top_day:.0f}%" '
        f'title="{per_g.get(i, 0)} partidas"></i></div><small>{day(since + i * 86400).strftime("%d")}</small></div>'
        for i in range(14))

    return f"""<!doctype html>
<html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ticket Rush · Estadísticas</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap">
<style>
:root {{ --bg:#0d0c14; --panel:#171525; --line:#2c2840; --fg:#ece8f7; --muted:#9d96b8; --accent:#a285f5; --warn:#f2b441; --good:#5fd6a1; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:20px/1.25 VT323, ui-monospace, monospace; padding:20px 16px 40px; }}
main {{ max-width:900px; margin:0 auto; display:grid; grid-template-columns:minmax(0,1fr); gap:18px; }}
h1 {{ font:400 clamp(14px,3.6vw,22px) "Press Start 2P", monospace; color:var(--accent); margin:0; }}
h2 {{ font:400 11px "Press Start 2P", monospace; color:var(--warn); margin:0 0 12px; }}
.sub {{ color:var(--muted); }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(150px,100%),1fr)); gap:10px; }}
td small {{ color:var(--muted); font-size:14px; }}
form {{ margin:0; }}
button {{ font:16px VT323, monospace; color:var(--fg); background:#221f33; border:1px solid var(--line); padding:2px 8px; cursor:pointer; }}
button:hover {{ border-color:var(--accent); }}
section p {{ margin:0 0 8px; }}
input {{ font:16px VT323, monospace; color:var(--fg); background:#0d0c14; border:1px solid var(--line); padding:2px 6px; }}
.tile, section {{ background:var(--panel); border:2px solid var(--line); padding:12px 14px; }}
.tile {{ display:grid; gap:2px; }}
.tile span, .tile small {{ color:var(--muted); }}
.tile b {{ font:400 20px "Press Start 2P", monospace; color:var(--fg); margin:6px 0 4px; }}
table {{ width:100%; border-collapse:collapse; }}
th, td {{ text-align:left; padding:5px 6px; border-bottom:1px solid var(--line); }}
th {{ color:var(--muted); font-weight:400; }}
td.n {{ text-align:right; font-variant-numeric:tabular-nums; }}
tr:first-child td {{ color:var(--warn); }}
.empty {{ color:var(--muted); text-align:center; }}
em {{ color:var(--muted); font-style:normal; }}
.wrap {{ overflow-x:auto; }}
.hrow {{ display:grid; grid-template-columns:120px 1fr 48px; gap:10px; align-items:center; margin:6px 0; }}
.hrow b {{ text-align:right; font-weight:400; }}
.track {{ height:14px; background:#221f33; }}
.track i {{ display:block; height:100%; background:var(--accent); }}
.days {{ display:grid; grid-template-columns:repeat(14,minmax(0,1fr)); gap:4px; align-items:end; }}
.day {{ display:grid; gap:4px; text-align:center; }}
.day small {{ color:var(--muted); font-size:14px; }}
.bars {{ height:110px; display:flex; gap:2px; align-items:flex-end; justify-content:center; }}
.bars i {{ width:40%; min-height:2px; }}
.v {{ background:var(--accent); }} .g {{ background:var(--good); }}
.legend {{ color:var(--muted); margin-top:8px; }} .legend b {{ font-weight:400; }}
</style>
<main>
  <header><h1>TICKET RUSH · STATS</h1><div class="sub">Actualizado {datetime.now(TZ).strftime('%d/%m/%Y %H:%M')} (hora Colombia)</div></header>
  <div class="tiles">{tiles}</div>
  <section><h2>TOP 10 PUNTAJES</h2><div class="wrap"><table>
    <tr><th>#</th><th>Quién</th><th class=n>Puntos</th><th class=n>Tickets</th><th>Rango</th><th>Cuándo</th></tr>
    {rows}</table></div></section>
  <section><h2>TEMPORADAS</h2>
    <p>Temporada actual: <b>{html.escape(season["name"])}</b>{" (desde " + day(season["start"]).strftime("%d/%m/%Y %H:%M") + ")" if season["start"] else ""}.
    La tabla de líderes del juego solo cuenta desde ahí; esta página muestra todo.</p>
    {"".join(f"<p>🏆 {html.escape(f['season'])}: <b>{html.escape(f['n'])}</b> · {f['s']} pts</p>" for f in champs) or "<p class=legend>Todavía no hay temporadas terminadas.</p>"}
    <form method=post action="/stats/season" onsubmit="return confirm('¿Empezar una temporada nueva? La tabla del juego arranca de cero (no se borra nada).')">
      <input name=name value="{next_name}" maxlength=40 aria-label="Nombre de la temporada nueva"> <button>Empezar temporada nueva</button>
    </form></section>
  <section><h2>JUGADORES</h2><div class="wrap"><table>
    <tr><th>Apodo</th><th class=n>Partidas</th><th class=n>Mejor</th><th>Rango máx.</th><th class=n>♥ Distrajo</th><th>Última</th><th></th></tr>
    {people_rows}</table></div>
    <div class="legend">"Ocultar" quita el apodo de la tabla pública del juego (sale como Anónimo).</div></section>
  <section><h2>HASTA DÓNDE LLEGAN</h2>{rank_bars}</section>
  <section><h2>ÚLTIMOS 14 DÍAS</h2><div class="days">{days}</div>
    <div class="legend"><b style="color:var(--accent)">■</b> visitas · <b style="color:var(--good)">■</b> partidas</div></section>
</main></html>"""


if __name__ == "__main__":
    init()
    print(f"Ticket Rush stats en 127.0.0.1:{PORT} (base {DB})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
