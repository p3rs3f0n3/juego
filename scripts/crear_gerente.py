"""Crea al Gerente como variante de paleta del jefe (no se redibuja: se cambian colores).
Correr después de crear_jefe.py, desde la carpeta scripts:  python crear_gerente.py
"""
from PIL import Image

SP = "../sprites/"

# color del jefe -> color del gerente
SWAP = {
    (52, 52, 66): (112, 32, 52),     # traje -> vinotinto
    (38, 38, 50): (78, 20, 44),      # sombra del traje (más fría, hacia violeta)
    (40, 120, 220): (232, 184, 64),  # corbata azul -> dorada
    (20, 70, 150): (168, 118, 34),   # sombra de la corbata
    (140, 140, 148): (214, 212, 222),  # pelo gris -> canoso
    (36, 36, 46): (44, 30, 40),      # pantalón
}

img = Image.open(SP + "boss_48.png").convert("RGBA")
px = img.load()
for y in range(img.height):
    for x in range(img.width):
        r, g, b, a = px[x, y]
        if a and (r, g, b) in SWAP:
            px[x, y] = SWAP[(r, g, b)] + (a,)
img.save(SP + "gerente_48.png")
bg = Image.new("RGBA", (384, 384), (14, 14, 16, 255))
bg.alpha_composite(img.resize((384, 384), Image.NEAREST))
bg.save(SP + "gerente_preview.png")
print("ok")
