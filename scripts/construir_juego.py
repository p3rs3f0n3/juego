"""Une el juego (src/game_template.html) con los sprites y genera ticket_rush.html.
Uso (desde la carpeta scripts):  python construir_juego.py
"""
import base64

def uri(ruta):
    with open(ruta, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

with open("../src/game_template.html", encoding="utf-8") as f:
    html = f.read()

html = html.replace("__LOGO__", uri("../sprites/ticket-rush-logo.png"))
html = html.replace("__PLAYER__", uri("../sprites/avatar_48.png"))
html = html.replace("__BOSS__", uri("../sprites/boss_48.png"))
html = html.replace("__MATE__", uri("../sprites/companera_48.png"))
html = html.replace("__GERENTE__", uri("../sprites/gerente_48.png"))
for nombre in ("jugadora", "jugadora_arreglando", "jefe", "gerente", "dani"):
    html = html.replace("__CHIBI_%s__" % nombre.upper(), uri("../sprites/chibi_%s.png" % nombre))
html = html.replace("__JEFE_FRENTE__", uri("../sprites/chibi_jefe_frente.png"))
html = html.replace("__DANI_FRENTE__", uri("../sprites/chibi_dani_frente.png"))

with open("../ticket_rush.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Listo: ticket_rush.html generado")

