const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const env={URLSearchParams,Date};vm.createContext(env);
for(const file of ['sprite-runtime.js','sprite-seasonal.js'])vm.runInContext(fs.readFileSync(__dirname+'/../src/'+file,'utf8'),env);
const S=env.SpriteSeasonal,R=env.SpriteRuntime,c=JSON.parse(fs.readFileSync(__dirname+'/../src/sprites.config.json','utf8'));
assert.equal(S.isHalloween('',new Date(2026,9,22)),false);assert.equal(S.isHalloween('',new Date(2026,9,23)),true);
assert.equal(S.isHalloween('',new Date(2026,10,1)),true);assert.equal(S.isHalloween('',new Date(2026,10,2)),false);
assert.equal(S.isHalloween('?tema=normal',new Date(2026,9,26)),false);assert.equal(S.isHalloween('?tema=halloween',new Date(2026,0,1)),true);
const normal=R.applyTheme(c,'normal'),season=R.applyTheme(c,'halloween');
for(const id of ['player','playerDirections','playerWork','boss','manager','mate','cleaner','gossip','intern']){
 assert(season.assets[id].file.startsWith('sprites/halloween/'));
 assert.equal(season.assets[id].columns,4);assert.equal(season.assets[id].rows,3);
 const png=fs.readFileSync(__dirname+'/../'+season.assets[id].file);assert.equal(png.readUInt32BE(16),256);assert.equal(png.readUInt32BE(20),216);
 assert.equal(normal.assets[id].file,c.assets[id].file);
 assert(c.assets[id].halloween); // Applying a theme must not mutate the saved catalog.
}
assert.equal(normal.assets.player.file,normal.assets.playerWork.file);
assert.deepEqual(Array.from(normal.assets.playerWork.animations.work.frames),[0,1,2,3]);
assert.deepEqual(Array.from(normal.assets.player.animations.celebrate.frames),[4,5,6,7]);
assert.equal(R.frame(normal.assets.player,'celebrate',.01),4);assert.equal(R.frame(normal.assets.player,'celebrate',.30),7);
function renderHalo(time){const calls=[],ctx={save(){},restore(){},fillRect(...args){calls.push([this.fillStyle,...args]);}};S.halo(ctx,100.2,200.8,time);assert.equal(calls.length,96);for(const call of calls)assert(call.slice(1).every(Number.isInteger));return JSON.stringify(calls);}
assert.notEqual(renderHalo(0),renderHalo(.4));
console.log('Passed: seasonal dates, theme overrides, 9 complete 4×3 sheets, matching action shirt, short celebration sequence and animated pixel halo.');
