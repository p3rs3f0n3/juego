/* Shared sprite slicing and placement: used by both the game and its sprite studio. */
(function (root) {
  'use strict';
  const KEY = 'ticket-rush-sprites-v1';
  const SEASONS = ['halloween', 'navidad'];  // variantes de temporada de cada slot
  function validate(config) {
    if (!config || config.version !== 1 || !config.assets || typeof config.assets !== 'object') throw Error('Configuración no compatible.');
    for (const [id, a] of Object.entries(config.assets)) {
      if (!/^[a-zA-Z][a-zA-Z0-9]*$/.test(id) || !a || typeof a !== 'object') throw Error('Asset inválido.');
      if (typeof a.label !== 'string' || !a.label.length || a.label.length > 512) throw Error('Nombre de slot inválido: '+id);
      if (a.source != null && (typeof a.source !== 'string' || !/^(sprites|design-proposals|arte)\/[a-zA-Z0-9_./-]+\.(png|webp)$/.test(a.source) || a.source.includes('..'))) throw Error('Referencia no válida: '+id);
      if (typeof a.file !== 'string' || !/^(sprites|design-proposals|arte)\/[a-zA-Z0-9_./-]+\.png$/.test(a.file) || a.file.includes('..')) throw Error('Archivo no permitido: '+id);
      for (const k of ['columns','rows','cellWidth','cellHeight','width','height','stride']) if (!Number.isFinite(a[k]) || a[k] <= 0 || a[k] > 4096) throw Error('Valor inválido: '+id+' · '+k);
      for (const k of ['columns','rows','cellWidth','cellHeight']) if (!Number.isInteger(a[k])) throw Error('La cuadrícula requiere enteros.');
      for (const k of ['anchorX','anchorY','offsetX','offsetY']) if (!Number.isFinite(a[k]) || Math.abs(a[k]) > 4096) throw Error('Posición inválida: '+id);
      for (const season of SEASONS) if (a[season]) {
        if (SEASONS.some(s => a[season][s])) throw Error('La variante de temporada no puede contener otra variante.');
        validate({version:1, assets:{[id]:a[season]}});
      }
      if (!a.animations || !Object.keys(a.animations).length) throw Error('Faltan animaciones: '+id);
      for (const an of Object.values(a.animations)) {
        if (!Array.isArray(an.frames) || !an.frames.length || an.frames.length > 256 || an.frames.some(f => !Number.isInteger(f) || f < 0 || f >= a.columns*a.rows)) throw Error('Fotogramas fuera de la hoja: '+id);
        if (!Number.isFinite(an.fps) || an.fps <= 0 || an.fps > 60) throw Error('Velocidad inválida: '+id);
      }
      for (const r of Object.values(a.frameRects || {})) if (!r || ['x','y','w','h'].some(k => !Number.isFinite(r[k]) || r[k] < (k==='w'||k==='h'?1:0) || r[k]>8192 || !Number.isInteger(r[k]))) throw Error('Recorte por cuadro inválido: '+id);
      for (const o of Object.values(a.frameOffsets || {})) if (!o || !Number.isFinite(o.x) || !Number.isFinite(o.y) || Math.abs(o.x)>4096 || Math.abs(o.y)>4096) throw Error('Ajuste de fotograma inválido: '+id);
    }
    return config;
  }
  function animation(a, name) { return a.animations[name] || a.animations.idle || Object.values(a.animations)[0]; }
  function frame(a, name, time, step) {
    const an=animation(a,name), n=step === undefined ? Math.floor(time*an.fps) : Math.floor(step);
    const index=an.loop === false ? Math.max(0,Math.min(an.frames.length-1,n)) : ((n%an.frames.length)+an.frames.length)%an.frames.length;
    return an.frames[index];
  }
  function rect(a, f) { const r=(a.frameRects || {})[f]; return r ? [r.x,r.y,r.w,r.h] : [(f%a.columns)*a.cellWidth, Math.floor(f/a.columns)*a.cellHeight,a.cellWidth,a.cellHeight]; }
  function draw(ctx,img,a,f,x,y,flip) {
    const r=rect(a,f), o=(a.frameOffsets || {})[f] || {x:0,y:0};
    if (!img || !img.complete || !img.naturalWidth || f<0 || f>=a.columns*a.rows || r[0]+r[2]>img.naturalWidth || r[1]+r[3]>img.naturalHeight) return false;
    ctx.save(); ctx.imageSmoothingEnabled=false;
    ctx.translate(Math.round(x+a.offsetX),Math.round(y+a.offsetY)); if(flip)ctx.scale(-1,1);
    ctx.drawImage(img,...r,Math.round(-a.anchorX+o.x),Math.round(-a.anchorY+o.y),a.width,a.height); ctx.restore(); return true;
  }
  function resolve(defaults, storage, search) {
    const base=JSON.parse(JSON.stringify(defaults));
    if (new URLSearchParams(search || '').get('sprites') !== 'preview') return validate(base);
    try {
      const draft=validate(JSON.parse(storage.getItem(KEY)));
      // Preview may edit existing slots, but cannot remove the slots required by the game.
      for(const id of Object.keys(base.assets)) if(draft.assets[id]) base.assets[id]=draft.assets[id];
    } catch (_) { /* A missing or invalid draft never prevents starting the game. */ }
    return validate(base);
  }
  function applyTheme(config, theme) {
    const result=JSON.parse(JSON.stringify(config));
    for(const [id,a] of Object.entries(result.assets)) {
      if(SEASONS.includes(theme) && a[theme]) result.assets[id]=a[theme];
      for(const season of SEASONS) delete result.assets[id][season];
    }
    return validate(result);
  }
  root.SpriteRuntime={KEY,SEASONS,validate,animation,frame,rect,draw,resolve,applyTheme};
})(typeof globalThis !== 'undefined' ? globalThis : window);
