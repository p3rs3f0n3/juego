"""Une el juego (src/game_template.html) con los sprites y genera ticket_rush.html.
Uso (desde la carpeta scripts):  python construir_juego.py
"""
import base64
import json
from pathlib import Path
from sprite_config import validate_config

ROOT = Path(__file__).resolve().parent.parent

def uri(ruta):
    with open(Path(__file__).resolve().parent / ruta, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

with open(ROOT / "src/game_template.html", encoding="utf-8") as f:
    html = f.read()

config = json.loads((ROOT / "src/sprites.config.json").read_text())
validate_config(config, ROOT)
variants = list(config["assets"].values()) + [a["halloween"] for a in config["assets"].values() if a.get("halloween")]
files = {a["file"]: uri(str(ROOT / a["file"])) for a in variants}
html = html.replace("__SPRITE_SEASONAL__", (ROOT / "src/sprite-seasonal.js").read_text())
html = html.replace("__SPRITE_RUNTIME__", (ROOT / "src/sprite-runtime.js").read_text())
html = html.replace("__SPRITE_CONFIG__", json.dumps(config, ensure_ascii=True).replace("<", "\\u003c"))
html = html.replace("__SPRITE_FILES__", json.dumps(files))
html = html.replace("__OFFICE__", uri("../sprites/oficina.png"))
html = html.replace("__LOGO__", uri("../sprites/ticket-rush-logo.png"))
html = html.replace("__PLAYER__", uri("../sprites/avatar_48.png"))
html = html.replace("__BOSS__", uri("../sprites/boss_48.png"))
html = html.replace("__MATE__", uri("../sprites/companera_48.png"))
html = html.replace("__GERENTE__", uri("../sprites/gerente_48.png"))
for nombre in ("jugadora", "jugadora_arreglando", "jefe", "gerente", "dani", "aseo", "sapo", "pasante"):
    html = html.replace("__CHIBI_%s__" % nombre.upper(), uri("../sprites/chibi_%s.png" % nombre))
html = html.replace("__JEFE_FRENTE__", uri("../sprites/chibi_jefe_frente.png"))
html = html.replace("__DANI_FRENTE__", uri("../sprites/chibi_dani_frente.png"))
for nombre in ("aseo", "sapo", "pasante"):
    html = html.replace("__%s_FRENTE__" % nombre.upper(), uri("../sprites/chibi_%s_frente.png" % nombre))

with open(ROOT / "ticket_rush.html.tmp", "w", encoding="utf-8") as f:
    f.write(html)
(ROOT / "ticket_rush.html.tmp").replace(ROOT / "ticket_rush.html")
print("Listo: ticket_rush.html generado")



