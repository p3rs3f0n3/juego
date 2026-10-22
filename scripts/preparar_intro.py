"""Recorta las 4 viñetas del cómic de la intro (arte/intro/comic.jpg, rejilla 2x2) y las guarda
como intro/1.webp ... intro/4.webp, al lado de ticket_rush.html (no van dentro del HTML para
que el juego siga siendo liviano: solo se descargan cuando se ve la intro).
Uso (desde la carpeta scripts):  python preparar_intro.py
"""
from PIL import Image

# (x0, y0, x1, y1) de cada viñeta, medidos sobre las canaletas blancas del original de 1536x1024
VINETAS = [(16, 16, 762, 508), (775, 16, 1520, 508), (16, 519, 762, 1002), (775, 519, 1520, 1002)]

im = Image.open("../arte/intro/comic.jpg").convert("RGB")
for i, caja in enumerate(VINETAS, 1):
    im.crop(caja).save("../intro/%d.webp" % i, quality=82, method=6)
    print("ok", i)
