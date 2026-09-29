// requires: environments/RoomEnvironment, geometries/RoundedBoxGeometry
let S;
async function setupPrizes(){
  await waitFonts();const s=makeRenderer('prizes-gl',[.25,.45,.9]);
  s.R.toneMapping=THREE.ACESFilmicToneMapping;s.R.toneMappingExposure=.82;
  s.scene.background=new THREE.Color(0x05070b);s.scene.fog=new THREE.FogExp2(0x05070b,.024);
  const pm=new THREE.PMREMGenerator(s.R),room=new THREE.RoomEnvironment();s.env=pm.fromScene(room,.035);s.scene.environment=s.env.texture;if(room.dispose)room.dispose();pm.dispose();
  const gold=new THREE.MeshStandardMaterial({color:0xe9c46a,metalness:1,roughness:.22,envMapIntensity:1.3});
  const dark=new THREE.MeshStandardMaterial({color:0x0b1725,metalness:.65,roughness:.3});
  const key=new THREE.DirectionalLight(0xffe5bd,2.4);key.position.set(-4,7,6);s.scene.add(key);
  s.rim=new THREE.PointLight(0x7fd8ff,35,28,2);s.rim.position.set(4,5,-2);s.scene.add(s.rim);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(70,70),dark);floor.rotation.x=-Math.PI/2;floor.position.y=-2.4;s.scene.add(floor);
  // A sculptural film aperture: eight solid, twisting golden blades surround an open centre.
  s.trophy=new THREE.Group();s.trophy.position.set(-3.65,-.1,.4);s.scene.add(s.trophy);
  const base=new THREE.Mesh(new THREE.CylinderGeometry(1.18,1.35,.34,64),dark);base.position.y=-1.68;s.trophy.add(base);
  const foot=new THREE.Mesh(new THREE.CylinderGeometry(.94,1.08,.12,64),gold);foot.position.y=-1.46;s.trophy.add(foot);
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(.13,.32,1.5,24),gold);stem.position.y=-.68;s.trophy.add(stem);
  s.crown=new THREE.Group();s.crown.position.y=1.13;s.trophy.add(s.crown);
  const bladeShape=new THREE.Shape();bladeShape.moveTo(.7,-.26);bladeShape.bezierCurveTo(1.1,-.5,1.55,-.3,1.69,.27);bladeShape.lineTo(1.32,.6);bladeShape.bezierCurveTo(1.22,.13,.85,.06,.7,.11);bladeShape.closePath();
  const bladeGeo=new THREE.ExtrudeGeometry(bladeShape,{depth:.22,bevelEnabled:true,bevelThickness:.045,bevelSize:.045,bevelSegments:3,steps:1,curveSegments:16});
  for(let i=0;i<8;i++){const blade=new THREE.Mesh(bladeGeo,gold);blade.rotation.z=i*Math.PI/4;blade.rotation.y=.13;s.crown.add(blade);}
  const core=new THREE.Mesh(new THREE.TorusGeometry(.61,.033,12,80),gold);core.position.z=.12;s.crown.add(core);
  const plateGeo=new THREE.RoundedBoxGeometry(2.9,2.25,.16,3,.09);
  const insetGeo=new THREE.PlaneGeometry(2.65,2.0);
  const homes=[[.5,1.7,-.25],[4.05,1.7,-.55],[.5,-1.0,.05],[4.05,-1.0,-.25]];
  s.plates=homes.map((home,i)=>{
    const g=new THREE.Group();s.scene.add(g);g.add(new THREE.Mesh(plateGeo,gold));
    const face=new THREE.Mesh(insetGeo,dark);face.position.z=.085;g.add(face);
    // Small embossed category emblems, with the lower half left clear for sharp labels.
    const icon=new THREE.Group();icon.position.set(0,.45,.14);g.add(icon);
    if(i===0){const eye=new THREE.Mesh(new THREE.TorusGeometry(.34,.026,8,48),gold);eye.scale.y=.62;icon.add(eye);icon.add(new THREE.Mesh(new THREE.SphereGeometry(.095,16,12),gold));}
    if(i===1){for(let j=0;j<3;j++){const m=new THREE.Mesh(new THREE.BoxGeometry(.31,.41,.045),gold);m.position.x=(j-1)*.22;m.position.z=j*.05;m.rotation.z=(j-1)*-.2;icon.add(m);}}
    if(i===2){const m=new THREE.Mesh(new THREE.TorusGeometry(.27,.027,8,48),gold);icon.add(m);const bar=new THREE.Mesh(new THREE.BoxGeometry(.7,.025,.04),gold);icon.add(bar);const v=bar.clone();v.rotation.z=Math.PI/2;icon.add(v);}
    if(i===3){const m=new THREE.Mesh(new THREE.ConeGeometry(.27,.5,3),gold);m.rotation.z=-Math.PI/2;icon.add(m);for(let j=0;j<2;j++){const arc=new THREE.Mesh(new THREE.TorusGeometry(.38+j*.13,.017,6,32,1.4),gold);arc.rotation.z=-.7;icon.add(arc);}}
    return {g,home,anchor:new THREE.Vector3(0,-.43,.12)};
  });
  const geo=new THREE.BufferGeometry(),pos=new Float32Array(650*3);for(let i=0;i<650;i++){pos[i*3]=(rnd(i)-.5)*23;pos[i*3+1]=rnd(i+710)*10-3;pos[i*3+2]=-rnd(i+1900)*14;}
  geo.setAttribute('position',new THREE.BufferAttribute(pos,3));s.dust=new THREE.Points(geo,new THREE.PointsMaterial({size:.036,map:dotTex('255,212,133'),color:0xe9c46a,transparent:true,opacity:.5,depthWrite:false}));s.scene.add(s.dust);
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  return s;
}
function prizeLabel(id,v,opacity,cam){v.project(cam);const e=el(id);e.style.left=(v.x*.5+.5)*1280+'px';e.style.top=(-v.y*.5+.5)*720+'px';e.style.opacity=opacity;}
async function render(frame,totalFrames,fps){
  const t=frame/fps;if(!S)S=setupPrizes();const s=await S,p=ease(seg(t,0,D));
  s.cam.position.set(lerp(-.8,.3,p),lerp(2.1,1.4,p),lerp(16.8,18.1,p));s.cam.lookAt(.15,.2,0);
  // The trophy is established before its spoken name; the four plates enter only on their cues.
  s.trophy.rotation.y=lerp(-.3,.14,p);s.crown.rotation.z=lerp(-.13,.08,p);
  s.rim.position.x=lerp(-2,5,p);s.dust.rotation.y=p*.16;
  s.plates.forEach(({g,home},i)=>{const a=easeOut(seg(t,C[i+1],C[i+1]+Math.min(.48,(D-C[i+1])*.3)));g.visible=t>=C[i+1];g.position.set(home[0]+(1-a)*1.0,home[1]-(1-a)*.45,home[2]-(1-a)*3);g.rotation.y=(1-a)*-.6;});
  s.composer.render();
  prizeLabel('prizes-grand',s.trophy.localToWorld(new THREE.Vector3(0,-2.18,.3)),seg(t,C[0],C[0]+.28),s.cam);
  s.plates.forEach(({g,anchor},i)=>prizeLabel('prizes-'+i,g.localToWorld(anchor.clone()),seg(t,C[i+1],C[i+1]+.32),s.cam));
  el('prizes-top').style.opacity=seg(t,0,C[0]*.45);
  beatFade(t,D,.2,.25);
}
