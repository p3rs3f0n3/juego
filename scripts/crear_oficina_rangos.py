"""Versiones por rango de los muebles de Manuel (sprites/oficina_detallada.png), para que al ascender
se note el cambio de oficina. Uso (desde la carpeta scripts):  python crear_oficina_rangos.py

- Practicante: el original (madera clara, panel verde, silla azul).
- Analista (área de TI moderna): escritorio blanco laminado, panel azul, silla turquesa.
- Jefe de TI (piso ejecutivo): caoba oscura, panel vinotinto, silla de cuero negro.

Solo se recolorean los escritorios y el mueble de la cafetera; servidores, impresora, mata y ventana
quedan iguales (la mata crece en el juego) y en estas imágenes sus celdas van vacías. Salida: sprites/oficina_detallada_analista.png y _jefe.png.
"""
import colorsys
from PIL import Image

SP = "../sprites/"
CELDAS = [(0, 0, 192, 192), (0, 192, 192, 384)]  # escritorio · cafetera


def madera(h, s, v):
    return 0.04 <= h <= 0.12 and s > 0.5 and v > 0.15


def panel(h, s, v):
    return 0.38 <= h <= 0.53 and 0.1 <= s <= 0.36 and v > 0.3


def silla(h, s, v):
    return 0.56 <= h <= 0.64 and s > 0.42 and v > 0.25


RANGOS = {
    "analista": {
        "madera": lambda h, s, v: (0.58, 0.05, 0.62 + 0.36 * v),
        "panel": lambda h, s, v: (0.58, 0.45, min(1, v * 1.05)),
        "silla": lambda h, s, v: (0.5, 0.6, min(1, v * 1.15)),
    },
    "jefe": {
        "madera": lambda h, s, v: (0.02, 0.72, v * 0.55),
        "panel": lambda h, s, v: (0.97, 0.45, v * 0.75),
        "silla": lambda h, s, v: (0.0, 0.1, v * 0.45),
    },
}

base = Image.open(SP + "oficina_detallada.png").convert("RGBA")
for nombre, cambios in RANGOS.items():
    im = base.copy(); px = im.load()
    for x0, y0, x1, y1 in CELDAS:
        for y in range(y0, y1):
            for x in range(x0, x1):
                r, g, b, a = px[x, y]
                if not a:
                    continue
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                for parte, prueba in (("madera", madera), ("panel", panel), ("silla", silla)):
                    if prueba(h, s, v):
                        nr, ng, nb = colorsys.hsv_to_rgb(*cambios[parte](h, s, v))
                        px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a)
                        break
    solo = Image.new("RGBA", im.size, (0, 0, 0, 0))  # el resto de celdas vacías: pesa menos y se usa el original
    for caja in CELDAS:
        solo.paste(im.crop(caja), caja[:2])
    solo.quantize(colors=64, method=Image.FASTOCTREE, dither=Image.Dither.NONE).save(SP + "oficina_detallada_" + nombre + ".png", optimize=True)
    print("ok", nombre)
