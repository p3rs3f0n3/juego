/* Accesorios pixel art, halo de la protagonista y decoración de temporada. */
(function(root){
  'use strict';
  // Temporada activa: 'halloween' (23 oct – 1 nov), 'navidad' (1 dic – 6 ene, Reyes) o 'normal'.
  // Para probar en otra fecha: ?tema=halloween · ?tema=navidad · ?tema=normal.
  function season(search,date){
    const value=new URLSearchParams(search||'').get('tema');
    if(value==='normal'||value==='halloween'||value==='navidad')return value;
    date=date||new Date();const m=date.getMonth(),d=date.getDate();
    if((m===9&&d>=23)||(m===10&&d<=1))return 'halloween';
    if(m===11||(m===0&&d<=6))return 'navidad';
    return 'normal';
  }
  function isHalloween(search,date){return season(search,date)==='halloween';}
  function isNavidad(search,date){return season(search,date)==='navidad';}
  function halo(ctx,x,y,time){
    ctx.save();x=Math.round(x);y=Math.round(y);
    const pulse=1+Math.sin(time*3.5)*.045,phase=Math.floor(time*10)%48;
    for(let i=0;i<48;i++){
      const a=i/48*Math.PI*2,px=Math.round(x+Math.cos(a)*21*pulse),py=Math.round(y+Math.sin(a)*7*pulse);
      ctx.fillStyle='#57304e';ctx.globalAlpha=.45;ctx.fillRect(px-1,py-1,3,3);
      ctx.globalAlpha=.8;ctx.fillStyle=(i+phase)%16<3?'#fff0b8':'#ff4aab';ctx.fillRect(px,py,2,1);
    }
    ctx.restore();
  }
  // Gorro de Papá Noel: c = color del gorro, b = borde y pompón.
  function santaHat(r,k,c,shade,b,dx){
    dx=dx||0;
    r(dx-15,-1,30,6,k);r(dx-13,0,26,4,b);r(dx-11,1,3,2,'#ffffff');r(dx+4,1,3,2,'#ffffff');
    r(dx-11,-8,22,8,k);r(dx-9,-7,18,7,c);r(dx+3,-7,6,7,shade);
    r(dx-6,-14,15,7,k);r(dx-4,-13,11,7,c);r(dx+4,-13,3,6,shade);
    r(dx+2,-19,12,6,k);r(dx+4,-18,8,5,c);
    r(dx+11,-21,9,9,k);r(dx+12,-20,7,7,b);r(dx+13,-19,2,2,'#ffffff');
  }
  function accessoryNavidad(r,id,k){
    if(id==='boss'){
      santaHat(r,k,'#d8343c','#a71f2c','#f4f1ea');
    }else if(id==='manager'){
      // Cachos de reno (Rodolfo): no tapan la cara.
      for(const side of [-1,1]){
        const dx=side*9;
        r(dx-2,-8,5,10,k);r(dx-1,-7,3,9,'#9a6236');
        r(dx+side*2-2,-14,5,8,k);r(dx+side*2-1,-13,3,7,'#b07440');
        r(dx+side*5-2,-12,6,4,k);r(dx+side*5-1,-11,4,2,'#b07440');
        r(dx-side*1-2,-19,5,7,k);r(dx-side*1-1,-18,3,6,'#b07440');
      }
      r(-12,-1,24,4,k);r(-11,0,22,2,'#d8343c');r(-1,-1,3,4,'#f2c94c');
    }else if(id==='mate'){
      // Gorro de duende verde con cascabel.
      r(-16,0,32,5,k);r(-14,1,28,3,'#d8343c');for(let i=0;i<5;i++)r(-13+i*6,1,2,3,'#f4f1ea');
      r(-10,-7,20,8,k);r(-8,-6,16,7,'#2f9e55');r(2,-6,5,7,'#237a42');
      r(-5,-14,13,8,k);r(-3,-13,9,8,'#2f9e55');r(3,-13,3,7,'#237a42');
      r(1,-20,12,7,k);r(3,-19,8,6,'#36b062');
      r(10,-22,9,7,k);r(11,-21,6,5,'#36b062');
      r(16,-19,7,7,k);r(17,-18,5,5,'#f2c94c');r(18,-17,2,2,'#fff6c8');
    }else if(id==='cleaner'){
      // Moño rojo con cintas, de lado (como la calavera de Halloween).
      r(6,1,15,9,k);r(7,2,5,7,'#d8343c');r(15,2,5,7,'#d8343c');r(11,3,5,5,k);r(12,4,3,3,'#f2c94c');
      r(9,9,3,4,k);r(10,9,1,3,'#a71f2c');r(15,9,3,4,k);r(16,9,1,3,'#a71f2c');
    }else if(id==='gossip'){
      // Gorro de lana a rayas con pompón.
      r(-14,2,28,5,k);r(-12,3,24,3,'#f4f1ea');
      r(-12,-6,24,9,k);r(-10,-5,20,8,'#2f9e55');r(-10,-2,20,2,'#d8343c');
      r(-7,-9,14,4,k);r(-5,-8,10,3,'#2f9e55');
      r(-4,-15,8,7,k);r(-3,-14,6,5,'#f4f1ea');
    }else if(id==='intern'){
      santaHat(r,k,'#2f9e55','#237a42','#f4f1ea',-1);
    }else{
      // Ramita de acebo con dos bolitas rojas: no oculta el afro ni los lentes.
      r(8,3,15,8,k);r(9,4,6,4,'#2f9e55');r(16,4,6,4,'#2f9e55');r(10,5,3,2,'#58c27d');r(18,5,3,2,'#58c27d');
      r(13,6,6,5,k);r(14,7,2,3,'#e23b44');r(17,7,2,3,'#e23b44');r(14,7,1,1,'#ffd6d6');
    }
  }
  function accessory(ctx,id,head,theme){
    const x=Math.round(head.x),y=Math.round(head.y),k='#241b2d';
    const r=(dx,dy,w,h,c)=>{ctx.fillStyle=c;ctx.fillRect(x+dx,y+dy,w,h);};
    if(theme==='navidad')return accessoryNavidad(r,id,k);
    if(id==='mate'){
      r(-17,0,34,4,k);r(-15,0,30,2,'#6c3b95');
      r(-10,-7,20,7,k);r(-8,-6,16,6,'#75469c');r(-8,-2,16,3,'#ed963a');
      r(-7,-14,13,8,k);r(-5,-13,9,8,'#70408f');
      r(-3,-21,10,9,k);r(-1,-20,6,8,'#8151a5');r(3,-23,10,4,k);r(5,-22,6,2,'#8151a5');r(2,-1,3,2,'#ffd76a');
    }else if(id==='boss'||id==='manager'){
      for(const side of [-1,1]){
        const dx=side*10;
        r(dx-3,-2,7,6,k);r(dx-2,-3,5,6,'#e44c48');r(dx+side-2,-7,5,5,k);r(dx+side-1,-7,3,5,'#f36654');r(dx+side*2-1,-10,3,4,k);r(dx+side*2,-9,1,3,'#ffb174');
      }
    }else if(id==='cleaner'){
      r(8,2,9,8,k);r(9,3,7,6,'#f0ebd9');r(10,4,1,2,k);r(13,4,1,2,k);r(9,9,2,2,'#f0ebd9');r(14,9,2,2,'#f0ebd9');
    }else if(id==='gossip'){
      for(const side of [-1,1]){const dx=side*11;r(dx-4,-3,8,6,k);r(dx-3,-6,6,5,k);r(dx-2,-8,3,4,k);r(dx-1,-5,2,3,'#a66e87');}
    }else if(id==='intern'){
      r(-12,-1,24,4,k);r(-10,-3,20,5,'#d77b34');r(-7,-8,14,6,k);r(-6,-7,12,5,'#e59442');r(-2,-11,4,4,'#648450');r(-4,-5,2,2,k);r(3,-5,2,2,k);r(-2,-2,5,1,k);
    }else{
      // Un broche de murciélago naranja: no oculta el afro ni los lentes.
      r(9,5,12,3,k);r(7,3,5,4,k);r(18,3,5,4,k);r(8,4,4,2,'#f3a940');r(18,4,4,2,'#f3a940');r(12,4,6,5,k);r(13,5,4,3,'#ed873d');r(13,4,1,1,'#fff0a0');r(16,4,1,1,'#fff0a0');
    }
  }
  function decorations(ctx,width,time,theme){
    ctx.save();
    const r=(x,y,w,h,c)=>{ctx.fillStyle=c;ctx.fillRect(x,y,w,h);};
    if(theme==='navidad'){
      // Banderines rojo, verde y dorado sobre la pared.
      const colors=['#d8343c','#2f9e55','#e8b840'];
      for(let i=0;i<16;i++){
        const x=42+i*44,y=36+Math.round(Math.sin(i*.6)*2);
        r(x,y,19,1,'#51404f');
        for(let j=0;j<6;j++)r(x+3+j,y+1+j,12-j*2,1,colors[i%3]);
      }
      // Medias navideñas colgadas en las dos paredes laterales.
      for(const x of [19,width-29]){
        const y=380+Math.round(Math.sin(time*2+x)*1);  // abajo, para no tapar el agua ni el tablón
        r(x+3,y-3,1,3,'#51404f');
        r(x,y,10,4,'#f4f1ea');r(x+1,y+4,8,9,'#d8343c');r(x+1,y+11,12,5,'#d8343c');r(x+9,y+12,4,3,'#a71f2c');
        r(x+3,y+6,2,2,'#2f9e55');r(x+5,y+9,2,2,'#e8b840');
      }
      ctx.restore();return;
    }
    // Banderines sobre la pared; los pasillos y colisiones permanecen libres.
    for(let i=0;i<16;i++){
      const x=42+i*44,y=36+Math.round(Math.sin(i*.6)*2);
      r(x,y,19,1,'#51404f');
      for(let j=0;j<6;j++)r(x+3+j,y+1+j,12-j*2,1,i%2?'#ad75ce':'#ee9c42');
    }
    // Fantasmas de papel en las dos paredes laterales.
    for(const x of [20,width-28]){
      const y=285+Math.round(Math.sin(time*2+x)*2);
      r(x+2,y,9,2,'#ded9e7');r(x,y+2,13,10,'#f5f0e5');r(x+1,y+12,3,3,'#f5f0e5');r(x+8,y+12,3,3,'#f5f0e5');r(x+3,y+4,2,3,'#3a2c44');r(x+8,y+4,2,3,'#3a2c44');
    }
    ctx.restore();
  }
  root.SpriteSeasonal={season,isHalloween,isNavidad,halo,accessory,decorations};
})(typeof globalThis!=='undefined'?globalThis:window);
