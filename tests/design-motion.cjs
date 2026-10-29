// Focused regression checks for distance-based gait, completion and repair screens.
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const source = fs.readFileSync(__dirname + '/../src/game_template.html', 'utf8');
function fn(name) { const start = source.indexOf('  function ' + name + '('); assert(start >= 0); return source.slice(start, source.indexOf('\n  }', start) + 4); }
const calls = [];
const env = {Math, P:{}, N:{}, anim:1, R:(...a)=>calls.push(a), approach:(e,a,d)=>{e[a]+=d; return true;}, slideAround:()=>{},
  score:0, done:0, clock:10, lastDone:0, combo:0, rank:0, lives:3, MAX_LIVES:3,
  pop:()=>{}, beep:()=>{}, setTimeout:()=>{}, removeTicket:()=>{}, rankOf:()=>0};
vm.createContext(env);
vm.runInContext(['move','gait','facing','screen','complete'].map(fn).join('\n'),env);
let actor = {x:0,y:0};
assert.equal(env.move(actor, 0, -16), true); assert.equal(actor.dir,'up'); assert.equal(env.gait(actor,0),1);
assert.equal(env.gait(actor,0),1); // Drawing again must not advance or flip the actor.
assert.equal(env.move(actor, -16, 0), true); assert.equal(actor.face,-1); assert.equal(actor.dir,'left');
assert.equal(env.move(actor, 16, 0),true); assert.equal(actor.dir,'right');
assert.equal(env.move(actor, 0, 16),true); assert.equal(actor.dir,'down');
env.approach=()=>false;
const distance = actor.walk;
assert.equal(env.move(actor, 6, 0),false); assert.equal(actor.walk,distance);
const ticket = {pts:10, st:{x:0,y:0,w:96}};
env.P.fixing=true; env.nearestTicket=()=>ticket;
env.complete(ticket); assert.equal(env.P.cheer,0.32); assert.equal(env.P.fixing,false); assert.equal(env.done,1);
env.P.fixing=true;
env.screen(0,0,34,20,ticket,0); const first=JSON.stringify(calls); calls.length=0;
env.anim=1.1; env.screen(0,0,34,20,ticket,0); assert.notEqual(JSON.stringify(calls), first);
assert(calls.some(a=>a[4]==='#70f0b7')); calls.length=0;
env.P.fixing=false; env.screen(0,0,34,20,ticket,0); assert(calls.some(a=>a[4]==='#2551bd'));
console.log('Passed: 4 directions, blocked gait, render stability, short celebration, animated repair screen.');
