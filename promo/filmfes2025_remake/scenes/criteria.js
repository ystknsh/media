// requires: environments/RoomEnvironment
let S;
async function setupCriteria() {
  const s = makeRenderer('criteria-gl', [.3,.5,1.08]);
  s.scene.background = new THREE.Color(0x05070b);
  s.scene.fog = new THREE.FogExp2(0x05070b,.032);
  s.R.toneMapping = THREE.ACESFilmicToneMapping; s.R.toneMappingExposure = .83;
  const pm = new THREE.PMREMGenerator(s.R), room = new THREE.RoomEnvironment();
  s.env = pm.fromScene(room,.04); s.scene.environment = s.env.texture; room.dispose(); pm.dispose();
  const gold = new THREE.MeshStandardMaterial({color:0xe9c46a,metalness:.94,roughness:.26});
  const dark = new THREE.MeshStandardMaterial({color:0x14212b,metalness:.78,roughness:.34});
  const key = new THREE.DirectionalLight(0xffdfad,2.5); key.position.set(-4,7,6); s.scene.add(key);
  const rim = new THREE.PointLight(0x7fd8ff,14,22,2); rim.position.set(6,3,-3); s.scene.add(rim);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshStandardMaterial({color:0x080d14,metalness:.4,roughness:.42}));
  floor.rotation.x = -Math.PI/2; floor.position.y = -3.45; s.scene.add(floor);
  s.instrument = new THREE.Group(); s.instrument.position.set(4.1,-.05,0); s.scene.add(s.instrument);
  function mesh(geometry,material,parent=s.instrument,x=0,y=0,z=0) {
    const m = new THREE.Mesh(geometry,material); m.position.set(x,y,z); parent.add(m); return m;
  }
  mesh(new THREE.CylinderGeometry(2.35,2.55,.3,80),dark,s.instrument,0,-3.23,0);
  mesh(new THREE.CylinderGeometry(1.92,2.1,.12,80),gold,s.instrument,0,-3.01,0);
  mesh(new THREE.CylinderGeometry(.14,.24,.53,24),gold,s.instrument,0,-2.73,0);
  // A single physical armature; each spoken criterion completes another component.
  const outer = mesh(new THREE.TorusGeometry(2.62,.065,12,160),dark); outer.rotation.y = -.18;
  s.parts = Array.from({length:4},()=>{const g=new THREE.Group();s.instrument.add(g);return g;});
  mesh(new THREE.TorusKnotGeometry(1.85,.046,240,8,2,3),gold,s.parts[0]).scale.set(1.16,1.16,.73);
  for(let i=0;i<3;i++) {
    const ring=mesh(new THREE.TorusGeometry(2.33,.032,8,128),gold,s.parts[1]);
    ring.rotation.set(i*Math.PI/3,Math.PI/2+i*.3,.25);
  }
  const pinGeo = new THREE.SphereGeometry(.085,12,8);
  for(let i=0;i<8;i++) {
    const a=i*Math.PI/4;
    mesh(pinGeo,gold,s.parts[1],2.33*Math.cos(a),2.33*Math.sin(a),0);
  }
  s.collar = s.parts[2]; s.collar.rotation.y = -.18;
  mesh(new THREE.TorusGeometry(2.66,.038,8,160),gold,s.collar);
  const ticks = new THREE.InstancedMesh(new THREE.BoxGeometry(.025,.13,.09),gold,100), dummy=new THREE.Object3D();
  for(let i=0;i<100;i++) {
    const a=i/100*Math.PI*2; dummy.position.set(Math.sin(a)*2.78,Math.cos(a)*2.78,0);
    dummy.rotation.z=-a; dummy.scale.set(1,i%5===0?1.7:1,1); dummy.updateMatrix(); ticks.setMatrixAt(i,dummy.matrix);
  }
  s.collar.add(ticks);
  // A fictitious, code-sculpted world: blue ocean, raised ochre continents, tiny mountain ridges.
  const geo = new THREE.SphereGeometry(1.48,112,64), p=geo.attributes.position, colors=[];
  const sea = new THREE.Color(0x153f53), land = new THREE.Color(0xa99760), peak = new THREE.Color(0xe1cc93);
  for(let i=0;i<p.count;i++) {
    const v=new THREE.Vector3().fromBufferAttribute(p,i).normalize();
    const n=Math.sin(v.x*5+v.z*2)*Math.cos(v.y*6-v.x)+.46*Math.sin(v.z*9+v.y*3)+.18*Math.cos(v.x*18+v.z*14);
    const h=Math.max(0,n-.23), r=1.48+h*.14; p.setXYZ(i,v.x*r,v.y*r,v.z*r);
    const c=n>.23?land.clone().lerp(peak,Math.min(1,h)):sea; colors.push(c.r,c.g,c.b);
  }
  geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3)); geo.computeVertexNormals();
  s.world=mesh(geo,new THREE.MeshStandardMaterial({vertexColors:true,metalness:.38,roughness:.48}),s.parts[3]);
  const halo=mesh(new THREE.TorusGeometry(1.72,.012,8,128),new THREE.MeshBasicMaterial({color:0x7fd8ff}),s.parts[3]);
  halo.rotation.set(.32,.4,-.3);
  const pos = new Float32Array(900*3);
  for(let i=0;i<900;i++){pos[i*3]=(rnd(i*3)-.5)*24;pos[i*3+1]=(rnd(i*3+1)-.5)*15;pos[i*3+2]=(rnd(i*3+2)-.5)*20;}
  const dustgeo=new THREE.BufferGeometry();dustgeo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  s.dust=new THREE.Points(dustgeo,new THREE.PointsMaterial({color:0xc5ad78,map:dotTex('233,196,106'),size:.033,transparent:true,opacity:.4,depthWrite:false}));s.scene.add(s.dust);
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  return s;
}
async function render(frame,totalFrames,fps) {
  const t=frame/fps,u=seg(t,0,D); if(!S)S=setupCriteria();const s=await S;
  const complete=ease(seg(t,C[3],D));
  s.cam.position.set(lerp(.9,-.35,u),lerp(1.1,.55,u),lerp(18.7,17.5,u));s.cam.lookAt(.55,-.05,0);
  s.instrument.rotation.y=lerp(-.26,.12,u);
  s.parts.forEach((part,i)=>{
    const k=easeOut(seg(t,C[i],C[i]+Math.min(.65,(D-C[i])*.2)));
    part.visible=k>0;part.scale.setScalar(.8+.2*k);part.position.y=(1-k)*.7;
    const label=el('criterion-'+i);label.style.opacity=k;label.style.transform=`translateX(${(1-k)*-14}px)`;
    label.style.color=i===3?'#f4ebd9':(t>=(C[i+1]??D)?'#b7b5ae':'#f4ebd9');
  });
  s.parts[0].rotation.set(.1+u*.2,u*.5,-.3+u*.25);
  s.parts[1].rotation.y=u*.45;
  s.collar.rotation.z=-u*.24;
  s.world.rotation.y=complete*.5;
  s.dust.rotation.y=u*.08;s.dust.position.y=u*.3;
  el('criteria-ai').style.opacity=seg(t,C[3]+(D-C[3])*.15,C[3]+(D-C[3])*.28);
  s.composer.render();beatFade(t,D,0.2,0.25);
}
