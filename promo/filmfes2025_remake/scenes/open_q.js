// requires: environments/RoomEnvironment, objects/Sky
let S;
function setupQuestions() {
  const s=makeRenderer('oq-world',[.28,.65,.95]);
  s.R.toneMapping=THREE.ACESFilmicToneMapping; s.R.toneMappingExposure=.85;
  s.cam.fov=46;s.cam.far=4000;s.cam.updateProjectionMatrix();
  const pm=new THREE.PMREMGenerator(s.R), room=new THREE.RoomEnvironment();
  s.env=pm.fromScene(room,.04);s.scene.environment=s.env.texture;room.dispose();pm.dispose();
  s.scene.fog=new THREE.FogExp2(0x24333e,.009);
  // Physical sky: the sun climbs from below the horizon (night over the maze) to just above it (the answer).
  const sky=new THREE.Sky();sky.scale.setScalar(3000);const su=sky.material.uniforms;
  su.turbidity.value=7;su.rayleigh.value=2.6;su.mieCoefficient.value=.006;su.mieDirectionalG.value=.86;
  s.sunDir=(elev)=>new THREE.Vector3().setFromSphericalCoords(1,THREE.MathUtils.degToRad(90-elev),Math.PI-.12);
  s.sky=sky;s.scene.add(sky);
  // the river mirrors the sunrise sky: one PMREM of the sky at its final sun height
  const skyScene=new THREE.Scene(),skyCopy=new THREE.Sky();skyCopy.scale.setScalar(3000);
  Object.keys(su).forEach((k)=>{if(skyCopy.material.uniforms[k]&&k!=='sunPosition')skyCopy.material.uniforms[k].value=su[k].value;});
  skyCopy.material.uniforms.sunPosition.value.copy(s.sunDir(3));skyScene.add(skyCopy);
  const pm2=new THREE.PMREMGenerator(s.R);s.skyEnv=pm2.fromScene(skyScene).texture;pm2.dispose();
  s.hemi=new THREE.HemisphereLight(0x8fa9c9,0x1a1410,.35);s.scene.add(s.hemi);
  s.sunlight=new THREE.DirectionalLight(0xffb870,2.5);s.sunlight.position.set(30,10,-120);s.scene.add(s.sunlight);

  const halo=new THREE.Sprite(new THREE.SpriteMaterial({map:dotTex('246,165,85'),color:0xc78746,transparent:true,opacity:.3,depthWrite:false,blending:THREE.AdditiveBlending,fog:false}));s.halo=halo;halo.scale.set(420,420,1);s.scene.add(halo);
  // A real valley: broad ridges flank a winding low riverbed, with layered silhouettes in fog.
  const land=new THREE.PlaneGeometry(520,430,160,140);land.rotateX(-Math.PI/2);
  const lp=land.attributes.position;
  for(let i=0;i<lp.count;i++){
    const x=lp.getX(i),z=lp.getZ(i)-150;
    const river=13*Math.sin(z*.026), bank=Math.abs(x-river);
    const height=(1-Math.exp(-bank*bank/1400))*(9+17*Math.pow(.5+.5*Math.sin(x*.035+z*.02),2)+8*Math.sin(z*.049+x*.02));
    lp.setXYZ(i,x,height-5,z);
  }
  land.computeVertexNormals();s.scene.add(new THREE.Mesh(land,new THREE.MeshStandardMaterial({color:0x2e2a26,roughness:.95,metalness:0})));
  const river=new THREE.Mesh(new THREE.PlaneGeometry(36,440),new THREE.MeshStandardMaterial({color:0xffffff,metalness:1,roughness:.06,envMap:s.skyEnv,envMapIntensity:1}));river.rotation.x=-Math.PI/2;river.position.set(0,-4.5,-145);s.scene.add(river);s.river=river;
  const base=new THREE.Mesh(new THREE.BoxGeometry(35,1,35),new THREE.MeshStandardMaterial({color:0x18242b,roughness:.65,metalness:.3}));base.position.y=-.55;s.scene.add(base);s.base=base;
  // Seeded depth-first carving produces an actual connected maze, not random blocks.
  const n=13, walls=new Map(),visited=new Set([0]),stack=[[0,0]];
  for(let z=0;z<=n;z++)for(let x=0;x<n;x++)walls.set(`h${x},${z}`,[x,z,0]);
  for(let x=0;x<=n;x++)for(let z=0;z<n;z++)walls.set(`v${x},${z}`,[x,z,1]);
  let seed=41;
  while(stack.length){const [x,z]=stack[stack.length-1];const nb=[[1,0],[-1,0],[0,1],[0,-1]].filter(([dx,dz])=>x+dx>=0&&x+dx<n&&z+dz>=0&&z+dz<n&&!visited.has((z+dz)*n+x+dx));
    if(!nb.length){stack.pop();continue;}const [dx,dz]=nb[Math.floor(rnd(seed++)*nb.length)];
    walls.delete(dx?`v${x+(dx>0?1:0)},${z}`:`h${x},${z+(dz>0?1:0)}`);visited.add((z+dz)*n+x+dx);stack.push([x+dx,z+dz]);}
  walls.delete('h6,0');walls.delete('h6,13');s.walls=Array.from(walls.values());
  s.maze=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshStandardMaterial({color:0x526473,metalness:.7,roughness:.29,envMapIntensity:.65}),s.walls.length);
  s.edges=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshStandardMaterial({color:0xe9c46a,emissive:0x604617,emissiveIntensity:.5,metalness:.65,roughness:.3}),s.walls.length);
  s.maze.instanceMatrix.setUsage(THREE.DynamicDrawUsage);s.edges.instanceMatrix.setUsage(THREE.DynamicDrawUsage);s.maze.frustumCulled=s.edges.frustumCulled=false;s.scene.add(s.maze,s.edges);s.dummy=new THREE.Object3D();
  const dust=new Float32Array(600*3);for(let i=0;i<600;i++){dust[i*3]=(rnd(i+90)-.5)*65;dust[i*3+1]=rnd(i+870)*18;dust[i*3+2]=(rnd(i+340)-.5)*60;}
  const dg=new THREE.BufferGeometry();dg.setAttribute('position',new THREE.BufferAttribute(dust,3));s.dust=new THREE.Points(dg,new THREE.PointsMaterial({size:.08,map:dotTex('235,202,146'),color:0xe9c46a,transparent:true,opacity:.4,depthWrite:false}));s.scene.add(s.dust);
  s.composer.addPass(new THREE.ShaderPass({uniforms:{tDiffuse:{value:null}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;gl_FragColor=vec4(max(c,vec3(0.)),1.);}'}));
  return s;
}
async function render(frame,totalFrames,fps){
  const t=frame/fps;if(!S)S=setupQuestions();const s=S;
  const travel=seg(t,C[0],C[1]),reveal=ease(seg(t,C[1],C[1]+(D-C[1])*.72));
  s.cam.position.set(lerp(15-4*travel,2,reveal),lerp(24-3*travel,8,reveal),lerp(30-4*travel,13,reveal));
  s.cam.lookAt(lerp(0,4,reveal),lerp(0,2,reveal),lerp(-2,-100,reveal));
  const elev=lerp(-6,3,reveal),sd=s.sunDir(elev);s.sky.material.uniforms.sunPosition.value.copy(sd);
  s.halo.position.copy(sd).multiplyScalar(1500);s.halo.material.opacity=.35*reveal;
  s.sunlight.position.copy(sd).multiplyScalar(200);s.sunlight.intensity=lerp(.2,2.6,reveal);
  s.R.toneMappingExposure=lerp(.85,.5,reveal);
  s.river.material.envMapIntensity=lerp(.04,1,reveal);  // no sunrise in the water while it is still night
  s.base.position.y=-.55-ease(seg(t,C[1],C[1]+(D-C[1])*.6))*8;  // the maze's slab sinks with its walls
  s.scene.fog.color.setRGB(lerp(.02,.62,reveal),lerp(.035,.40,reveal),lerp(.06,.30,reveal));
  s.walls.forEach(([x,z,v],i)=>{const delay=rnd(i+500)*.15;const sink=ease(seg(t,C[1]+(D-C[1])*delay,C[1]+(D-C[1])*(delay+.42)));
    const d=s.dummy;d.position.set((x-6.5+(v?0:.5))*2.4,1.55-sink*4.5,(z-6.5+(v?.5:0))*2.4);d.scale.set(v?.19:2.6,3.1,v?2.6:.19);d.updateMatrix();s.maze.setMatrixAt(i,d.matrix);
    d.position.y+=1.57;d.scale.y=.035;d.updateMatrix();s.edges.setMatrixAt(i,d.matrix);});
  s.maze.instanceMatrix.needsUpdate=s.edges.instanceMatrix.needsUpdate=true;s.dust.rotation.y=t/D*.08;
  el('oq-question').style.opacity=seg(t,C[0],C[0]+(C[1]-C[0])*.12)*(1-seg(t,C[1],C[1]+(D-C[1])*.15));
  el('oq-answer').style.opacity=seg(t,C[1]+(D-C[1])*.16,C[1]+(D-C[1])*.4);
  s.composer.render();beatFade(t,D,.2,.25);
}
