// requires: environments/RoomEnvironment, geometries/RoundedBoxGeometry
let S;
function setupClose(){
  const s=makeRenderer('cl-world',[.35,.5,.95]);s.R.toneMapping=THREE.ACESFilmicToneMapping;s.R.toneMappingExposure=.78;
  s.cam.fov=43;s.cam.far=150;s.cam.updateProjectionMatrix();s.scene.background=new THREE.Color(0x03070c);s.scene.fog=new THREE.FogExp2(0x03070c,.023);
  const pm=new THREE.PMREMGenerator(s.R),room=new THREE.RoomEnvironment();s.env=pm.fromScene(room,.04);s.scene.environment=s.env.texture;room.dispose();pm.dispose();
  const gold=new THREE.MeshStandardMaterial({color:0xc7a767,roughness:.24,metalness:.88,envMapIntensity:.8});
  const dark=new THREE.MeshStandardMaterial({color:0x15202a,roughness:.28,metalness:.75,envMapIntensity:.65});
  const cyan=new THREE.MeshStandardMaterial({color:0x7fd8ff,emissive:0x7fd8ff,emissiveIntensity:1.5,roughness:.3,metalness:.3});
  const warm=new THREE.MeshStandardMaterial({color:0xe9c46a,emissive:0xe9c46a,emissiveIntensity:1.2,roughness:.25,metalness:.4});
  s.scene.add(new THREE.HemisphereLight(0x769ebc,0x181719,.8));
  const key=new THREE.PointLight(0x7fd8ff,7,24,2);key.position.set(0,6,3);s.scene.add(key);
  const rim=new THREE.PointLight(0xe9c46a,9,28,2);rim.position.set(-8,8,5);s.scene.add(rim);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(90,110),new THREE.MeshStandardMaterial({color:0x111d27,roughness:.22,metalness:.8}));floor.rotation.x=-Math.PI/2;floor.position.z=-15;s.scene.add(floor);
  function box(w,h,d,x,y,z,mat,rounded=false){const mesh=new THREE.Mesh(rounded?new THREE.RoundedBoxGeometry(w,h,d,2,.06):new THREE.BoxGeometry(w,h,d),mat);mesh.position.set(x,y,z);s.scene.add(mesh);return mesh;}
  // Tall architectural bays and repeated floor lights supply parallax for the physical approach.
  for(let i=0;i<7;i++){
    const z=12-i*6;
    for(const side of [-1,1]){box(.45,13,.65,side*9,6.5,z,dark,true);box(.032,10,.06,side*8.74,6,z+.34,i%2?cyan:warm);box(.08,.024,3,side*3.4,.02,z,warm);}
    box(18,.35,.6,0,12.8,z,dark);
  }
  const plinth=box(13.4,.35,2.2,0,.2,-.3,dark,true);
  box(12.7,.028,1.7,0,.39,-.3,gold);
  for(const x of [-5.7,5.7])box(.12,1.3,.12,x,1,0,gold,true);
  const cy=5.0,w=12,h=6.75;
  // A dark backing avoids the washed-out type common to additive holograms.
  box(w+.24,h+.24,.15,0,cy,-.17,dark,true);
  box(w,h,.035,0,cy,-.065,new THREE.MeshStandardMaterial({color:0x071723,metalness:.35,roughness:.42,envMapIntensity:.22}));
  for(const side of [-1,1]){box(.075,h+.2,.15,side*(w/2+.08),cy,0,gold,true);box(w+.25,.075,.15,0,cy+side*(h/2+.08),0,gold,true);box(.018,h,.025,side*(w/2-.025),cy,.045,cyan);}
  box(w,.018,.025,0,cy-h/2+.025,.045,cyan);
  // Thin secondary frame behind the screen gives the hovering panel a visible depth edge.
  const rear=new THREE.Mesh(ringOf(w+.7,h+.7,.18,.018),cyan);rear.position.set(0,cy,-.36);s.scene.add(rear);
  // Projection cone is a light atmospheric veil, low alpha to preserve the blacks.
  const beam=new THREE.Mesh(new THREE.ConeGeometry(5.7,5,4,1,true),new THREE.MeshBasicMaterial({color:0x7fd8ff,transparent:true,opacity:.018,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending}));beam.rotation.z=Math.PI;beam.rotation.y=Math.PI/4;beam.scale.z=.12;beam.position.set(0,2.8,.1);s.scene.add(beam);
  const pg=new THREE.BufferGeometry(),pos=new Float32Array(900*3);s.seeds=[];
  for(let i=0;i<900;i++)s.seeds.push([rnd(i+43),rnd(i+533),rnd(i+999)]);
  pg.setAttribute('position',new THREE.BufferAttribute(pos,3));s.dust=new THREE.Points(pg,new THREE.PointsMaterial({map:dotTex('155,220,245'),size:.045,transparent:true,opacity:.48,depthWrite:false,blending:THREE.AdditiveBlending,color:0x91bed0}));s.dust.frustumCulled=false;s.scene.add(s.dust);
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  // DOM pixels -> screen world coordinates; project the exact same plane through the real camera.
  s.screenWorld=new THREE.Matrix4().set(w/960,0,0,-w/2,0,-h/540,0,cy+h/2,0,0,1,.055,0,0,0,1);
  s.films=Array.from({length:5},(_,k)=>el('cl-film-'+k).getContext('2d'));return s;
}
function projectCloseScreen(s){
  s.cam.updateMatrixWorld();
  const m=new THREE.Matrix4().multiplyMatrices(s.cam.projectionMatrix,s.cam.matrixWorldInverse).multiply(s.screenWorld).elements;
  const css=[];
  // the element's z is always 0, but an all-zero z row makes the matrix non-invertible and the browser then does not
  // draw the element at all (the round-1 screen was blank); a 1 on the z diagonal keeps it invertible and changes nothing.
  for(let col=0;col<4;col++){const j=col*4;css.push(640*(m[j]+m[j+3]),360*(m[j+3]-m[j+1]),col===2?1:0,m[j+3]);}
  el('cl-screen').style.transform='matrix3d('+css.join(',')+')';
}
async function render(frame,totalFrames,fps){
  const t=frame/fps;if(!S)S=setupClose();const s=S;
  const intro=ease(seg(t,C[0],C[2])),step=ease(seg(t,C[2],D));
  s.cam.position.set(lerp(2.0-.8*intro,.15,step),lerp(4.0,4.5,step),lerp(20.5,16.1,step));s.cam.lookAt(0,4.55,0);
  const pos=s.dust.geometry.attributes.position;
  s.seeds.forEach(([a,b,c],i)=>pos.setXYZ(i,(a-.5)*21,((b+t/D*.18)%1)*11,(c-.5)*28));pos.needsUpdate=true;
  s.films.forEach((g,k)=>miniFilm(g,k,0,0,320,180,t+k));
  el('cl-title').style.opacity=seg(t,C[0],C[0]+(C[1]-C[0])*.16);
  el('cl-power').style.opacity=seg(t,C[1],C[1]+(C[2]-C[1])*.18);
  el('cl-step').style.opacity=seg(t,C[2],C[2]+(D-C[2])*.22);
  s.composer.render();projectCloseScreen(s);beatFade(t,D,.2,.25);
}
