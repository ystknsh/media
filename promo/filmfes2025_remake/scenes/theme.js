// requires: environments/RoomEnvironment
let S;
async function setupTheme(){
  const s=makeRenderer('theme-space',[.42,.45,.9]);
  s.scene.background=new THREE.Color('#05070b');s.scene.fog=new THREE.FogExp2('#05070b',.026);
  const pm=new THREE.PMREMGenerator(s.R),room=new THREE.RoomEnvironment();
  s.env=pm.fromScene(room,.04);s.scene.environment=s.env.texture;pm.dispose();room.dispose();
  s.R.toneMapping=THREE.ACESFilmicToneMapping;s.R.toneMappingExposure=.85;
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  s.world=new THREE.Group();s.scene.add(s.world);
  // A tapered strip with a changing cross-section: a brushstroke that twists in space.
  s.warmPoint=u=>new THREE.Vector3(-9.5+9.5*u,(Math.sin(u*11)*1.05+Math.sin(u*24)*.17)*(1-u),Math.sin(u*13)*1.35*(1-u));
  const vertices=[],indices=[],steps=240;
  for(let i=0;i<=steps;i++){
    const u=i/steps,p=s.warmPoint(u),w=(.10+.25*Math.sin(Math.PI*u))*(1-.65*Math.pow(u,8));
    const twist=u*11+.25*Math.sin(u*17);
    for(const sign of [-1,1])vertices.push(p.x,p.y+sign*w*Math.cos(twist),p.z+sign*w*Math.sin(twist));
    if(i<steps){const k=i*2;indices.push(k,k+1,k+2,k+1,k+3,k+2);}
  }
  const rg=new THREE.BufferGeometry();rg.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));rg.setIndex(indices);rg.computeVertexNormals();
  s.ribbon=new THREE.Mesh(rg,new THREE.MeshStandardMaterial({color:0xe9b757,metalness:.8,roughness:.29,side:THREE.DoubleSide,emissive:0x7c3507,emissiveIntensity:.12}));s.world.add(s.ribbon);s.rg=rg;
  // Fine filaments sit beside the ribbon, like several hairs from the same brush.
  s.filaments=[];
  for(let j=0;j<3;j++){
    const points=[];for(let i=0;i<=steps;i++){const u=i/steps,p=s.warmPoint(u);p.y+=(j-1)*.14*(1-u);p.z+=.08*Math.sin(u*25+j)*(1-u);points.push(p);}
    const g=new THREE.BufferGeometry().setFromPoints(points),line=new THREE.Line(g,new THREE.LineBasicMaterial({color:0xf6d88b,transparent:true,opacity:.32}));s.world.add(line);s.filaments.push(g);
  }
  const nodes=[new THREE.Vector3(9.5,-.6,-.8),new THREE.Vector3(7.8,-.6,-.8),new THREE.Vector3(6.4,1.05,.1),new THREE.Vector3(4.8,1.05,.1),new THREE.Vector3(3.4,-.7,.7),new THREE.Vector3(1.8,-.7,.7),new THREE.Vector3(0,0,0)];
  s.coolCurve=new THREE.CurvePath();for(let i=0;i<nodes.length-1;i++)s.coolCurve.add(new THREE.LineCurve3(nodes[i],nodes[i+1]));
  const crystal=new THREE.MeshPhysicalMaterial({color:0x80c8e4,metalness:.4,roughness:.16,clearcoat:1,clearcoatRoughness:.1,emissive:0x173747,emissiveIntensity:.3});
  s.crystals=new THREE.InstancedMesh(new THREE.OctahedronGeometry(.19,0),crystal,150);s.world.add(s.crystals);
  s.matrix=new THREE.Object3D();
  const guidePts=[];for(let i=0;i<=300;i++)guidePts.push(s.coolCurve.getPoint(i/300));
  s.guide=new THREE.BufferGeometry().setFromPoints(guidePts);s.world.add(new THREE.Line(s.guide,new THREE.LineBasicMaterial({color:0x7fd8ff,transparent:true,opacity:.8})));
  s.warmTip=new THREE.Mesh(new THREE.SphereGeometry(.08,12,8),new THREE.MeshBasicMaterial({color:0xffda85}));s.world.add(s.warmTip);
  s.coolTip=new THREE.Mesh(new THREE.OctahedronGeometry(.14),new THREE.MeshBasicMaterial({color:0xa8e4ff}));s.world.add(s.coolTip);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshStandardMaterial({color:0x04070b,metalness:.4,roughness:.48}));floor.rotation.x=-Math.PI/2;floor.position.y=-3;s.scene.add(floor);
  const warm=new THREE.PointLight(0xffce7e,20,25,2);warm.position.set(-4,3,4);s.scene.add(warm);
  const cool=new THREE.PointLight(0x7fd8ff,24,25,2);cool.position.set(5,2,3);s.scene.add(cool);
  s.scene.add(new THREE.HemisphereLight(0xa7bdd1,0x211407,.65));
  s.burstPos=new Float32Array(900*3);const bg=new THREE.BufferGeometry();bg.setAttribute('position',new THREE.BufferAttribute(s.burstPos,3));
  const colors=[];for(let i=0;i<900;i++){const c=new THREE.Color(i%2?0xe9c46a:0x7fd8ff);colors.push(c.r,c.g,c.b);}bg.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  s.burst=new THREE.Points(bg,new THREE.PointsMaterial({size:.065,map:dotTex('255,238,200'),vertexColors:true,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}));s.world.add(s.burst);
  s.halo=new THREE.Mesh(new THREE.RingGeometry(.98,1,96),new THREE.MeshBasicMaterial({color:0xcce4e4,transparent:true,opacity:0,side:THREE.DoubleSide,depthWrite:false}));s.world.add(s.halo);
  const dp=[];for(let i=0;i<600;i++)dp.push((rnd(i+32)-.5)*34,(rnd(i+33)-.5)*16,(rnd(i+34)-.5)*25);
  const dg=new THREE.BufferGeometry();dg.setAttribute('position',new THREE.Float32BufferAttribute(dp,3));s.dust=new THREE.Points(dg,new THREE.PointsMaterial({color:0x758d9d,size:.025,transparent:true,opacity:.4}));s.scene.add(s.dust);
  return s;
}
async function render(frame,totalFrames,fps){
  const t=frame/fps;if(!S)S=setupTheme();const s=await S;
  const u=seg(t,0,D),grow=ease(seg(t,C[0],C[2])),after=seg(t,C[2],D);
  s.rg.setDrawRange(0,Math.floor(grow*240)*6);s.filaments.forEach(g=>g.setDrawRange(0,Math.floor(grow*240)+1));
  s.guide.setDrawRange(0,Math.floor(grow*300)+1);
  const count=Math.floor(grow*150);s.crystals.count=count;
  for(let i=0;i<count;i++){
    const v=i/149;s.matrix.position.copy(s.coolCurve.getPoint(v));s.matrix.rotation.set(v*6+u*.35,v*9,v*3);s.matrix.scale.setScalar(.65+.3*Math.sin(v*Math.PI));s.matrix.updateMatrix();s.crystals.setMatrixAt(i,s.matrix.matrix);
  }
  s.crystals.instanceMatrix.needsUpdate=true;
  s.warmTip.position.copy(s.warmPoint(grow));s.coolTip.position.copy(s.coolCurve.getPoint(grow));
  s.warmTip.visible=s.coolTip.visible=t>=C[0]&&t<C[2];
  s.burst.visible=t>=C[2];
  const expansion=easeOut(after);
  for(let i=0;i<900;i++){
    const angle=rnd(i+19)*Math.PI*2,z=rnd(i+21)*2-1,r=(.4+rnd(i+27)*4.5)*expansion,xy=Math.sqrt(1-z*z);
    s.burstPos[i*3]=Math.cos(angle)*xy*r;s.burstPos[i*3+1]=Math.sin(angle)*xy*r;s.burstPos[i*3+2]=z*r;
  }
  s.burst.geometry.attributes.position.needsUpdate=true;s.burst.material.opacity=(1-after)*.9;
  s.halo.scale.setScalar(.1+expansion*4.3);s.halo.material.opacity=t>=C[2]?(1-after)*.45:0;
  s.cam.position.set(lerp(1.4,-.5,u),lerp(1.6,.9,u),lerp(18,16.5,u));s.cam.lookAt(0,.2,0);  // closer: the two paths fill the frames.halo.quaternion.copy(s.cam.quaternion);
  s.dust.rotation.y=u*.07;
  el('theme-kicker').style.opacity=seg(t,C[0],C[0]+.25);
  el('theme-people').style.opacity=el('theme-ai').style.opacity=seg(t,C[1],C[1]+.3);
  el('theme-caption').style.opacity=seg(t,C[1],C[1]+.3);
  el('theme-together').style.opacity=seg(t,C[2],C[2]+(D-C[2])*.18);
  s.composer.render();beatFade(t,D,.2,.25);
}
