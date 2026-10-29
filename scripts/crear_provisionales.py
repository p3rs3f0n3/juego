"""Muñequitos PROVISIONALES para probar personajes nuevos mientras llegan los dibujos de Manuel.
Uso (desde la carpeta scripts, después de preparar_chibi.py):  python crear_provisionales.py

- Pasante del SENA: el jefe rejuvenecido (pelo oscuro en vez de calva y canas), con camiseta verde, jean y cara alegre.
  La gorra (verde) se dibuja en el juego.

- PENDIENTES_GRIS: personajes que ya tienen hoja (de preparar_chibi.py) pero que se quieren dejar en gris
  para que se note que no son la figura final. Desde el 29 oct 2026 van a color (vacía).

Cuando Manuel mande la hoja del pasante (arte/chibi/pasante.png), se agregan a NOMBRES
en preparar_chibi.py y este script ya no hace falta.
"""
import colorsys
from collections import Counter
from PIL import Image

SP = "../sprites/"


def recolor_pelo(nombre, fn):
    im = Image.open(SP + "chibi_" + nombre + ".png").convert("RGBA")
    im.save(SP + "_tmp_base.png")
    con_pelo(im).save(SP + "_tmp_base.png")
    out = recolor("_tmp_base", fn, prefijo="", por_cuadro=True)
    import os; os.remove(SP + "_tmp_base.png")
    return out


def recolor(nombre, fn, prefijo="chibi_", por_cuadro=False):
    im = Image.open(SP + prefijo + nombre + ".png").convert("RGBA")
    px = im.load()
    pies = None
    if por_cuadro:                                     # fila de los pies de cada cuadro de 56 px
        pies = {}
        for f in range(im.width // 56):
            filas = [y for y in range(im.height) if any(px[f * 56 + x, y][3] for x in range(56))]
            pies[f] = filas[-1] + 1 if filas else im.height
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            nuevo = fn(h, s, v, y, pies.get(x // 56, im.height)) if pies is not None else fn(h, s, v)
            if nuevo:
                px[x, y] = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(*nuevo)) + (a,)
    return im


def gris(v, s):
    return (0, 0, v)


def pasante(h, s, v, y=0, pie=56):
    if y < pie - 16:                                   # cabeza: canas del jefe -> pelo oscuro (joven)
        if s < 0.32 and 0.3 < v < 0.75:
            return (0.06, 0.35, 0.18)
        return None
    piel = 0.02 <= h <= 0.1 and s > 0.25 and v > 0.6
    if piel or v < 0.1:                                # manos y contorno se quedan
        return None
    if y >= pie - 5:                                   # piernas: jean
        return (0.6, 0.55, min(1, 0.35 + v * 0.8))
    return (0.33, 0.62, min(1, 0.38 + v * 0.75))      # vestido del jefe -> camiseta verde SENA


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


def piel(p):
    r, g, b, a = p
    return a and r > 200 and g > 140 and b > 100


def oscuro(p):
    return p[3] and max(p[:3]) < 40


def grupos(cols):
    g = []
    for c in cols:
        if g and c - g[-1][-1] <= 1:
            g[-1].append(c)
        else:
            g.append([c])
    return g


def cara_alegre(tira):
    """El pasante es joven y alegre (como Dani): borra las cejas de mal genio y la boca seria del jefe,
    pinta cejas arqueadas y una sonrisa. Los cuadros 9-11 (puños y vapor de rabia) pasan a ser el quieto."""
    px = tira.load(); TINTA = (24, 18, 18, 255)
    for f in range(9):
        x0 = f * 56
        top = min(y for y in range(56) if any(piel(px[x0 + x, y]) for x in range(56)))
        tono = Counter(px[x0 + x, y] for y in range(top, top + 14) for x in range(56) if piel(px[x0 + x, y])).most_common(1)[0][0]
        sp = {}
        for y in range(top, top + 16):
            fila = [x for x in range(56) if piel(px[x0 + x, y])]
            sp[y] = (fila[0], fila[-1]) if fila else None
        ojos = [g for g in grupos(sorted({x for y in range(top + 7, top + 10) for x in range(56)
                if oscuro(px[x0 + x, y]) and sp[y] and sp[y][0] + 2 < x < sp[y][1] - 2})) if len(g) <= 3]
        ojo_top = min(y for y in range(top, top + 10) for g in ojos for x in g
                      if all(oscuro(px[x0 + x, yy]) for yy in range(y, top + 9)))

        def borrar(y0, y1):
            for y in range(y0, y1):
                if sp[y]:
                    for x in range(sp[y][0] + 1, sp[y][1]):
                        if not piel(px[x0 + x, y]):
                            px[x0 + x, y] = tono
        borrar(top, ojo_top)                           # cejas de mal genio
        borrar(top + 11, top + 15)                     # boca seria
        for g in ojos:                                 # cejas arqueadas, más arriba
            c = g[len(g) // 2]
            for dx, dy in ((-1, 0), (0, -1), (1, 0)):
                px[x0 + c + dx, ojo_top - 3 + dy] = TINTA
        c = (ojos[0][0] + ojos[-1][-1]) // 2 if f >= 8 else ojos[0][0] + 4   # 0-7 de perfil, 8 de frente
        for dx, dy in ((-2, 0), (2, 0), (-1, 1), (0, 1), (1, 1)):          # sonrisa
            px[x0 + c + dx, top + 12 + dy] = TINTA
    for f in (9, 10, 11):
        tira.paste(tira.crop((8 * 56, 0, 9 * 56, 56)), (f * 56, 0))
    return tira


for nombre, base, fn in (("pasante", "jefe", pasante),):
    tira = recolor(base, fn) if nombre != "pasante" else cara_alegre(recolor_pelo(base, fn))
    tira.save(SP + "chibi_" + nombre + ".png", optimize=True)
    frente = tira.crop((8 * 56, 0, 9 * 56, 56))
    frente.crop(frente.getbbox()).save(SP + "chibi_" + nombre + "_frente.png", optimize=True)
    print("ok", nombre)


# Figura aún no definitiva: en gris (el pelo y la ropa se distinguen por el brillo).
PENDIENTES_GRIS = []
for nombre in PENDIENTES_GRIS:
    for sufijo in ("", "_frente"):
        ruta = SP + "chibi_" + nombre + sufijo + ".png"
        im = Image.open(ruta).convert("RGBA")
        g = im.convert("L").convert("RGBA"); g.putalpha(im.getchannel("A"))
        g.save(ruta, optimize=True)
    print("gris", nombre)
