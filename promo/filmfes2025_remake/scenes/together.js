// requires: environments/RoomEnvironment
let S;
function setupTogether(){
  const s=makeRenderer('tg-world',[.55,.55,1.0]);s.R.toneMapping=THREE.ACESFilmicToneMapping;s.R.toneMappingExposure=.78;
  s.scene.background=new THREE.Color(0x04080e);s.scene.fog=new THREE.FogExp2(0x04080e,.027);
  const pm=new THREE.PMREMGenerator(s.R),room=new THREE.RoomEnvironment();s.env=pm.fromScene(room,.04);s.scene.environment=s.env.texture;room.dispose();pm.dispose();
  s.scene.add(new THREE.HemisphereLight(0xbedaff,0x111725,.6));
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshStandardMaterial({color:0x0d1720,metalness:.75,roughness:.3}));floor.rotation.x=-Math.PI/2;floor.position.y=-3.5;s.scene.add(floor);
  const stage=new THREE.Mesh(new THREE.CylinderGeometry(5,5.2,.2,96),new THREE.MeshStandardMaterial({color:0x17212c,metalness:.8,roughness:.27}));stage.position.y=-3.45;s.scene.add(stage);
  for(let i=0;i<3;i++){const ring=new THREE.Mesh(new THREE.TorusGeometry(4.2+i*.3,.013,6,96),new THREE.MeshBasicMaterial({color:0x34536b}));ring.rotation.x=-Math.PI/2;ring.position.y=-3.33;s.scene.add(ring);}
  s.strands=[];s.lights=[];
  for(let k=0;k<2;k++){
    const g=new THREE.BufferGeometry(),positions=new Float32Array(241*9*3),indices=[];
    for(let j=0;j<240;j++)for(let a=0;a<8;a++){const q=j*9+a;indices.push(q,q+9,q+1,q+1,q+9,q+10);}
    g.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));g.setIndex(indices);
    const mat=new THREE.MeshStandardMaterial({color:k?0x7fd8ff:0xe9c46a,emissive:k?0x389dd1:0xdd8a24,emissiveIntensity:1.65,metalness:.65,roughness:.23});
    const mesh=new THREE.Mesh(g,mat);mesh.frustumCulled=false;s.scene.add(mesh);s.strands.push(mesh);
    const light=new THREE.PointLight(k?0x7fd8ff:0xe9c46a,3,15,2);s.scene.add(light);s.lights.push(light);
  }
  const coreMat=new THREE.MeshStandardMaterial({color:0xf6e0a0,emissive:0xffd78c,emissiveIntensity:2.5,roughness:.18,metalness:.55});
  s.core=new THREE.Mesh(new THREE.SphereGeometry(.13,24,16),coreMat);s.scene.add(s.core);
  s.halo=new THREE.Sprite(new THREE.SpriteMaterial({map:dotTex('241,216,158'),color:0xf6e0a0,blending:THREE.AdditiveBlending,transparent:true,depthWrite:false,opacity:.35}));s.halo.scale.set(2,2,1);s.scene.add(s.halo);
  const pg=new THREE.BufferGeometry(),p=new Float32Array(1600*3),col=new Float32Array(1600*3);
  for(let i=0;i<1600;i++){p[i*3]=(rnd(i+17)-.5)*24;p[i*3+1]=(rnd(i+99)-.5)*12;p[i*3+2]=(rnd(i+543)-.5)*18;const c=new THREE.Color(i%2?0x7fd8ff:0xe9c46a);c.toArray(col,i*3);}
  pg.setAttribute('position',new THREE.BufferAttribute(p,3));pg.setAttribute('color',new THREE.BufferAttribute(col,3));s.dust=new THREE.Points(pg,new THREE.PointsMaterial({size:.035,map:dotTex('255,255,255'),vertexColors:true,transparent:true,opacity:.6,depthWrite:false,blending:THREE.AdditiveBlending}));s.scene.add(s.dust);
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  return s;
}
// Tangent and an orthogonal frame give the threads round, truly three-dimensional cross sections.
function strandPoint(u,k,phase,merge){
  const a=u*Math.PI*5.5+phase+k*Math.PI;
  const radius=(1-merge)*(1.0+.6*Math.sin(u*Math.PI))+.025;
  return new THREE.Vector3(Math.cos(a)*radius,-3.2+u*7.1,Math.sin(a)*radius);
}
async function render(frame,totalFrames,fps){
  const t=frame/fps;if(!S)S=setupTogether();const s=S;
  const p=seg(t,C[0],D),merge=ease(seg(t,C[1],C[1]+(D-C[1])*.72));
  const length=lerp(.18,1,easeOut(seg(t,C[0],C[1]))),phase=p*2.4;
  for(let k=0;k<2;k++){
    const g=s.strands[k].geometry,a=g.attributes.position;
    for(let j=0;j<=240;j++){
      const u=j/240*length,v=strandPoint(u,k,phase,merge),next=strandPoint(u+.001,k,phase,merge),tangent=next.sub(v).normalize();
      const normal=new THREE.Vector3(1,0,0).cross(tangent).normalize(),binormal=new THREE.Vector3().crossVectors(tangent,normal).normalize();
      const radius=(.045+.02*Math.sin(u*Math.PI))*(.4+.6*Math.sin(Math.PI*j/240));
      for(let q=0;q<=8;q++){const ang=q/8*Math.PI*2,point=v.clone().addScaledVector(normal,Math.cos(ang)*radius).addScaledVector(binormal,Math.sin(ang)*radius);a.setXYZ(j*9+q,point.x,point.y,point.z);}
    }
    a.needsUpdate=true;g.computeVertexNormals();s.lights[k].position.copy(strandPoint(length*.7,k,phase,merge));
  }
  const head=strandPoint(length,0,phase,merge);s.core.position.copy(head);s.halo.position.copy(head);s.core.scale.setScalar(.5+merge*.7);s.halo.material.opacity=.12+merge*.2;
  s.cam.position.set(lerp(8,2.4,ease(p)),lerp(2.8,1.3,p),lerp(19,17,p));s.cam.lookAt(0,.4,0);
  s.dust.rotation.y=p*.12;
  el('tg-heading').style.opacity=seg(t,C[0],C[0]+(C[1]-C[0])*.18);
  el('tg-caption').style.opacity=seg(t,C[1],C[1]+(D-C[1])*.2);
  s.composer.render();beatFade(t,D,.2,.25);
}
