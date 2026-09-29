// requires: objects/Water
const PROMPT_LINES = ['At dawn by the sea,', 'particles of light melt into the waves'];
const PROMPT_TEXT = PROMPT_LINES.join('\n');
let S;
async function setupPrompt() {
  await waitFonts();
  const s = makeRenderer('prompt-ocean', [0.12, 0.25, 1.1]);
  s.cam.fov = 47; s.cam.near = 0.1; s.cam.far = 250000; s.cam.updateProjectionMatrix();
  // Keep the sky, water reflection and bloom linear; apply exposure only once, at output.
  s.R.toneMapping = THREE.NoToneMapping;
  // mulmocast rewrites only html src attributes to absolute paths, so the texture comes from the hidden <img>
  const normals = await new THREE.TextureLoader().loadAsync(el('tex_water').src);
  normals.wrapS = normals.wrapT = THREE.RepeatWrapping;
  normals.anisotropy = Math.min(8, s.R.capabilities.getMaxAnisotropy());
  const sun = new THREE.Vector3(0.24, 0.032, -1).normalize();
  // A bounded dawn palette avoids the atmospheric Sky shader's broad white solar halo.
  // The same sphere is captured by Water's mirror camera, so the colours reflect in the sea.
  const sky = new THREE.Mesh(new THREE.SphereGeometry(100000, 48, 24), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: { sunDirection: { value: sun } },
    vertexShader: `varying vec3 skyDirection;
      void main(){skyDirection=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader: `uniform vec3 sunDirection; varying vec3 skyDirection;
      void main(){
        vec3 d=normalize(skyDirection);
        float h=max(d.y,0.);
        vec3 horizon=vec3(.85,.17,.055), rose=vec3(.32,.065,.12);
        vec3 violet=vec3(.045,.025,.115), blue=vec3(.012,.022,.075);
        vec3 c=mix(horizon,rose,smoothstep(0.,.12,h));
        c=mix(c,violet,smoothstep(.07,.29,h));
        c=mix(c,blue,smoothstep(.22,.52,h));
        float angle=acos(clamp(dot(d,sunDirection),-1.,1.));
        c+=vec3(.32,.10,.018)*exp(-angle*angle/.0032);
        float disc=1.-smoothstep(.009,.0105,angle);
        c=mix(c,vec3(3.2,1.25,.25),disc);
        gl_FragColor=vec4(c,1.);
      }`
  }));
  s.scene.add(sky);
  // Dense near-field mesh grades logarithmically into the horizon; no faceted distant grid.
  const geom = new THREE.PlaneGeometry(1, 1, 300, 230);
  const p = geom.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const u = p.getX(i) + 0.5, v = p.getY(i) + 0.5;
    const distance = Math.expm1(v * Math.log(16001));
    p.setXYZ(i, (u - 0.5) * (180 + distance * 3), distance - 65, 0);
  }
  geom.computeBoundingSphere();
  const water = new THREE.Water(geom, { textureWidth: 1024, textureHeight: 512,
    waterNormals: normals, sunDirection: sun, sunColor: 0xffa443,
    waterColor: 0x031522, distortionScale: 2.0 });
  water.rotation.x = -Math.PI / 2; s.scene.add(water); s.water = water;
  water.material.uniforms.size.value = 2.0;
  // Swell displaces real geometry. Its analytic derivatives also tilt the normal-map lighting.
  const swell = `
    float swell(vec2 p) { return .19*sin(dot(p,vec2(.19,.31))+time*.8)
      +.095*sin(dot(p,vec2(-.41,.22))-time*.65)
      +.045*sin(dot(p,vec2(.73,.51))+time*1.1); }
    vec2 slope(vec2 p) { return .19*vec2(.19,.31)*cos(dot(p,vec2(.19,.31))+time*.8)
      +.095*vec2(-.41,.22)*cos(dot(p,vec2(-.41,.22))-time*.65)
      +.045*vec2(.73,.51)*cos(dot(p,vec2(.73,.51))+time*1.1); }
  `;
  water.material.vertexShader = water.material.vertexShader.replace('void main() {', swell + '\nvoid main() {\n vec3 displaced = position; displaced.z += swell(vec2(position.x,-position.y));')
    .replaceAll('vec4( position, 1.0 )', 'vec4( displaced, 1.0 )');
  water.material.fragmentShader = water.material.fragmentShader.replace('void main() {', swell + '\nvoid main() {')
    .replace('vec3 surfaceNormal = normalize( noise.xzy * vec3( 1.5, 1.0, 1.5 ) );',
      'vec2 ds = slope(worldPosition.xz); vec3 surfaceNormal = normalize(noise.xzy * vec3(.72,1.0,.72) + vec3(-ds.x,0.0,-ds.y));')
    .replace('100.0, 2.0, 0.5', '240.0, 4.5, 0.35')
    .replace('float rf0 = 0.3;', 'float rf0 = 0.045;')
    // Remove Water's constant grey fill; preserve dark troughs and add direct amber glints.
    .replace('vec3 outgoingLight = albedo;', `
      vec3 deepWater = waterColor * (.32 + .68 * max(surfaceNormal.y,0.));
      vec3 reflected = reflectionSample * .82;
      vec3 outgoingLight = mix(deepWater + scatter*.22, reflected, reflectance)
        + specularLight * .9;`);

  // Display transform after bloom (r147 composer does not automatically encode its output).
  const finish = new THREE.ShaderPass({ uniforms: { tDiffuse: { value: null } },
    vertexShader: 'varying vec2 vUv; void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader: `uniform sampler2D tDiffuse; varying vec2 vUv;
      void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;
      c=max(c,vec3(0.))*.9;
      c=clamp((c*(2.51*c+.03))/(c*(2.43*c+.59)+.14),0.,1.);
      c=mix(12.92*c,1.055*pow(c,vec3(1./2.4))-.055,step(vec3(.0031308),c));
      c*=1.-.13*pow(length((vUv-.5)*vec2(1.,.75)),1.5);
      gl_FragColor=vec4(c,1.);}` });
  s.composer.addPass(finish);
  // Rasterize at precisely the HTML baselines, so every speck has a letter as its origin.
  const mask = document.createElement('canvas'); mask.width = 1280; mask.height = 720;
  const g = mask.getContext('2d'); g.font = "400 30px 'Inter Tight'"; g.fillStyle = '#fff';
  g.textBaseline = 'alphabetic';
  el('prompt-copy').textContent = PROMPT_TEXT;
  const textNode = el('prompt-copy').firstChild;
  s.specks = [];
  for (let j = 0; j < PROMPT_TEXT.length; j++) {
    if (/\s/.test(PROMPT_TEXT[j])) continue;
    const range = document.createRange(); range.setStart(textNode,j); range.setEnd(textNode,j+1);
    const rect = range.getBoundingClientRect();
    const ascent = g.measureText(PROMPT_TEXT[j]).fontBoundingBoxAscent;
    g.fillText(PROMPT_TEXT[j],rect.x,rect.y+ascent);
  }
  const data = g.getImageData(0,0,1280,720).data;
  for(let y=300;y<445;y+=2) for(let x=210;x<1080;x+=2)
    if(data[(y*1280+x)*4+3]>100) s.specks.push([x,y,rnd(x+y*1280),rnd(x*7+y*3)]);
  return s;
}
async function render(frame, totalFrames, fps) {
  const t = frame / fps;
  if (!S) S = setupPrompt();
  const s = await S;
  const remaining = D-C[2], after = seg(t,C[2],D);
  // First phrase types the setting, second phrase completes the image and leaves a reading hold.
  const first = PROMPT_LINES[0].length;
  const n = t<C[1] ? Math.floor(first*seg(t,C[0],C[1]))
    : first+Math.floor((PROMPT_TEXT.length-first)*seg(t,C[1],C[2]-(C[2]-C[1])*.15));
  el('prompt-copy').textContent = PROMPT_TEXT.slice(0,n);
  el('prompt-caret').style.opacity = t<C[2] ? (Math.sin((t-C[0])/(C[1]-C[0])*Math.PI*6)>0 ? 1:.2) : 0;
  // Reveal beneath the intact box just ahead of "Now", then dissolve into that lit ocean.
  const revealStart = C[2]-Math.min(.22,remaining*.06);
  const revealEnd = C[2]+remaining*.18;
  const uiEnd = C[2]+remaining*.16;
  const dissolve = seg(t,C[2],uiEnd);
  el('prompt-ui').style.opacity = 1-easeOut(dissolve);
  el('prompt-ui').style.visibility = t>=uiEnd ? 'hidden' : 'visible';
  el('prompt-copy').style.opacity = 1-seg(t,C[2],C[2]+remaining*.06);
  el('prompt-cover').style.opacity = 1-easeOut(seg(t,revealStart,revealEnd));
  el('prompt-cover').style.visibility = t>=revealEnd ? 'hidden' : 'visible';
  s.cam.position.set(lerp(-1.2,1.0,after),lerp(3.5,2.8,after),lerp(24,12,after));
  s.cam.lookAt(lerp(-1.2,0.0,after),-3.6,-120);
  s.water.material.uniforms.time.value = t*.55;
  s.composer.render();
  const g=el('prompt-light').getContext('2d'); g.clearRect(0,0,1280,720);
  const lightEnd = C[2]+remaining*.48;
  el('prompt-light').style.visibility = t>=lightEnd ? 'hidden' : 'visible';
  if(t>=C[2] && t<lightEnd) {
    g.globalCompositeOperation='lighter';
    s.specks.forEach(([x,y,a,b],i)=>{
      const life = seg(t,C[2]+remaining*a*.065,C[2]+remaining*(.32+a*.16));
      const drift = easeIn(life), fade = (1-seg(life,.62,1))*seg(t,C[2],C[2]+remaining*.025);
      if(fade<=0)return;
      const px=x+Math.sin(life*5+b*6.28)*life*28+(a-.5)*drift*150;
      const py=y+drift*(220+b*150);
      const radius=(.65+b*.7)*(1+life*.45);
      g.globalAlpha=fade*(.5+a*.5); g.fillStyle='#ffdf9f';
      g.shadowColor='#ffb950'; g.shadowBlur=life>0?5:0;
      g.fillRect(px,py,radius,radius);
    });
    g.shadowBlur=0;g.globalAlpha=1;g.globalCompositeOperation='source-over';
  }
  beatFade(t,D,0.2,0.25);
}
