// requires: environments/RoomEnvironment, geometries/RoundedBoxGeometry
let S;
async function setupDates() {
  await waitFonts();
  const s=makeRenderer('dates-gl',[.19,.35,1.12]);
  s.R.toneMapping=THREE.ACESFilmicToneMapping;s.R.toneMappingExposure=.8;
  s.scene.background=new THREE.Color(0x05070b);s.scene.fog=new THREE.FogExp2(0x05070b,.026);
  const pm=new THREE.PMREMGenerator(s.R),room=new THREE.RoomEnvironment();
  s.env=pm.fromScene(room,.04);s.scene.environment=s.env.texture;room.dispose();pm.dispose();
  const metal=new THREE.MeshStandardMaterial({color:0x253039,metalness:.85,roughness:.32});
  const black=new THREE.MeshStandardMaterial({color:0x080c11,metalness:.3,roughness:.58});
  const brass=new THREE.MeshStandardMaterial({color:0xcba761,metalness:.87,roughness:.28});
  const light=new THREE.DirectionalLight(0xffdfae,2.4);light.position.set(-5,8,9);s.scene.add(light);
  const blue=new THREE.PointLight(0x7fd8ff,20,30,2);blue.position.set(8,4,3);s.scene.add(blue);
  s.board=new THREE.Group();s.scene.add(s.board);
  function mesh(geo,mat,x,y,z,parent=s.board){const m=new THREE.Mesh(geo,mat);m.position.set(x,y,z);parent.add(m);return m;}
  mesh(new THREE.RoundedBoxGeometry(15.1,6.45,.65,3,.16),metal,0,0,-.25);
  mesh(new THREE.RoundedBoxGeometry(14.75,6.08,.16,2,.08),black,0,0,.11);
  for(const y of [-3.11,3.11])mesh(new THREE.BoxGeometry(14.45,.024,.025),brass,0,y,.16);
  for(const x of [-7.16,7.16])for(const y of [-2.85,2.85]) {
    const screw=mesh(new THREE.CylinderGeometry(.075,.075,.035,12),brass,x,y,.24);screw.rotation.x=Math.PI/2;
    mesh(new THREE.BoxGeometry(.067,.012,.008),black,x,y,.263);
  }
  // The headings are attached to the cabinet, so the camera move preserves the physical perspective.
  function plate(text,w,h,x,y,color) {
    const c=document.createElement('canvas');c.width=1536;c.height=128;
    const g=c.getContext('2d');g.clearRect(0,0,c.width,c.height);g.fillStyle=color;
    g.font="600 63px 'JetBrains Mono'";g.textBaseline='middle';g.fillText(text,8,64);
    const tx=new THREE.CanvasTexture(c);tx.anisotropy=4;
    return mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:tx,transparent:true,depthWrite:false,toneMapped:false}),x,y,.225);
  }
  plate('ENTRIES CLOSE',12.9,1.075,0,2.43,'#9c8555');
  plate('WINNERS ANNOUNCED',12.9,1.075,0,-.05,'#9c8555');
  // Cache a full glyph, then expose its real upper/lower texture halves on independently hinged leaves.
  s.glyph={};
  for(const char of ' X.ONLIE—/') {
    if(s.glyph[char])continue;
    const c=document.createElement('canvas');c.width=256;c.height=336;const g=c.getContext('2d');
    g.fillStyle='#10171e';g.fillRect(0,0,256,336);
    const gr=g.createLinearGradient(0,0,0,336);gr.addColorStop(0,'#ffffff0c');gr.addColorStop(1,'#00000022');g.fillStyle=gr;g.fillRect(0,0,256,336);
    g.fillStyle='#b7bdba';g.font="600 258px 'JetBrains Mono'";g.textAlign='center';g.textBaseline='middle';g.fillText(char,128,174);
    s.glyph[char]=[true,false].map(top=>{
      const tex=new THREE.CanvasTexture(c);tex.repeat.set(1,.5);tex.offset.y=top?.5:0;tex.anisotropy=4;
      return new THREE.MeshBasicMaterial({map:tex,toneMapped:false});
    });
  }
  const half=new THREE.PlaneGeometry(.985,.67), leaf=new THREE.BoxGeometry(1.005,.687,.036);
  const socket=new THREE.RoundedBoxGeometry(1.075,1.49,.18,2,.055);
  const hingeGeo=new THREE.CylinderGeometry(.032,.032,1.055,8);hingeGeo.rotateZ(Math.PI/2);
  s.cells=[];
  ['XX.XX','XX.XX ONLINE'].forEach((value,row)=>{
    [...value].forEach((char,col)=>{
      const x=-6.34+col*1.15,y=row===0?1.27:-1.21;
      const group=new THREE.Group();group.position.set(x,y,.26);s.board.add(group);
      mesh(socket,metal,0,0,0,group);
      const top=mesh(half,s.glyph[' '][0],0,.344,.12,group);
      const bottom=mesh(half,s.glyph[' '][1],0,-.344,.12,group);
      const pivot=new THREE.Group();pivot.position.z=.157;group.add(pivot);
      mesh(leaf,black,0,.344,0,pivot);
      const front=mesh(half,s.glyph[' '][0],0,.344,.021,pivot);
      const back=mesh(half,s.glyph[' '][1],0,.344,-.021,pivot);back.rotation.x=Math.PI;
      mesh(hingeGeo,brass,0,0,.195,group);
      s.cells.push({row,col,char,top,bottom,pivot,front,back});
    });
  });
  plate('SEND IN YOUR FILM',6.15,.512,3.34,1.2,'#50616b');
  // Ceiling mounts and a distant architectural wall keep the object in a real space.
  for(const x of [-5.7,5.7])mesh(new THREE.CylinderGeometry(.025,.025,9,8),metal,x,7.6,-.3,s.scene);
  mesh(new THREE.BoxGeometry(80,30,.4),new THREE.MeshStandardMaterial({color:0x020304,roughness:1}),0,1,-5,s.scene);  // the board's key light washed a lighter wall to grey-blue
  const pos=[];for(let i=0;i<450;i++)pos.push((rnd(i*3)-.5)*28,(rnd(i*3+1)-.5)*16,rnd(i*3+2)*12-5);
  const dg=new THREE.BufferGeometry();dg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  s.dust=new THREE.Points(dg,new THREE.PointsMaterial({color:0xd7bb7f,map:dotTex('220,198,150'),size:.024,transparent:true,opacity:.3,depthWrite:false}));s.scene.add(s.dust);
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  return s;
}
async function render(frame,totalFrames,fps) {
  const t=frame/fps,u=ease(seg(t,0,D));if(!S)S=setupDates();const s=await S;
  s.cam.position.set(lerp(2.4,.65,u),lerp(1.1,.32,u),lerp(20.5,18.6,u));s.cam.lookAt(0,.08,0);
  for(const c of s.cells) {
    const span=(c.row===0?C[1]-C[0]:D-C[1]);
    const start=C[c.row]+span*(.025+c.col*.009);
    const p=seg(t,start,start+span*.34),steps=3,step=Math.min(steps-1,Math.floor(p*steps)),phase=p>=1?1:(p*steps)%1;
    const seq=[' ','—',c.char==='.'?'/':'X',c.char];
    const old=seq[step],next=seq[step+1];
    c.top.material=s.glyph[next][0];c.bottom.material=s.glyph[old][1];
    c.front.material=s.glyph[old][0];c.back.material=s.glyph[next][1];
    c.pivot.rotation.x=Math.PI*easeIn(phase);
    if(t<start){c.top.material=s.glyph[' '][0];c.bottom.material=s.glyph[' '][1];c.front.material=s.glyph[' '][0];c.pivot.rotation.x=0;}
  }
  s.dust.position.x=u*.2;s.dust.position.y=u*.16;
  s.composer.render();beatFade(t,D,0.2,0.25);
}
