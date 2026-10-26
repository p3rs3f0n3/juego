/* Accesorios pixel art, halo de la protagonista y decoración de temporada. */
(function(root){
  'use strict';
  function isHalloween(search,date){
    const value=new URLSearchParams(search||'').get('tema');
    if(value==='normal')return false;if(value==='halloween')return true;
    date=date||new Date();const m=date.getMonth(),d=date.getDate();
    return (m===9&&d>=23)||(m===10&&d<=1);
  }
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
  function accessory(ctx,id,head){
    const x=Math.round(head.x),y=Math.round(head.y),k='#241b2d';
    const r=(dx,dy,w,h,c)=>{ctx.fillStyle=c;ctx.fillRect(x+dx,y+dy,w,h);};
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
  function decorations(ctx,width,time){
    ctx.save();
    const r=(x,y,w,h,c)=>{ctx.fillStyle=c;ctx.fillRect(x,y,w,h);};
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
  root.SpriteSeasonal={isHalloween,halo,accessory,decorations};
})(typeof globalThis!=='undefined'?globalThis:window);
