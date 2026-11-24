/* Exporta las hojas PNG de temporada. Requiere @napi-rs/canvas solo al regenerar arte.
   node preparar_octubre.cjs           → hojas base de octubre + disfraces de Halloween
   node preparar_octubre.cjs navidad   → solo los disfraces de Navidad (sprites/navidad/) */
const fs=require('node:fs'),path=require('node:path');
const {createCanvas,loadImage}=require('@napi-rs/canvas');
require('../src/sprite-seasonal.js');
const root=path.resolve(__dirname,'..');
function bounds(ctx,w,h){
 const p=ctx.getImageData(0,0,w,h).data;let x0=w,y0=h,x1=0,y1=0;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(p[(y*w+x)*4+3]>=128){x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}
 if(x0>x1)throw Error('Celda vacía');return{x:x0,y:y0,w:x1-x0+1,h:y1-y0+1};
}
async function prepare(source,destination){
 const img=await loadImage(path.join(root,source)),cw=img.width/4,ch=img.height/3;
 if(!Number.isInteger(cw)||!Number.isInteger(ch))throw Error('Se requiere cuadrícula 4 × 3 exacta');
 const cells=[];for(let i=0;i<12;i++){const c=createCanvas(cw,ch),ctx=c.getContext('2d');ctx.drawImage(img,(i%4)*cw,Math.floor(i/4)*ch,cw,ch,0,0,cw,ch);cells.push({canvas:c,box:bounds(ctx,cw,ch)});}
 const scale=50/Math.max(...cells.map(c=>c.box.h)),out=createCanvas(224,168),ctx=out.getContext('2d');ctx.imageSmoothingEnabled=false;
 for(let i=0;i<12;i++){
   const {canvas,box:b}=cells[i],w=Math.round(b.w*scale),h=Math.round(b.h*scale);
   // Cabeza estable y escala común: no se recentra cada celda completa por el balanceo de brazos.
   const pixel=canvas.getContext('2d').getImageData(0,0,cw,ch).data;
   let hx0=cw,hx1=0;
   for(let y=b.y;y<b.y+b.h*.55;y++)for(let x=b.x;x<b.x+b.w;x++)if(pixel[(y*cw+x)*4+3]>=128){hx0=Math.min(hx0,x);hx1=Math.max(hx1,x);}
   const headCenter=(hx0+hx1)/2,dx=Math.round(28-(headCenter-b.x)*scale);
   ctx.drawImage(canvas,b.x,b.y,b.w,b.h,(i%4)*56+dx,Math.floor(i/4)*56+5,w,h);
 }
 fs.writeFileSync(path.join(root,destination),out.toBuffer('image/png'));
}
function headBox(ctx,w,h){
 // La componente conectada más grande excluye corazones y gotas de sudor al colocar accesorios.
 const p=ctx.getImageData(0,0,w,h).data,seen=new Uint8Array(w*h);let best=[];
 for(let i=0;i<w*h;i++){
  if(seen[i]||p[i*4+3]<128)continue;const stack=[i],comp=[];seen[i]=1;
  while(stack.length){const v=stack.pop();comp.push(v);const x=v%w,y=Math.floor(v/w);for(const n of [x>0?v-1:-1,x<w-1?v+1:-1,y>0?v-w:-1,y<h-1?v+w:-1])if(n>=0&&!seen[n]&&p[n*4+3]>=128){seen[n]=1;stack.push(n);}}
  if(comp.length>best.length)best=comp;
 }
 const ys=best.map(i=>Math.floor(i/w)),top=Math.min(...ys),head=best.filter(i=>Math.floor(i/w)<top+14).map(i=>i%w);
 return{x:Math.round((Math.min(...head)+Math.max(...head))/2),y:top+1};
}
async function bake(id,a,theme){
 const img=await loadImage(path.join(root,a.file)),out=createCanvas(256,216),ctx=out.getContext('2d');ctx.imageSmoothingEnabled=false;
 for(let f=0;f<a.columns*a.rows;f++){
  const cell=createCanvas(64,72),c=cell.getContext('2d');c.imageSmoothingEnabled=false;
  c.drawImage(img,(f%a.columns)*a.cellWidth,Math.floor(f/a.columns)*a.cellHeight,a.cellWidth,a.cellHeight,4,16,56,56);
  SpriteSeasonal.accessory(c,id,headBox(c,64,72),theme);ctx.drawImage(cell,(f%4)*64,Math.floor(f/4)*72);
 }
 fs.writeFileSync(path.join(root,'sprites/'+theme+'/'+id+'.png'),out.toBuffer('image/png'));
}
const IDS=['player','playerDirections','playerWork','boss','manager','mate','cleaner','gossip','intern'];
(async()=>{
 const config=JSON.parse(fs.readFileSync(path.join(root,'src/sprites.config.json'),'utf8'));
 if(process.argv[2]==='navidad'){
  fs.mkdirSync(path.join(root,'sprites/navidad'),{recursive:true});
  for(const id of IDS)await bake(id,config.assets[id],'navidad');
  console.log('Exportadas 9 hojas de Navidad (PNG transparente 4 × 3).');return;
 }
 fs.mkdirSync(path.join(root,'sprites/halloween'),{recursive:true});
 await prepare('design-proposals/octubre-2026/jugadora-caminar.png','sprites/jugadora_octubre.png');
 await prepare('design-proposals/octubre-2026/jugadora-acciones.png','sprites/jugadora_acciones_octubre.png');
 for(const id of IDS)await bake(id,config.assets[id],'halloween');
 console.log('Exportadas 2 hojas base y 9 hojas Halloween (PNG transparente 4 × 3).');
})().catch(e=>{console.error(e);process.exitCode=1;});
