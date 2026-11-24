const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const env={URLSearchParams,Date};vm.createContext(env);
for(const file of ['sprite-runtime.js','sprite-seasonal.js'])vm.runInContext(fs.readFileSync(__dirname+'/../src/'+file,'utf8'),env);
const S=env.SpriteSeasonal,R=env.SpriteRuntime,c=JSON.parse(fs.readFileSync(__dirname+'/../src/sprites.config.json','utf8'));
// Fechas: del 1 de diciembre al 6 de enero (Reyes); Halloween no cambia.
assert.equal(S.season('',new Date(2026,10,30)),'normal');assert.equal(S.season('',new Date(2026,11,1)),'navidad');
assert.equal(S.season('',new Date(2026,11,24)),'navidad');assert.equal(S.season('',new Date(2027,0,6)),'navidad');
assert.equal(S.season('',new Date(2027,0,7)),'normal');assert.equal(S.season('',new Date(2026,9,31)),'halloween');
assert.equal(S.isNavidad('',new Date(2026,11,25)),true);assert.equal(S.isHalloween('',new Date(2026,11,25)),false);
assert.equal(S.season('?tema=navidad',new Date(2026,5,1)),'navidad');assert.equal(S.season('?tema=normal',new Date(2026,11,25)),'normal');
assert.equal(S.season('?tema=halloween',new Date(2026,11,25)),'halloween');assert.equal(S.isHalloween('?tema=navidad',new Date(2026,9,25)),false);
const normal=R.applyTheme(c,'normal'),season=R.applyTheme(c,'navidad');
for(const id of ['player','playerDirections','playerWork','boss','manager','mate','cleaner','gossip','intern']){
 assert(season.assets[id].file.startsWith('sprites/navidad/'),id);
 assert.equal(season.assets[id].columns,4);assert.equal(season.assets[id].rows,3);
 const png=fs.readFileSync(__dirname+'/../'+season.assets[id].file);assert.equal(png.readUInt32BE(16),256);assert.equal(png.readUInt32BE(20),216);
 assert.equal(normal.assets[id].file,c.assets[id].file);
 assert(!season.assets[id].halloween&&!season.assets[id].navidad);
 assert(c.assets[id].navidad&&c.assets[id].halloween); // Aplicar el tema no cambia el catálogo guardado.
}
// Los muebles no tienen disfraz: siguen iguales en Navidad.
for(const id of ['desk','server','printer','coffee','plant','window'])assert.equal(season.assets[id].file,c.assets[id].file);
assert.throws(()=>R.validate({version:1,assets:{x:{...c.assets.boss,navidad:{...c.assets.boss.navidad,halloween:c.assets.boss.halloween}}}}));
// Adornos y accesorios: se dibujan sin errores y en píxeles enteros.
const calls=[],ctx={save(){},restore(){},fillRect(...a){calls.push(a);}};
S.decorations(ctx,768,1.5,'navidad');for(const id of ['player','boss','manager','mate','cleaner','gossip','intern'])S.accessory(ctx,id,{x:32,y:20},'navidad');
assert(calls.length>100);for(const a of calls)assert(a.every(Number.isInteger),JSON.stringify(a));
console.log('Passed: Christmas dates (1 dic – 6 ene), ?tema=navidad, 9 complete 4×3 costume sheets, furniture untouched and pixel-aligned decorations.');
