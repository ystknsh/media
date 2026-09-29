// requires: environments/RoomEnvironment, geometries/RoundedBoxGeometry
let S;
async function setupJudge(){
  await waitFonts();const s=makeRenderer('judge-gl',[.16,.45,1.1]);
  s.R.toneMapping=THREE.ACESFilmicToneMapping;s.R.toneMappingExposure=.75;
  s.scene.background=new THREE.Color(0x05070b);s.scene.fog=new THREE.FogExp2(0x05070b,.03);
  const pm=new THREE.PMREMGenerator(s.R),room=new THREE.RoomEnvironment();s.env=pm.fromScene(room,.04);s.scene.environment=s.env.texture;if(room.dispose)room.dispose();pm.dispose();
  const gold=new THREE.MeshStandardMaterial({color:0xe9c46a,metalness:.95,roughness:.28});
  const slate=new THREE.MeshStandardMaterial({color:0x0b1825,metalness:.45,roughness:.42});
  const key=new THREE.DirectionalLight(0xffdfa9,1.8);key.position.set(-3,7,5);s.scene.add(key);
  s.rim=new THREE.PointLight(0x7fd8ff,28,20,2);s.rim.position.set(6,3,-2);s.scene.add(s.rim);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(70,70),slate);floor.rotation.x=-Math.PI/2;floor.position.y=-2.6;s.scene.add(floor);
  // Load via the rewritten HTML src. The uncropped photograph has its native aspect ratio.
  const texture=await new THREE.TextureLoader().loadAsync(el('judge-source').src);texture.anisotropy=Math.min(4,s.R.capabilities.getMaxAnisotropy());
  const w=7.65,h=w*texture.image.height/texture.image.width;
  s.portrait=new THREE.Group();s.portrait.position.set(3.0,.6,0);s.portrait.rotation.y=-.045;s.scene.add(s.portrait);
  const backing=new THREE.Mesh(new THREE.RoundedBoxGeometry(w+.22,h+.22,.18,3,.06),gold);s.portrait.add(backing);
  const mount=new THREE.Mesh(new THREE.BoxGeometry(w+.12,h+.12,.035),slate);mount.position.z=.107;s.portrait.add(mount);
  const photo=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:texture,toneMapped:false,fog:false}));photo.position.z=.13;s.portrait.add(photo);
  // Architectural frames recede behind the portrait; they give the modest dolly real parallax.
  const barGeo=new THREE.BoxGeometry(.045,8,.09),topGeo=new THREE.BoxGeometry(18,.045,.09);
  for(let i=0;i<6;i++){
    const group=new THREE.Group();group.position.set(.6,1,-2.2-i*2.2);s.scene.add(group);
    [-9,9].forEach(x=>{const bar=new THREE.Mesh(barGeo,gold);bar.position.x=x;group.add(bar);});
    const top=new THREE.Mesh(topGeo,gold);top.position.y=4;group.add(top);
    const low=new THREE.Mesh(new THREE.BoxGeometry(18,.025,.055),gold);low.position.y=-3.5;group.add(low);
  }
  // A grounded plinth beneath the floating exhibition print.
  const plinth=new THREE.Mesh(new THREE.BoxGeometry(w+.5,.16,1.15),slate);plinth.position.set(3,-2.46,-.08);s.scene.add(plinth);
  const trim=new THREE.Mesh(new THREE.BoxGeometry(w+.5,.025,1.17),gold);trim.position.set(3,-2.37,-.08);s.scene.add(trim);
  const positions=new Float32Array(280*3);for(let i=0;i<280;i++){positions[i*3]=(rnd(i)-.5)*23;positions[i*3+1]=rnd(i+401)*11-3;positions[i*3+2]=-3-rnd(i+901)*17;}
  const dustGeo=new THREE.BufferGeometry();dustGeo.setAttribute('position',new THREE.BufferAttribute(positions,3));s.dust=new THREE.Points(dustGeo,new THREE.PointsMaterial({color:0xd1b57b,map:dotTex('233,196,106'),size:.04,transparent:true,opacity:.28,depthWrite:false}));s.scene.add(s.dust);
  // Linear compositor output is encoded once; the photo bypasses tone mapping and bloom.
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  return s;
}
async function render(frame,totalFrames,fps){
  const t=frame/fps;if(!S)S=setupJudge();const s=await S,p=ease(seg(t,0,D));
  s.cam.position.set(lerp(.55,-.12,p),lerp(1.15,.85,p),lerp(16.8,16.0,p));s.cam.lookAt(.15,.25,0);
  s.dust.position.y=p*.18;s.dust.rotation.y=p*.025;s.rim.position.x=lerp(6,4,p);s.composer.render();
  const role=easeOut(seg(t,C[0],C[0]+.32)),name=easeOut(seg(t,C[1],C[1]+.38)),society=easeOut(seg(t,C[2],C[2]+.32));
  el('judge-role').style.opacity=role;el('judge-rule').style.transform=`scaleX(${role})`;
  el('judge-name').style.opacity=name;el('judge-name').style.transform=`translateY(${(1-name)*12}px)`;
  el('judge-society').style.opacity=society;el('judge-society').style.transform=`translateY(${(1-society)*8}px)`;
  el('judge-footer').style.opacity=role*.8;
  beatFade(t,D,.2,.25);
}
