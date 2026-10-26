"""Prepara los assets aprobables de diseño v4 sin alterar cajas de colisión.
Fuente PNG: design-proposals/design-v4. Salida PNG transparente en sprites/.
Conserva las hojas de personajes en 4 columnas x 3 filas.
Ejecutar desde scripts, antes de construir_juego.py.
"""
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent

def cargar(nombre):
    return Image.open(ROOT / 'design-proposals/design-v4' / nombre).convert('RGBA')

def preparar_jugadora():
    im = cargar('jugadora-direcciones.png')
    w, h = im.width // 4, im.height // 3
    cells = [im.crop((c*w, r*h, (c+1)*w, (r+1)*h)) for r in range(3) for c in range(4)]
    # Common scale, independent centers, fixed soles: no frame-to-frame size jitter.
    bounds = [cell.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox() for cell in cells]
    scale = 50 / max(b[3]-b[1] for b in bounds)
    out = Image.new('RGBA', (224, 168))
    for i, (cell, b) in enumerate(zip(cells, bounds)):
        sprite = cell.crop(b)
        sprite = sprite.resize((round(sprite.width*scale), round(sprite.height*scale)), Image.Resampling.NEAREST)
        sprite.putalpha(sprite.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
        out.alpha_composite(sprite, ((i%4)*56+(56-sprite.width)//2, (i//4)*56+55-sprite.height))
    out.quantize(colors=96, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(ROOT/'sprites/chibi_jugadora_direcciones.png', optimize=True)

def preparar_oficina():
    im = cargar('oficina-atlas.png')
    w, h = im.width//3, im.height//2
    out = Image.new('RGBA', (576,384))
    for i in range(6):
        cell = im.crop(((i%3)*w,(i//3)*h,(i%3+1)*w,(i//3+1)*h))
        if i == 4: cell = cargar('planta-referencia.png')
        b = cell.getchannel('A').point(lambda a: 255 if a >= 200 else 0).getbbox()
        if not b: raise ValueError('Celda vacía: '+str(i))
        sprite = cell.crop(b).resize((188,188), Image.Resampling.NEAREST)
        sprite.putalpha(sprite.getchannel('A').point(lambda a: 255 if a >= 200 else 0))
        out.alpha_composite(sprite, ((i%3)*192+2,(i//3)*192+2))
    out.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(ROOT/'sprites/oficina_detallada.png', optimize=True)

if __name__ == '__main__':
    preparar_jugadora()
    preparar_oficina()
    print('Assets v4 preparados')
