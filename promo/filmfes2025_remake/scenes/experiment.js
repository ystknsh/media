// requires: environments/RoomEnvironment, geometries/RoundedBoxGeometry
let S;
async function setupExperiment() {
  const s=makeRenderer('experiment-gl',[.4,.48,1.05]);
  s.R.toneMapping=THREE.ACESFilmicToneMapping;s.R.toneMappingExposure=.76;
  s.scene.background=new THREE.Color(0x05070b);s.scene.fog=new THREE.FogExp2(0x05070b,.034);
  const pm=new THREE.PMREMGenerator(s.R),room=new THREE.RoomEnvironment();
  s.env=pm.fromScene(room,.04);s.scene.environment=s.env.texture;room.dispose();pm.dispose();
  const gold=new THREE.MeshStandardMaterial({color:0xb69653,metalness:.88,roughness:.27});
  const film=new THREE.MeshStandardMaterial({color:0x33251a,metalness:.35,roughness:.36,side:THREE.DoubleSide});
  const black=new THREE.MeshStandardMaterial({color:0x0a1720,metalness:.65,roughness:.37});
  const key=new THREE.DirectionalLight(0xffd5a0,2.4);key.position.set(-5,6,8);s.scene.add(key);
  s.blue=new THREE.PointLight(0x7fd8ff,1,25,2);s.blue.position.set(0,2,3);s.scene.add(s.blue);
  function mesh(geo,mat,x,y,z,parent=s.scene){const m=new THREE.Mesh(geo,mat);m.position.set(x,y,z);parent.add(m);return m;}
  mesh(new THREE.RoundedBoxGeometry(21,.32,13,2,.1),black,0,-2.2,-1.5);
  const floor=mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshStandardMaterial({color:0x080d15,metalness:.35,roughness:.5}),0,-2.65,0);floor.rotation.x=-Math.PI/2;
  // Continuous curved celluloid, including actual gaps between its sprocket bridges.
  s.strip=new THREE.Group();s.scene.add(s.strip);
  const path=(x,y)=>new THREE.Vector3(x,1.05+.45*Math.sin(x*.31)+y,1.6*Math.cos(x*.23));
  function patch(x0,x1,y0,y1,mat,uvRect=[0,0,1,1],front=0) {
    const vertices=[],uv=[],indices=[],n=Math.max(1,Math.ceil((x1-x0)*10));
    for(let i=0;i<=n;i++)for(let j=0;j<2;j++){
      const u=i/n,p=path(lerp(x0,x1,u),j?y1:y0);vertices.push(p.x,p.y,p.z+front);
      uv.push(lerp(uvRect[0],uvRect[2],u),j?uvRect[3]:uvRect[1]);
    }
    for(let i=0;i<n;i++){const a=i*2;indices.push(a,a+2,a+1,a+1,a+2,a+3);}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(indices);g.computeVertexNormals();
    const m=new THREE.Mesh(g,mat);s.strip.add(m);return m;
  }
  s.atlas=document.createElement('canvas');s.atlas.width=1600;s.atlas.height=180;
  s.texture=new THREE.CanvasTexture(s.atlas);s.texture.anisotropy=4;
  const images=new THREE.MeshBasicMaterial({map:s.texture,color:0xb0b0b0,side:THREE.DoubleSide,toneMapped:false});
  const pitch=2.95;
  for(let i=0;i<11;i++) {
    const x=(i-5)*pitch;
    patch(x-pitch/2,x+pitch/2,-.89,.89,film);
    patch(x-1.32,x+1.32,-.7425,.7425,images,[(i%5)*.2,0,(i%5+1)*.2,1],.014);
    for(const side of [-1,1]) {
      patch(x-pitch/2,x+pitch/2,side>0?1.1:-1.2,side>0?1.2:-1.1,film);
      for(let j=0;j<8;j++) {
        const a=x-pitch/2+j*pitch/8;
        patch(a,a+.13,side>0?.89:-1.1,side>0?1.1:-.89,film);
      }
    }
    // Narrow metallic edge rails catch the travelling key light without blooming the films.
    for(const side of [-1,1])patch(x-pitch/2,x+pitch/2,side*1.205-.009,side*1.205+.009,gold);
  }
  // Batch the continuous strip by material: all perforations survive, but only three draw calls remain.
  for(const material of [film,images,gold]) {
    const pieces=s.strip.children.filter(m=>m.material===material),positions=[],normals=[],uvs=[],indices=[];
    let offset=0;
    for(const piece of pieces) {
      const geo=piece.geometry;
      positions.push(...geo.attributes.position.array);normals.push(...geo.attributes.normal.array);uvs.push(...geo.attributes.uv.array);
      for(const index of geo.index.array)indices.push(index+offset);
      offset+=geo.attributes.position.count;s.strip.remove(piece);geo.dispose();
    }
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
    geo.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));geo.setIndex(indices);
    s.strip.add(new THREE.Mesh(geo,material));
  }
  s.traces=[];s.signals=[];
  const off=new THREE.MeshStandardMaterial({color:0x354c4d,metalness:.8,roughness:.4});
  const glow=new THREE.MeshStandardMaterial({color:0x71bfd8,emissive:0x58caff,emissiveIntensity:2.2,metalness:.2,roughness:.4});
  const dotgeo=new THREE.SphereGeometry(.052,8,6);
  const chipgeo=new THREE.RoundedBoxGeometry(.68,.24,.87,2,.045);
  const pins=new THREE.InstancedMesh(new THREE.BoxGeometry(.12,.04,.055),gold,34*8),pinPose=new THREE.Object3D();s.scene.add(pins);let pinIndex=0;
  for(let i=0;i<34;i++) {
    const side=i%2?1:-1,x=side*(2.1+rnd(i*5)*7.5),z=-6+rnd(i*7)*10;
    const chip=mesh(chipgeo,black,x,-1.86,z);chip.rotation.y=(i%3)*Math.PI/2;
    for(let j=0;j<4;j++)for(const a of [-1,1]){pinPose.position.set(x+a*.39,-1.83,z-.27+j*.18);pinPose.updateMatrix();pins.setMatrixAt(pinIndex++,pinPose.matrix);}
    const points=[new THREE.Vector3(side*.75,-2.01,-.8+(i%9)*.14),new THREE.Vector3(x*.54,-2.01,-.8+(i%9)*.14),new THREE.Vector3(x*.54,-2.01,z),new THREE.Vector3(x,-2.01,z)];
    const curve=new THREE.CurvePath();for(let j=1;j<points.length;j++)curve.add(new THREE.LineCurve3(points[j-1],points[j]));
    const geo=new THREE.TubeGeometry(curve,42,.014,5,false);s.scene.add(new THREE.Mesh(geo,off));
    const litgeo=geo.clone();const lit=new THREE.Mesh(litgeo,glow);lit.position.y=.007;s.scene.add(lit);
    s.traces.push({geo:litgeo,count:litgeo.index.count});
    const signal=mesh(dotgeo,new THREE.MeshBasicMaterial({color:new THREE.Color(1.3,2,2.5)}),0,0,0);s.signals.push({mesh:signal,curve});
  }
  // The central processor is a real socket and package, directly beneath the film.
  mesh(new THREE.RoundedBoxGeometry(1.8,.12,1.8,2,.06),gold,0,-1.96,0);
  mesh(new THREE.RoundedBoxGeometry(1.42,.26,1.42,2,.07),black,0,-1.78,0);
  const core=mesh(new THREE.PlaneGeometry(.87,.87),new THREE.MeshStandardMaterial({color:0x2d778a,metalness:.9,roughness:.2,emissive:0x1c5068,emissiveIntensity:.3}),0,-1.64,0);core.rotation.x=-Math.PI/2;s.core=core;
  const beamGeo=new THREE.BufferGeometry(),beamPos=[];
  for(let i=0;i<480;i++)beamPos.push((rnd(i*3)-.5)*.85,rnd(i*3+1)*2.5-1.5,(rnd(i*3+2)-.5)*.85);
  beamGeo.setAttribute('position',new THREE.Float32BufferAttribute(beamPos,3));
  s.beam=new THREE.Points(beamGeo,new THREE.PointsMaterial({map:dotTex('127,216,255'),color:0x8be3ff,size:.027,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending}));s.scene.add(s.beam);
  const dust=[];for(let i=0;i<650;i++)dust.push((rnd(i*3)-.5)*32,(rnd(i*3+1)-.5)*12,rnd(i*3+2)*22-10);
  const dg=new THREE.BufferGeometry();dg.setAttribute('position',new THREE.Float32BufferAttribute(dust,3));
  s.dust=new THREE.Points(dg,new THREE.PointsMaterial({color:0xd5bc82,map:dotTex('233,196,106'),size:.029,transparent:true,opacity:.32,depthWrite:false}));s.scene.add(s.dust);
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  return s;
}
async function render(frame,totalFrames,fps) {
  const t=frame/fps,u=seg(t,0,D);if(!S)S=setupExperiment();const s=await S;
  const reveal=easeOut(seg(t,C[1],C[1]+(D-C[1])*.47));
  s.cam.position.set(lerp(-1.4,1.2,u),lerp(4.25,5.9,u),lerp(18,16.8,u));s.cam.lookAt(0,-.2,0);
  s.strip.position.x=lerp(.7,-.7,u);s.strip.rotation.y=lerp(-.06,.06,u);
  const g=s.atlas.getContext('2d');for(let i=0;i<5;i++)miniFilm(g,i,i*s.atlas.width/5,0,s.atlas.width/5,s.atlas.height,u*4+i);s.texture.needsUpdate=true;
  s.traces.forEach((trace,i)=>{const k=easeOut(seg(t,C[1]+(D-C[1])*rnd(i)*.1,C[1]+(D-C[1])*(.42+rnd(i)*.1)));trace.geo.setDrawRange(0,Math.floor(trace.count*k/3)*3);});
  s.signals.forEach((signal,i)=>{const p=(seg(t,C[1],D)*1.8+rnd(i))%1;signal.mesh.position.copy(signal.curve.getPoint(p));signal.mesh.position.y+=.035;signal.mesh.visible=reveal>.01;signal.mesh.scale.setScalar(reveal);});
  s.blue.intensity=1+reveal*19;s.core.material.emissiveIntensity=.3+reveal*1.6;
  s.beam.material.opacity=reveal*.62;s.beam.rotation.y=u*.4;
  s.dust.rotation.y=u*.04;s.dust.position.y=u*.13;
  el('experiment-title').style.opacity=seg(t,C[0],C[0]+(C[1]-C[0])*.1);
  el('experiment-title').style.transform=`translateY(${(1-easeOut(seg(t,C[0],C[0]+(C[1]-C[0])*.16)))*10}px)`;
  el('experiment-second').style.opacity=seg(t,C[1],C[1]+(D-C[1])*.15);
  el('experiment-second').style.transform=`translateY(${(1-reveal)*14}px)`;
  el('experiment-label').style.opacity=seg(t,C[1],C[1]+(D-C[1])*.3);
  s.composer.render();beatFade(t,D,0.2,0.25);
}
