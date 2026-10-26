"""Validación compartida por el generador y el servidor local del visor."""
import math
import re
import struct
REQUIRED = {'player','playerDirections','playerWork','boss','manager','mate','cleaner','gossip','intern','desk','server','printer','coffee','plant','window'}

def number(value, low, high, integer=False):
    return isinstance(value, (int,float)) and not isinstance(value,bool) and math.isfinite(value) and low <= value <= high and (not integer or int(value)==value)

def validate_config(config, root):
    if not isinstance(config,dict) or config.get('version')!=1 or not isinstance(config.get('assets'),dict) or set(config['assets']) != REQUIRED:
        raise ValueError('La configuración debe conservar todos los slots del juego.')
    for id,a in config['assets'].items():
        if not isinstance(a,dict): raise ValueError('Asset inválido: '+id)
        if not isinstance(a.get('label'),str) or not 1<=len(a['label'])<=512: raise ValueError('Nombre de slot inválido: '+id)
        source=a.get('source')
        if source is not None and (not isinstance(source,str) or not re.fullmatch(r'(sprites|design-proposals|arte)/[a-zA-Z0-9_./-]+\.(png|webp)',source) or '..' in source): raise ValueError('Referencia no válida: '+id)
        file=a.get('file','')
        if not re.fullmatch(r'(sprites|design-proposals|arte)/[a-zA-Z0-9_./-]+\.png', file) or '..' in file:
            raise ValueError('Ruta PNG no válida: '+id)
        path=(root/file).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file(): raise ValueError('Archivo no encontrado: '+file)
        for key in ('columns','rows','cellWidth','cellHeight','width','height','stride'):
            if not number(a.get(key),1,4096,key in ('columns','rows','cellWidth','cellHeight')): raise ValueError('Valor inválido: '+id+' · '+key)
        for key in ('anchorX','anchorY','offsetX','offsetY'):
            if not number(a.get(key),-4096,4096): raise ValueError('Posición inválida: '+id)
        header=path.read_bytes()[:24]
        if header[:8] != b'\x89PNG\r\n\x1a\n': raise ValueError('Debe ser PNG: '+file)
        w,h=struct.unpack('>II',header[16:24])
        if a['columns']*a['cellWidth']>w or a['rows']*a['cellHeight']>h: raise ValueError('La cuadrícula sale del PNG: '+id)
        animations=a.get('animations')
        if not isinstance(animations,dict) or not animations: raise ValueError('Faltan animaciones: '+id)
        for an in animations.values():
            if not isinstance(an,dict) or not isinstance(an.get('frames'),list) or not 1<=len(an['frames'])<=256: raise ValueError('Secuencia inválida: '+id)
            if any(not number(f,0,a['columns']*a['rows']-1,True) for f in an['frames']): raise ValueError('Fotogramas fuera de la hoja: '+id)
            if not number(an.get('fps'),0.1,60): raise ValueError('FPS inválidos: '+id)
        rects=a.get('frameRects',{})
        if not isinstance(rects,dict): raise ValueError('Recorte inválido: '+id)
        for r in rects.values():
            if not isinstance(r,dict) or any(not number(r.get(k),1 if k in ('w','h') else 0,8192,True) for k in ('x','y','w','h')) or r['x']+r['w']>w or r['y']+r['h']>h: raise ValueError('El recorte sale del PNG: '+id)
        offsets=a.get('frameOffsets',{})
        if not isinstance(offsets,dict) or any(not isinstance(o,dict) or not number(o.get('x'),-4096,4096) or not number(o.get('y'),-4096,4096) for o in offsets.values()): raise ValueError('Ajuste por cuadro inválido: '+id)
    return config
