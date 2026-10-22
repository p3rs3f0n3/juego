"""Limpia los spritesheets chibi de Manuel (arte/chibi/*.png) y los deja listos para el juego.
Uso (desde la carpeta scripts):  python preparar_chibi.py

Cada hoja original tiene 4 columnas x 3 filas: caminar, correr y accion especial. Son imagenes
generadas con IA, asi que no son pixel art exacto: se limpian (bordes nitidos, sin transparencias
a medias, paleta reducida), se descartan pedacitos que se cuelan de la celda vecina, se alinean
los pies de cada fila y se reducen todas con la misma escala.

Salida: sprites/chibi_<nombre>.png, una tira de 12 cuadros de CELDA x CELDA px
(cuadros 0-3 caminar, 4-7 correr, 8-11 accion especial), con los pies en el borde de abajo.
El Gerente sale del jefe cambiando colores (traje vinotinto, corbata dorada, canas).
"""
import colorsys
from collections import deque
from PIL import Image

ARTE = "../arte/chibi/"
SP = "../sprites/"
CELDA = 56          # tamano de cada cuadro en el juego
ALTO = 50           # alto de la jugadora caminando (la mas alta); los demas, a la misma escala
COLORES = 20        # paleta por personaje
NOMBRES = ["jugadora", "jefe", "dani", "sapo"]


def mascara(cell):
    a = cell.getchannel("A")
    return [[a.getpixel((x, y)) >= 128 for x in range(cell.width)] for y in range(cell.height)]


def componentes(m):
    """Grupos de pixeles conectados: [(area, x0, y0, x1, y1, pixeles)]."""
    h, w = len(m), len(m[0])
    visto = [[False] * w for _ in range(h)]
    out = []
    for y in range(h):
        for x in range(w):
            if m[y][x] and not visto[y][x]:
                q, pix = deque([(x, y)]), []
                visto[y][x] = True
                while q:
                    cx, cy = q.popleft(); pix.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and m[ny][nx] and not visto[ny][nx]:
                            visto[ny][nx] = True; q.append((nx, ny))
                xs = [p[0] for p in pix]; ys = [p[1] for p in pix]
                out.append((len(pix), min(xs), min(ys), max(xs), max(ys), pix))
    return out


def limpiar_celda(cell):
    """Deja solo la figura y sus efectos (corazones, humo); quita lo que se cuela de la celda vecina."""
    comps = componentes(mascara(cell))
    if not comps:
        return cell, None
    grande = max(comps, key=lambda c: c[0])
    keep = Image.new("L", cell.size, 0)
    for area, x0, y0, x1, y1, pix in comps:
        pequeno = area < grande[0] * 0.05
        toca_lado = x0 == 0 or x1 == cell.width - 1
        # rayita plana pegada arriba o abajo: pies o cabeza de la fila vecina (los corazones no son planos)
        raya = (y0 == 0 or y1 == cell.height - 1) and (y1 - y0 + 1) <= 12
        if area == grande[0] or (area >= 30 and not (pequeno and (toca_lado or raya))):
            for p in pix:
                keep.putpixel(p, 255)
    limpio = Image.new("RGBA", cell.size, (0, 0, 0, 0))
    solido = cell.copy(); solido.putalpha(255)
    limpio.paste(solido, (0, 0), keep)
    return limpio, grande  # grande: la figura principal (para alinear los pies)


def hoja(nombre):
    im = Image.open(ARTE + nombre + ".png").convert("RGBA")
    cw, ch = im.width // 4, im.height // 3
    celdas, pies = [], []
    for fila in range(3):
        fila_celdas = []
        for col in range(4):
            c, grande = limpiar_celda(im.crop((col * cw, fila * ch, (col + 1) * cw, (fila + 1) * ch)))
            fila_celdas.append(c)
            pies.append(grande[4] if grande else ch - 1)
        celdas.append(fila_celdas)
    return celdas, pies, cw, ch


def construir():
    hojas = {n: hoja(n) for n in NOMBRES}
    # escala comun: la jugadora caminando mide ALTO px
    cel, pies, cw, ch = hojas["jugadora"]
    caja = cel[0][0].getbbox()
    k = ALTO / (pies[0] - caja[1] + 1)
    for nombre, (celdas, pies, cw, ch) in hojas.items():
        tira = Image.new("RGBA", (CELDA * 12, CELDA), (0, 0, 0, 0))
        for fila in range(3):
            base = max(pies[fila * 4:fila * 4 + 4])  # pies de la fila: todos apoyados a la misma altura
            for col in range(4):
                c = celdas[fila][col]
                peq = c.resize((max(1, round(cw * k)), max(1, round(ch * k))), Image.LANCZOS)
                a = peq.getchannel("A").point(lambda v: 255 if v >= 110 else 0)
                peq.putalpha(a)
                # centro de la celda original -> centro del cuadro; pies de la fila -> borde de abajo
                dx = round(CELDA / 2 - cw * k / 2)
                dy = round(CELDA - 1 - base * k)
                cuadro = Image.new("RGBA", (CELDA, CELDA), (0, 0, 0, 0))
                cuadro.paste(peq, (dx, dy), peq)
                tira.alpha_composite(cuadro, ((fila * 4 + col) * CELDA, 0))
        tira = paleta(tira)
        tira.save(SP + "chibi_" + nombre + ".png", optimize=True)
        frente = tira.crop((8 * CELDA, 0, 9 * CELDA, CELDA))  # cuadro "quieto de frente", para la ayuda
        frente.crop(frente.getbbox()).save(SP + "chibi_" + nombre + "_frente.png", optimize=True)
        if nombre == "jefe":
            gerente(tira).save(SP + "chibi_gerente.png", optimize=True)
        print("ok", nombre)


def paleta(tira):
    """Reduce a pocos colores planos (sin degradados ni ruido de la IA)."""
    rgb = tira.convert("RGB")
    q = rgb.quantize(colors=COLORES, method=Image.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    out = q.convert("RGBA"); out.putalpha(tira.getchannel("A"))
    return out


def gerente(tira):
    """Traje y corbata azules -> vinotinto y dorado; pelo gris -> canoso."""
    out = tira.copy(); px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if 0.52 < h < 0.72 and s > 0.25:          # azules
                if v > 0.6:                            # corbata clara -> dorado
                    nr, ng, nb = colorsys.hsv_to_rgb(0.12, 0.75, min(1, v * 1.05))
                else:                                  # traje -> vinotinto
                    nr, ng, nb = colorsys.hsv_to_rgb(0.95, 0.65, min(1, v * 1.15 + 0.08))
                px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a)
            elif s < 0.12 and 0.35 < v < 0.8:          # pelo gris -> canoso
                c = round(min(255, v * 255 + 60))
                px[x, y] = (c, c, min(255, c + 6), a)
    return out


if __name__ == "__main__":
    construir()
