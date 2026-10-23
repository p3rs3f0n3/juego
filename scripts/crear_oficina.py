"""Atlas de oficina pixel art. Ejecutar antes de construir_juego.py.

Objetos en las posiciones y tamaños del juego; no modifica sus colisiones.
Tres filas de 128 px: oficina, TI y ejecutivo. PNG transparente sin dependencias web.
"""
from pathlib import Path
from PIL import Image, ImageDraw

PALETAS = [
    dict(wood='#d9b77d', light='#f0d39a', edge='#806247', dark='#a98759',
         divider='#849c92', trim='#435b5c', chair='#465e73', seat='#647e92'),
    dict(wood='#c6d4d7', light='#e6eeee', edge='#738793', dark='#9caeb9',
         divider='#809da5', trim='#425c70', chair='#435d79', seat='#6483a1'),
    dict(wood='#a88461', light='#c9a47b', edge='#594b3f', dark='#826247',
         divider='#89977d', trim='#505e50', chair='#5d5264', seat='#7b6d80'),
]


def crear():
    atlas = Image.new('RGBA', (384, 384))
    d = ImageDraw.Draw(atlas)

    for fila, p in enumerate(PALETAS):
        oy = fila * 128

        def r(x, y, w, h, color):
            d.rectangle((x, oy + y, x + w - 1, oy + y + h - 1), fill=color)

        # Mesa: separación baja, superficie, cajonera y silla recogida debajo.
        r(1, 7, 94, 22, p['trim']); r(3, 9, 90, 17, p['divider'])
        r(4, 10, 88, 2, '#b4c5b8'); r(1, 5, 3, 27, p['trim']); r(92, 5, 3, 27, p['trim'])
        r(0, 29, 96, 24, p['edge']); r(2, 30, 92, 18, p['wood'])
        r(2, 30, 92, 3, p['light']); r(4, 47, 88, 3, p['dark'])
        for x, y, w in [(7, 36, 17), (68, 34, 21), (28, 44, 10), (74, 44, 12)]:
            r(x, y, w, 1, p['dark'])
        r(4, 51, 22, 11, p['edge']); r(6, 52, 18, 8, '#b5bcad')
        r(7, 53, 16, 1, '#d9ddcb'); r(12, 55, 6, 2, '#758480')
        r(88, 50, 4, 12, p['edge']); r(89, 51, 2, 8, p['dark'])
        # La silla queda dentro de la base de choque, no invade el pasillo.
        r(36, 44, 25, 16, '#2d3e48'); r(38, 45, 21, 11, p['chair'])
        r(40, 46, 17, 2, p['seat']); r(39, 55, 19, 3, p['seat'])
        r(33, 49, 3, 7, '#394d56'); r(61, 49, 3, 7, '#394d56')
        r(47, 59, 3, 3, '#34444c'); r(39, 61, 18, 2, '#34444c')
        # Teléfono y papeles a los lados de la pantalla.
        r(71, 32, 8, 10, '#43545b'); r(72, 33, 2, 7, '#243a43')
        r(75, 35, 2, 2, '#9cb1af'); r(75, 38, 2, 2, '#9cb1af')
        r(81, 34, 10, 10, '#b5aa8e'); r(81, 33, 9, 9, '#f5eedb')
        r(83, 35, 5, 1, '#8f9ea1'); r(83, 38, 4, 1, '#8f9ea1')

        # Servidores: 96 x 80, dos armarios con zócalo y ventilación.
        for k in range(2):
            x = 98 + k * 46
            r(x, 10, 44, 68, '#34434c'); r(x + 2, 12, 40, 62, '#52616d')
            r(x + 2, 12, 40, 3, '#71808a'); r(x + 4, 18, 36, 52, '#293943')
            for j in range(5):
                y = 20 + j * 10
                r(x + 6, y, 32, 8, '#42535e'); r(x + 7, y, 30, 1, '#62737b')
                r(x + 21, y + 3, 12, 1, '#22343c')
            r(x + 3, 75, 5, 4, '#26373b'); r(x + 35, 75, 5, 4, '#26373b')

        # Impresora: 96 x 64, papel, bandeja y mandos.
        r(214, 15, 52, 14, '#9da69d'); r(216, 13, 48, 14, '#f7f3e4')
        r(222, 18, 30, 1, '#b8c6bf'); r(222, 21, 25, 1, '#b8c6bf')
        r(200, 26, 80, 30, '#657978'); r(202, 27, 76, 26, '#d2d8cd')
        r(202, 27, 76, 4, '#e8eadd'); r(202, 48, 76, 5, '#a2b3ae')
        r(214, 44, 44, 6, '#3b5154'); r(219, 48, 34, 13, '#fcf7e7')
        r(222, 52, 25, 1, '#bdc6bb'); r(222, 55, 20, 1, '#bdc6bb')
        r(255, 33, 16, 8, '#354c53'); r(257, 35, 4, 3, '#69b58a')
        r(264, 36, 3, 2, '#a7b5ad')

        # Cafetera con mueble bajo: 48 x 64.
        r(294, 37, 37, 26, p['edge']); r(295, 38, 35, 4, p['light'])
        r(297, 44, 30, 17, p['wood']); r(311, 44, 1, 16, p['dark'])
        r(308, 49, 2, 5, p['edge']); r(314, 49, 2, 5, p['edge'])
        r(296, 17, 32, 28, '#384c51'); r(298, 18, 28, 4, '#718382')
        r(300, 23, 23, 12, '#20373c'); r(302, 36, 20, 9, '#253e42')
        r(305, 36, 11, 9, '#f3e9cc'); r(316, 38, 4, 5, '#f3e9cc')
        r(307, 37, 7, 2, '#78573e'); r(299, 44, 26, 2, '#98aaa5')

        # Planta: maceta y hojas con luces y sombras por grupos de píxeles.
        r(349, 45, 23, 17, '#e4d9bd'); r(347, 43, 27, 4, '#f4ebd4')
        r(351, 47, 3, 12, '#f5ecd4'); r(369, 47, 3, 13, '#b5b7a0')
        r(351, 43, 19, 2, '#76604a'); r(359, 18, 3, 27, '#526b3e')
        for x, y, w, h, col in [
            (350, 20, 12, 10, '#5e7f4d'), (360, 13, 12, 12, '#729354'),
            (344, 29, 14, 10, '#4a704c'), (361, 27, 14, 12, '#608849'),
            (350, 13, 8, 10, '#426749'), (367, 21, 9, 8, '#83a05e'),
            (352, 31, 9, 10, '#729354'), (359, 22, 9, 9, '#8eac6c')]:
            r(x, y, w, h, col); r(x + 2, y + 1, max(2, w - 5), 2, '#a3b975')

    destino = Path(__file__).resolve().parent.parent / 'sprites' / 'oficina.png'
    atlas.save(destino, optimize=True)
    print('Listo:', destino.name, atlas.size)


if __name__ == '__main__':
    crear()
