"""Servidor local del juego y del estudio de sprites.
python scripts/servidor_diseno.py [--port 8766]
Solo escucha en 127.0.0.1. Guarda configuración validada y regenera el HTML.
"""
import argparse
import base64
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import struct
import subprocess
import sys
import threading
from urllib.parse import urlsplit
from uuid import uuid4
from sprite_config import validate_config

ROOT = Path(__file__).resolve().parent.parent
LOCK = threading.Lock()
MAX_BODY = 12*1024*1024

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def json_response(self,status,data):
        content=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(content)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(content)
    def do_GET(self):
        if urlsplit(self.path).path == '/__sprites/files':
            files=sorted(str(p.relative_to(ROOT)) for folder in ('sprites','arte','design-proposals') for p in (ROOT/folder).rglob('*.png'))
            return self.json_response(200,{'files':files})
        return super().do_GET()
    def do_POST(self):
        host=self.headers.get('Host','');origin=self.headers.get('Origin')
        if host not in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}') or (origin and origin not in (f'http://{host}',)):
            return self.json_response(403,{'error':'Solo se aceptan cambios desde este estudio local.'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=MAX_BODY: raise ValueError('Solicitud demasiado grande o vacía.')
            if self.headers.get('Content-Type','').split(';')[0]!='application/json': raise ValueError('Se requiere JSON.')
            data=json.loads(self.rfile.read(size));path=urlsplit(self.path).path
            if path=='/__sprites/upload':
                raw=base64.b64decode(data.get('data',''),validate=True)
                if not 24<=len(raw)<=8*1024*1024 or raw[:8]!=b'\x89PNG\r\n\x1a\n': raise ValueError('El archivo debe ser un PNG de menos de 8 MB.')
                w,h=struct.unpack('>II',raw[16:24])
                if not 1<=w<=8192 or not 1<=h<=8192: raise ValueError('Dimensiones PNG no compatibles.')
                file='sprites/custom_'+uuid4().hex[:12]+'.png'
                (ROOT/file).write_bytes(raw)
                return self.json_response(201,{'file':file,'width':w,'height':h})
            if path!='/__sprites/save-config': return self.json_response(404,{'error':'Ruta desconocida.'})
            validate_config(data,ROOT)
            with LOCK:
                config_path=ROOT/'src/sprites.config.json';old=config_path.read_bytes()
                content=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
                temporary=config_path.with_suffix('.tmp')
                temporary.write_bytes(content);temporary.replace(config_path)
                try:
                    result=subprocess.run([sys.executable,str(ROOT/'scripts/construir_juego.py')],cwd=ROOT/'scripts',capture_output=True,text=True,timeout=30)
                    if result.returncode: raise ValueError('No se pudo regenerar el juego: '+result.stderr[-800:])
                except Exception:
                    config_path.write_bytes(old)
                    raise
            return self.json_response(200,{'ok':True,'file':'src/sprites.config.json','game':'ticket_rush.html'})
        except (ValueError,TypeError,KeyError,OverflowError) as e: return self.json_response(400,{'error':str(e)})
        except Exception as e: return self.json_response(500,{'error':'No se pudo guardar: '+str(e)})

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8766);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'Estudio: http://127.0.0.1:{args.port}/tools/sprites/\nJuego: http://127.0.0.1:{args.port}/ticket_rush.html?tema=normal',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
