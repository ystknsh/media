// requires: environments/RoomEnvironment
let S;
async function setupRules() {
  await waitFonts();
  const s=makeRenderer('rules-gl',[.23,.5,.9]);
  s.R.toneMapping=THREE.ACESFilmicToneMapping; s.R.toneMappingExposure=.85;
  s.scene.background=new THREE.Color(0x05070b); s.scene.fog=new THREE.FogExp2(0x05070b,.027);
  const pm=new THREE.PMREMGenerator(s.R), room=new THREE.RoomEnvironment();
  s.env=pm.fromScene(room,.04); s.scene.environment=s.env.texture; if(room.dispose)room.dispose(); pm.dispose();
  const gold=new THREE.MeshStandardMaterial({color:0xe9c46a,metalness:.88,roughness:.26});
  const black=new THREE.MeshStandardMaterial({color:0x101923,metalness:.55,roughness:.32});
  const key=new THREE.DirectionalLight(0xffe0ab,2);key.position.set(-5,8,5);s.scene.add(key);
  const fill=new THREE.PointLight(0x7fd8ff,28,25,2);fill.position.set(5,4,3);s.scene.add(fill);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(90,90),black);floor.rotation.x=-Math.PI/2;floor.position.y=-2.2;s.scene.add(floor);
  s.gallery=new THREE.Group();s.scene.add(s.gallery);s.films=[];
  [-4.6,0,4.6].forEach((x,i)=>{
    const group=new THREE.Group();group.position.set(x,1,-1-Math.abs(x)*.13);group.rotation.y=-x*.045;
    const frame=new THREE.Mesh(new THREE.BoxGeometry(4.2,2.46,.18),gold);group.add(frame);
    const canvas=document.createElement('canvas');canvas.width=512;canvas.height=288;
    const tex=new THREE.CanvasTexture(canvas);
    const face=new THREE.Mesh(new THREE.PlaneGeometry(4.02,2.26),new THREE.MeshBasicMaterial({map:tex,toneMapped:false}));face.position.z=.101;group.add(face);
    s.gallery.add(group);s.films.push({canvas,tex,k:[0,4,2][i]});
    const stand=new THREE.Mesh(new THREE.CylinderGeometry(.035,.035,2.1,8),gold);stand.position.set(x,-1.15,group.position.z);s.gallery.add(stand);
  });
  s.clock=new THREE.Group();s.clock.position.set(0,1,.8);s.scene.add(s.clock);
  const dial=new THREE.Mesh(new THREE.CircleGeometry(1.76,80),black);dial.position.z=-.06;s.clock.add(dial);
  s.clock.add(new THREE.Mesh(new THREE.TorusGeometry(1.8,.085,12,120),gold));
  s.ticks=[];
  const tickGeo=new THREE.BoxGeometry(.035,.16,.04);
  for(let i=0;i<60;i++){
    const a=i/60*Math.PI*2, mat=new THREE.MeshStandardMaterial({color:0x263342,metalness:.6,roughness:.3,emissive:0xe9c46a,emissiveIntensity:0});
    const tick=new THREE.Mesh(tickGeo,mat);tick.position.set(Math.sin(a)*1.58,Math.cos(a)*1.58,.02);tick.rotation.z=-a;s.clock.add(tick);s.ticks.push(tick);
  }
  s.people=[];const heads=new THREE.SphereGeometry(.105,10,8),bodies=new THREE.CylinderGeometry(.115,.19,.44,10);
  for(let r=0;r<7;r++)for(let j=0;j<19;j++){
    const i=r*19+j, x=(j-9)*.62+(r%2)*.22,z=1.8-r*.76;
    const mat=new THREE.MeshStandardMaterial({color:0x1a2935,metalness:.25,roughness:.48,emissive:0x000000});
    const person=new THREE.Group();person.position.set(x,-2.2,z);
    const head=new THREE.Mesh(heads,mat);head.position.y=.72;person.add(head);
    const body=new THREE.Mesh(bodies,mat);body.position.y=.36;person.add(body);
    person.scale.y=.88+rnd(i+40)*.3;s.scene.add(person);s.people.push({person,mat,delay:(r/7*.6+rnd(i)*.25),warm:rnd(i+81)>.45});
  }
  const pos=new Float32Array(450*3);for(let i=0;i<450;i++){pos[i*3]=(rnd(i)-.5)*22;pos[i*3+1]=rnd(i+600)*10-2;pos[i*3+2]=-rnd(i+900)*15;}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  s.dust=new THREE.Points(geo,new THREE.PointsMaterial({color:0xe9c46a,size:.035,map:dotTex('233,196,106'),transparent:true,opacity:.42,depthWrite:false}));s.scene.add(s.dust);
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  return s;
}
async function render(frame,totalFrames,fps){
  const t=frame/fps;if(!S)S=setupRules();const s=await S,p=t/D;
  const clock=easeOut(seg(t,C[1],C[1]+(C[2]-C[1])*.23));
  const crowd=ease(seg(t,C[2],C[2]+(D-C[2])*.45));
  s.cam.position.set(lerp(.65,-.35,p),lerp(2.8,4.8,crowd),lerp(16,17.8,crowd));s.cam.lookAt(0,.15,-.5);
  s.gallery.position.set(0,clock*1.9,-clock*6);s.gallery.scale.setScalar(1-clock*.22);
  s.films.forEach(f=>{miniFilm(f.canvas.getContext('2d'),f.k,0,0,512,288,t/D*7);f.tex.needsUpdate=true;});
  s.clock.visible=t>=C[1]&&crowd<.99;s.clock.scale.setScalar(Math.max(.001,clock*(1-crowd*.7)));s.clock.rotation.y=(1-clock)*.7;
  s.ticks.forEach((m,i)=>{m.material.emissiveIntensity=clock>i/60?.65:0;});
  s.people.forEach(({person,mat,delay,warm})=>{
    const a=seg(t,C[2]+delay*(D-C[2])*.45,C[2]+(delay*.45+.2)*(D-C[2]));
    person.visible=t>=C[2];mat.color.setHex(warm?0xe9c46a:0x7fd8ff).multiplyScalar(lerp(.06,.7,a));mat.emissive.setHex(warm?0xe9c46a:0x7fd8ff);mat.emissiveIntensity=a*.32;
  });
  s.dust.rotation.y=p*.12;s.composer.render();
  const v=new THREE.Vector3(0,1,.82).project(s.cam);el('rules-clock').style.left=(v.x*.5+.5)*1280+'px';el('rules-clock').style.top=(-v.y*.5+.5)*720+'px';el('rules-clock').style.opacity=clock*(1-crowd);
  const phase=t<C[1]?0:t<C[2]?1:2;
  el('rules-title').textContent=['ANY GENRE','UP TO 3:00','OPEN TO EVERYONE'][phase];
  el('rules-index').textContent=['01 / THE POSSIBILITIES','02 / THE RUNNING TIME','03 / THE INVITATION'][phase];
  el('rules-sub').textContent=['YOUR FILM. YOUR VOICE.','THREE MINUTES OR LESS','EVERY STORY STARTS WITH SOMEONE'][phase];
  const a=easeOut(seg(t,C[phase],C[phase]+.22));el('rules-copy').style.opacity=a;el('rules-copy').style.transform=`translateY(${(1-a)*12}px)`;
  beatFade(t,D,.2,.25);
}
