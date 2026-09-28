// requires: environments/RoomEnvironment
let S;
async function setupOpen(){
  await waitFonts();
  const s=makeRenderer('open-space',[1.1,.55,.35]);
  s.scene.background=new THREE.Color('#05070b'); s.scene.fog=new THREE.FogExp2('#05070b',.018);
  const env=new THREE.PMREMGenerator(s.R), room=new THREE.RoomEnvironment();
  s.env=env.fromScene(room,.04);s.scene.environment=s.env.texture;room.dispose();env.dispose();
  s.cam.fov=38;s.cam.updateProjectionMatrix();
  const targets=textTargets('Imagine',"italic 310px 'Instrument Serif'",1600,420,3);
  const N=24000,pos=new Float32Array(N*3),col=new Float32Array(N*3);
  s.word=[];s.screen=[];
  for(let i=0;i<N;i++){
    const p=targets[Math.floor(rnd(i+12)*targets.length)];
    s.word.push([(p[0]-800)/76,(210-p[1])/76+.6,(rnd(i+22)-.5)*.22]);
    let x,y;const u=rnd(i+42);
    if(i%5===0){const a=rnd(i+71),b=rnd(i+81)*(1-a);x=-.48+a*1.4;y=-.85+b*1.7+a*.85;}
    else {const d=u*40;if(d<12.8){x=-6.4+d;y=3.6;}else if(d<20){x=6.4;y=3.6-(d-12.8);}else if(d<32.8){x=6.4-(d-20);y=-3.6;}else{x=-6.4;y=-3.6+d-32.8;}}
    s.screen.push([x,y+.5,(rnd(i+91)-.5)*.14]);
    // mostly warm gold, with violet and cyan threads so the cloud reads as a nebula
    const k=rnd(i+7),c=k<.7?new THREE.Color().setRGB(1,.62+rnd(i+2)*.3,.25+rnd(i+3)*.3):k<.85?new THREE.Color().setRGB(.62,.42,1):new THREE.Color().setRGB(.45,.85,1);c.toArray(col,i*3);
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(pos,3));g.setAttribute('color',new THREE.BufferAttribute(col,3));
  const mat=new THREE.PointsMaterial({size:.15,map:dotTex('255,219,155'),transparent:true,vertexColors:true,depthWrite:false,blending:THREE.AdditiveBlending});
  const points=new THREE.Points(g,mat);points.frustumCulled=false;s.scene.add(points);s.pos=pos;s.g=g;s.points=points;
  const dustPos=new Float32Array(1800*3);
  for(let i=0;i<1800;i++){dustPos[i*3]=(rnd(i+100)-.5)*44;dustPos[i*3+1]=(rnd(i+200)-.5)*25;dustPos[i*3+2]=(rnd(i+300)-.5)*38;}
  const dg=new THREE.BufferGeometry();dg.setAttribute('position',new THREE.BufferAttribute(dustPos,3));
  s.dust=new THREE.Points(dg,new THREE.PointsMaterial({size:.045,color:0xcda870,map:dotTex('255,209,135'),transparent:true,opacity:.38,depthWrite:false}));s.scene.add(s.dust);
  s.panel=new THREE.Mesh(new THREE.BoxGeometry(12.75,7.15,.08),new THREE.MeshStandardMaterial({color:0x0b1925,metalness:.65,roughness:.3,transparent:true,opacity:0}));
  s.panel.position.set(0,.5,-.15);s.scene.add(s.panel);
  s.scene.add(new THREE.HemisphereLight(0x91cfff,0x2e1708,.4));
  return s;
}
async function render(frame,totalFrames,fps){
  const t=frame/fps;if(!S)S=setupOpen();const s=await S;
  const u=seg(t,0,D),a=ease(seg(t,C[0],C[1])),b=ease(seg(t,C[2],C[2]+(C[3]-C[2])*.46));
  for(let i=0;i<s.word.length;i++){
    const angle=rnd(i+4)*Math.PI*2+u*.65,rad=2+Math.pow(rnd(i+5),.65)*13;
    const cloud=[Math.cos(angle)*rad,Math.sin(angle)*rad*.43,(rnd(i+6)-.5)*14];
    for(let j=0;j<3;j++)s.pos[i*3+j]=lerp(lerp(cloud[j],s.word[i][j],a),s.screen[i][j],b);
  }
  s.g.attributes.position.needsUpdate=true;s.panel.material.opacity=b*.72;
  s.cam.position.set(lerp(2.0,-.6,u),lerp(1.0,.5,u),lerp(21,18.5,u));s.cam.lookAt(0,.1,0);
  s.dust.rotation.y=u*.12;
  el('open-eyebrow').style.opacity=seg(t,C[0],C[0]+.3)*.8;
  el('open-caption').textContent=t<C[2]?'and you can see it.':'When AI can make movies…';
  el('open-caption').style.opacity=seg(t,C[1],C[1]+.25)*(1-seg(t,C[3]-.2,C[3]));
  el('open-question').style.opacity=seg(t,C[3],C[3]+.25);
  s.composer.render();beatFade(t,D,.2,.25);
}
