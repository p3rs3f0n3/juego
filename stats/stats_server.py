#!/usr/bin/env python3
"""Contador de visitas y estadisticas de Ticket Rush.

Solo usa la libreria estandar de Python (sin pip). Guarda todo en SQLite.
No guarda IPs ni nombres: cada navegador manda un identificador al azar.

  POST /api/visit   {"v": id, "m": 1|0}                 se abrio el juego (m = celular)
  POST /api/start   {"v": id}                           empezo una partida
  POST /api/end     {"v": id, "score", "tickets",       termino una partida
                     "rank", "secs", "why"}
  GET  /stats       pagina de estadisticas (Caddy la protege con usuario y clave)

Variables de entorno: STATS_DB (ruta de la base), STATS_PORT (por defecto 8095),
STATS_STATIC (solo para probar en local: carpeta desde donde servir el juego).
"""
import html
import json
import os
import re
import sqlite3
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

    def do_POST(self):
        kind = self.path.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
        if not self.path.startswith("/api/") or kind not in ("visit", "start", "end"):
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
        with db() as c:
            if kind == "visit":
                c.execute("INSERT INTO visits VALUES (?,?,?)", (now(), v, 1 if d.get("m") else 0))
            elif kind == "start":
                c.execute("INSERT INTO starts VALUES (?,?)", (now(), v))
            else:
                tickets = num(d, "tickets", 2000)
                score = min(num(d, "score", 10**6), tickets * 100)  # 100 pts por ticket es imposible de superar
                c.execute("INSERT INTO games VALUES (?,?,?,?,?,?,?)",
                          (now(), v, score, tickets, num(d, "rank", 2), num(d, "secs", 86400),
                           str(d.get("why", ""))[:140]))
        self.send(204)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path.rstrip("/") == "/stats":
            return self.send(200, stats_page().encode("utf-8"), "text/html; charset=utf-8")
        if STATIC:
            name = "ticket_rush.html" if path == "/" else path.lstrip("/")
            f = os.path.normpath(os.path.join(STATIC, name))
            if f.startswith(os.path.normpath(STATIC)) and os.path.isfile(f):
                with open(f, "rb") as fh:
                    return self.send(200, fh.read(), "text/html; charset=utf-8")
        self.send(404)


# ---------------------------------------------------------------- pagina de estadisticas

def day(ts):
    return datetime.fromtimestamp(ts, TZ)


def player(v):
    # "Jugador 3f2a": los 4 primeros caracteres del id al azar, suficiente para distinguirlos
    return "Jugador " + html.escape(v[:4])


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
        best, avg = q("SELECT MAX(score) FROM games"), q("SELECT AVG(score) FROM games")
        max_t, played = q("SELECT MAX(tickets) FROM games"), q("SELECT SUM(secs) FROM games")
        boss = q("SELECT COUNT(*) FROM games WHERE why LIKE '%jefe%'")
        top = c.execute("SELECT * FROM games ORDER BY score DESC, ts ASC LIMIT 10").fetchall()
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
        tile("Puntaje promedio", round(avg), f"{ends} partidas terminadas"),
        tile("Tiempo jugado", mins(played), "entre todos"),
        tile("Perdieron por…", f"{boss} jefe", f"{ends - boss} SLA vencido"),
    ])

    rows = "".join(
        f"<tr><td>{i}</td><td>{player(g['visitor'])}</td><td class=n>{g['score']}</td>"
        f"<td class=n>{g['tickets']}</td><td>{RANKS[g['rank']]}</td>"
        f"<td>{day(g['ts']).strftime('%d/%m %H:%M')}</td></tr>"
        for i, g in enumerate(top, 1)) or '<tr><td colspan=6 class=empty>Todavía nadie ha terminado una partida.</td></tr>'

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
.tiles {{ grid-template-columns:repeat(auto-fit,minmax(min(150px,100%),1fr)); }}
h1 {{ font:400 clamp(14px,3.6vw,22px) "Press Start 2P", monospace; color:var(--accent); margin:0; }}
h2 {{ font:400 11px "Press Start 2P", monospace; color:var(--warn); margin:0 0 12px; }}
.sub {{ color:var(--muted); }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:10px; }}
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
  <section><h2>HASTA DÓNDE LLEGAN</h2>{rank_bars}</section>
  <section><h2>ÚLTIMOS 14 DÍAS</h2><div class="days">{days}</div>
    <div class="legend"><b style="color:var(--accent)">■</b> visitas · <b style="color:var(--good)">■</b> partidas</div></section>
</main></html>"""


if __name__ == "__main__":
    init()
    print(f"Ticket Rush stats en 127.0.0.1:{PORT} (base {DB})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
