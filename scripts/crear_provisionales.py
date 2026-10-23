"""Muñequitos PROVISIONALES (en gris, para que se note que no son los definitivos) para probar
personajes nuevos mientras llegan los dibujos de Manuel.
Uso (desde la carpeta scripts, después de preparar_chibi.py):  python crear_provisionales.py

- Pasante del SENA: el jefe rejuvenecido (pelo oscuro en vez de calva y canas), en gris. La gorra se dibuja en el juego.

- PENDIENTES_GRIS: personajes que ya tienen hoja (de preparar_chibi.py) pero cuya figura no es la final;
  se dejan en gris para que se note. Cuando Manuel apruebe la figura final, se quita de la lista.

Cuando Manuel mande la hoja del pasante (arte/chibi/pasante.png), se agregan a NOMBRES
en preparar_chibi.py y este script ya no hace falta.
"""
import colorsys
from PIL import Image

SP = "../sprites/"


def recolor_pelo(nombre, fn):
    im = Image.open(SP + "chibi_" + nombre + ".png").convert("RGBA")
    im.save(SP + "_tmp_base.png")
    con_pelo(im).save(SP + "_tmp_base.png")
    out = recolor("_tmp_base", fn, prefijo="")
    import os; os.remove(SP + "_tmp_base.png")
    return out


def recolor(nombre, fn, prefijo="chibi_"):
    im = Image.open(SP + prefijo + nombre + ".png").convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            nuevo = fn(h, s, v)
            if nuevo:
                px[x, y] = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(*nuevo)) + (a,)
    return im


def gris(v, s):
    return (0, 0, v)


def pasante(h, s, v):
    if s < 0.32 and 0.3 < v < 0.75:                    # canas del jefe -> pelo oscuro (joven)
        return (0, 0, 0.22)
    return gris(min(1, v * 1.05), s)


def con_pelo(tira):
    """El jefe es calvo: le pinta pelo oscuro en la parte de arriba de la cabeza para que se vea joven."""
    px = tira.load()
    for f in range(tira.width // 56):
        x0 = f * 56
        filas = [y for y in range(56) if any(px[x0 + x, y][3] for x in range(56))]
        if not filas:
            continue
        top = filas[0]
        for y in range(top, top + 12):
            for x in range(x0, x0 + 56):
                r, g, b, a = px[x, y]
                if a and r > 180 and g > 140:          # piel de la calva
                    px[x, y] = (40, 30, 26, a)
    return tira


for nombre, base, fn in (("pasante", "jefe", pasante),):
    tira = recolor(base, fn) if nombre != "pasante" else recolor_pelo(base, fn)
    tira.save(SP + "chibi_" + nombre + ".png", optimize=True)
    frente = tira.crop((8 * 56, 0, 9 * 56, 56))
    frente.crop(frente.getbbox()).save(SP + "chibi_" + nombre + "_frente.png", optimize=True)
    print("ok", nombre)


# Figura aún no definitiva: en gris (el pelo y la ropa se distinguen por el brillo).
PENDIENTES_GRIS = ["aseo", "sapo"]
for nombre in PENDIENTES_GRIS:
    for sufijo in ("", "_frente"):
        ruta = SP + "chibi_" + nombre + sufijo + ".png"
        im = Image.open(ruta).convert("RGBA")
        g = im.convert("L").convert("RGBA"); g.putalpha(im.getchannel("A"))
        g.save(ruta, optimize=True)
    print("gris", nombre)
