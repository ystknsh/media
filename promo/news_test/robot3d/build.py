"""robot v2 — the same article and narration as robot v1 (reenactment VTR), rebuilt as a 3D scene.

Models are ShapeScript (MulmoTerminal's 3D plugin) exported to GLB by models.mjs (node models.mjs);
the GLBs are embedded as base64 and staged, lit and filmed with three.js r147 in html_tailwind beats.
Costs: TTS only (BGM is the vtr bed already generated for robot v1).
"""
import base64
import json
import pathlib

HERE = pathlib.Path(__file__).parent
SCRATCH = HERE.parent
BGM = SCRATCH / "robot" / "assets" / "vtr-bed.mp3"
KIT = pathlib.Path(__file__).resolve().parents[4] / "mulmo-presentations" / "samples" / "cinematic" / "kit"

MODELS = ["robot_body", "robot_head", "person_a", "person_b", "arm_a", "arm_b", "table", "bench", "plate", "lamp"]
GLB = {m: base64.b64encode((HERE / "models" / f"{m}.glb").read_bytes()).decode() for m in MODELS}

THREE_CDN = "".join(
    f"<script src='https://cdn.jsdelivr.net/npm/three@0.147.0/{p}.js'></script>"
    for p in ["build/three.min", "examples/js/shaders/CopyShader", "examples/js/shaders/LuminosityHighPassShader",
              "examples/js/postprocessing/EffectComposer", "examples/js/postprocessing/RenderPass",
              "examples/js/postprocessing/ShaderPass", "examples/js/postprocessing/UnrealBloomPass",
              "examples/js/loaders/GLTFLoader"])

STYLE = """<style>
html,body{margin:0;background:#000}
.g{font-family:'Hiragino Sans','Helvetica Neue',sans-serif}
.tel{font-family:'Hiragino Sans',sans-serif;font-weight:900;color:#fff;-webkit-text-stroke:12px #111;paint-order:stroke fill;letter-spacing:.02em}
.tel.y{color:#ffe14d}
.tel.r{color:#fff;-webkit-text-stroke:12px #c4161c}
</style>"""

# ---------------------------------------------------------------- shared scene (pasted into every beat)
SCENE_JS = """
const GLB = __GLB__;
const S = {};
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const b64buf = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0)).buffer;
const loadGLB = (name) => new Promise((res, rej) => new THREE.GLTFLoader().parse(b64buf(GLB[name]), '', (g) => {
  g.scene.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  res(g.scene);
}, rej));
const canvasTex = (w, h, draw, rep) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding;
  if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); }
  t.anisotropy = 8; return t;
};
// film look of a TV reenactment: sepia wash, grain, vignette; uGray turns it monochrome for the freeze-frame
const VTRShader = {
  uniforms: { tDiffuse: { value: null }, uTime: { value: 0 }, uSepia: { value: 1 }, uGray: { value: 0 }, uFlash: { value: 0 }, uDim: { value: 1 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float uTime, uSepia, uGray, uFlash, uDim; varying vec2 vUv;
    float rnd(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + uTime * 37.0) * 43758.5453); }
    void main(){
      vec3 c = texture2D(tDiffuse, vUv).rgb;
      float l = dot(c, vec3(0.299,0.587,0.114));
      vec3 sep = vec3(l) * vec3(1.10, 0.95, 0.78);
      c = mix(c, sep, 0.28 * uSepia);
      c = mix(c, vec3(l) * 1.05, uGray);
      c = (c - 0.5) * (1.0 + 0.25 * uGray) + 0.5;
      c += (rnd(floor(vUv * vec2(640.0,360.0))) - 0.5) * 0.07;
      float v = smoothstep(0.85, 0.3, length((vUv - 0.5) * vec2(1.25, 1.0)));
      c *= mix(0.55, 1.0, v);
      c *= uDim; c = mix(c, vec3(1.0), uFlash);
      gl_FragColor = vec4(c, 1.0);
    }`,
};

async function setup() {
  const { R, scene, cam, composer } = makeRenderer('gl', [0.3, 0.35, 0.96]);
  R.outputEncoding = THREE.sRGBEncoding;   // GLB colours are linear factors
  R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap;
  scene.background = new THREE.Color(0x1a1009);
  scene.fog = new THREE.Fog(0x1a1009, 6, 13);
  cam.fov = 32; cam.updateProjectionMatrix();
  const vtr = new THREE.ShaderPass(VTRShader); composer.addPass(vtr);

  // room: plank floor, slatted back wall, a glowing shoji panel
  const floorTex = canvasTex(1024, 1024, (g, w, h) => {
    for (let i = 0; i < 16; i++) { const k = rnd(i * 3.1); g.fillStyle = `rgb(${92 + 30 * k},${58 + 18 * k},${36 + 10 * k})`; g.fillRect(0, i * 64, w, 62); g.fillStyle = 'rgba(0,0,0,.35)'; g.fillRect(0, i * 64 + 62, w, 2); }
    for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(40,20,10,${0.05 + 0.08 * rnd(i)})`; g.fillRect(rnd(i * 2) * w, rnd(i * 5) * h, 40 + 120 * rnd(i * 7), 1); }
  }, [3, 3]);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), new THREE.MeshStandardMaterial({ map: floorTex, roughness: 0.55 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  const wallTex = canvasTex(1024, 512, (g, w, h) => {
    for (let i = 0; i < 32; i++) { const k = rnd(i * 1.7); g.fillStyle = `rgb(${70 + 22 * k},${44 + 12 * k},${28 + 8 * k})`; g.fillRect(i * 32, 0, 30, h); }
  }, [4, 1]);
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(14, 4), new THREE.MeshStandardMaterial({ map: wallTex, roughness: 0.8 }));
  wall.position.set(0, 2, -5); wall.receiveShadow = true; scene.add(wall);
  const shoji = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.1), new THREE.MeshBasicMaterial({ map: canvasTex(320, 220, (g, w, h) => {
    g.fillStyle = '#ffe2ae'; g.fillRect(0, 0, w, h); g.strokeStyle = '#5a3a22'; g.lineWidth = 6;
    for (let x = 0; x <= w; x += w / 4) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }
    for (let y = 0; y <= h; y += h / 3) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
  }) }));
  shoji.position.set(0.05, 1.9, -4.98); scene.add(shoji);

  // furniture: the two tables of the story in front, two more behind for depth
  const tablePos = [[-1.5, -0.55], [1.6, -0.55], [-1.6, -3.0], [1.5, -3.0]];
  for (const [x, z] of tablePos) {
    const t = await loadGLB('table'); t.position.set(x, 0, z); scene.add(t);
    const b = await loadGLB('bench'); b.position.set(x, 0, z - 0.6); scene.add(b);
    const l = await loadGLB('lamp'); l.position.set(x, 2.05, z); scene.add(l);
    const pl = new THREE.PointLight(0xffb060, 0.9, 4.5, 2); pl.position.set(x, 1.85, z); scene.add(pl);
  }
  // people
  S.pa = await loadGLB('person_a'); S.pa.position.set(-1.15, 0, -1.12); scene.add(S.pa);
  S.paL = await loadGLB('arm_a'); S.paL.position.set(-1.38, 1.0, -1.1); S.paL.quaternion.setFromUnitVectors(V3(1, 0, 0), V3(0.1, -0.45, 0.88).normalize()); scene.add(S.paL);
  S.armA = await loadGLB('arm_a'); scene.add(S.armA);
  S.pb = await loadGLB('person_b'); S.pb.position.set(1.6, 0, -1.12); scene.add(S.pb);
  for (const sx of [-1, 1]) { const a = await loadGLB('arm_b'); a.position.set(1.6 + sx * 0.23, 1.0, -1.1); a.quaternion.setFromUnitVectors(V3(1, 0, 0), V3(-sx * 0.25, -0.45, 0.85).normalize()); scene.add(a); }
  // robot
  S.robot = new THREE.Group(); scene.add(S.robot);
  S.robot.add(await loadGLB('robot_body'));
  S.head = await loadGLB('robot_head'); S.head.position.set(0, 1.36, 0); S.robot.add(S.head);
  S.faceC = document.createElement('canvas'); S.faceC.width = 256; S.faceC.height = 150;
  S.faceT = new THREE.CanvasTexture(S.faceC); S.faceT.encoding = THREE.sRGBEncoding;
  const face = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.235), new THREE.MeshBasicMaterial({ map: S.faceT, transparent: true }));
  face.position.set(0, -0.01, 0.226); S.head.add(face);
  S.alertLight = new THREE.PointLight(0xff2a2a, 0, 2.5, 2); S.alertLight.position.set(0, 0, 0.5); S.head.add(S.alertLight);
  S.rings = [0, 1, 2].map(() => { const m = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.012, 8, 64), new THREE.MeshBasicMaterial({ color: 0xff4040, transparent: true, opacity: 0 })); S.head.add(m); return m; });
  S.plate = await loadGLB('plate'); scene.add(S.plate);
  // steam over the four pots
  const steamTex = dotTex('255,255,255');
  S.steam = [];
  for (const [x, z] of tablePos) for (let k = 0; k < 7; k++) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: steamTex, transparent: true, depthWrite: false, opacity: 0 }));
    sp.userData = { x, z, k }; scene.add(sp); S.steam.push(sp);
  }
  // light: warm key from upper front left with soft shadows, a cool rim, warm fill
  scene.add(new THREE.HemisphereLight(0xffe2c0, 0x2a1a10, 0.55));
  const key = new THREE.DirectionalLight(0xffd6a0, 1.25); key.position.set(-3, 5.5, 4); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5, near: 0.5, far: 20 });
  key.shadow.bias = -0.0004; key.shadow.radius = 4; scene.add(key);
  const rim = new THREE.DirectionalLight(0x9cc8ff, 0.45); rim.position.set(3, 3, -4); scene.add(rim);
  Object.assign(S, { R, scene, cam, composer, vtr });
  return S;
}

// ---------- story state helpers (all pure functions of t)
const SHOULDER = V3(-0.92, 1.02, -1.08);
const ARM_LEN = 0.74;
function robotAt(s) {            // s 0..1: curve in from the front left to beside table A; 1..2: straight on toward table B
  if (s <= 1) {
    const a = [-3.4, 1.9], b = [-0.55, 1.2], c = [-0.5, -0.45], u = s, iu = 1 - u;
    return V3(iu * iu * a[0] + 2 * iu * u * b[0] + u * u * c[0], 0, iu * iu * a[1] + 2 * iu * u * b[1] + u * u * c[1]);
  }
  return V3(-0.5 + (s - 1) * 1.1, 0, -0.45);
}
function setRobot(s, t) {
  const p = robotAt(s); S.robot.position.copy(p);
  S.robot.position.y = Math.abs(Math.sin(t * 9)) * 0.004;
  S.head.rotation.z = Math.sin(t * 2.2) * 0.03;
  return p;
}
const trayPlate = (p) => V3(p.x, 0.742, p.z);   // second tier
function setArm(lean, dir) {      // dir: unit vector the arm points along
  S.pa.rotation.x = lean * 0.22;
  const sh = SHOULDER.clone().add(V3(lean * 0.06, -lean * 0.03, lean * 0.2));
  S.armA.position.copy(sh); S.armA.quaternion.setFromUnitVectors(V3(1, 0, 0), dir);
  return sh.clone().add(dir.clone().multiplyScalar(ARM_LEN));
}
const REST = V3(0.05, -0.25, 0.97).normalize();
const toward = (from, to) => to.clone().sub(from).normalize();
const blendDir = (a, b, k) => a.clone().lerp(b, k).normalize();
function drawFace(mood) {
  const g = S.faceC.getContext('2d'), w = 256, h = 150;
  g.clearRect(0, 0, w, h);
  g.lineWidth = 14; g.lineCap = 'round';
  if (mood === 'alert') {
    g.fillStyle = '#ff3b3b'; g.font = '900 110px Helvetica'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText('!', 82, 80); g.fillText('!', 174, 80);
  } else {
    g.strokeStyle = '#7fe8ff';
    for (const cx of [82, 174]) { g.beginPath(); g.arc(cx, 92, 26, Math.PI * 1.15, Math.PI * 1.85); g.stroke(); }
    g.fillStyle = 'rgba(255,140,170,.55)'; g.beginPath(); g.arc(46, 112, 14, 0, 6.3); g.arc(210, 112, 14, 0, 6.3); g.fill();
  }
  S.faceT.needsUpdate = true;
}
function steam(t) {
  S.steam.forEach((sp) => {
    const { x, z, k } = sp.userData, ph = (t * 0.35 + k / 7 + rnd(x * 3 + z)) % 1;
    sp.position.set(x + Math.sin(ph * 5 + k) * 0.05, 0.95 + ph * 0.7, z + Math.cos(ph * 4 + k) * 0.04);
    const s = 0.12 + ph * 0.35; sp.scale.set(s, s, s); sp.material.opacity = Math.sin(ph * Math.PI) * 0.22;
  });
}
function shoot(t, eye, look) { S.cam.position.copy(eye); S.cam.lookAt(look); S.vtr.uniforms.uTime.value = t; S.composer.render(); }
function project(v) { const p = v.clone().project(S.cam); return [(p.x + 1) * 640, (1 - p.y) * 360]; }
const lerpV = (a, b, k) => a.clone().lerp(b, k);
const shake = (t, k) => V3(Math.sin(t * 1.7) * 0.012 * k + Math.sin(t * 5.1) * 0.004 * k, Math.cos(t * 1.3) * 0.01 * k, 0);
"""


def overlay(inner, label="※再現VTR"):
    return (STYLE + THREE_CDN + "<div class='relative overflow-hidden' style='width:1280px;height:720px;background:#000'>"
            "<canvas id='gl' width='1280' height='720' class='absolute inset-0'></canvas>"
            + inner +
            f"<div class='tel absolute' style='right:28px;top:20px;font-size:26px;-webkit-text-stroke:6px #111'>{label}</div>"
            "</div>")


def beat(bid, text, inner, script, label="※再現VTR"):
    kit = (KIT / "common.js").read_text() + "\n" + (KIT / "three-kit.js").read_text()
    js = kit + SCENE_JS.replace("__GLB__", json.dumps(GLB)) + script
    return {"id": bid, "text": text, "image": {"type": "html_tailwind", "html": overlay(inner, label), "script": js, "animation": {"fps": 30}}}


# 1. establishing crane shot
b1 = beat("open", "2026年、9月。とある、しゃぶしゃぶ店。",
          "<div id='date' class='tel absolute' style='left:60px;top:70px;font-size:44px;opacity:0'>2026年9月</div>"
          "<div id='place' class='tel absolute' style='left:60px;top:130px;font-size:56px;opacity:0'>とある しゃぶしゃぶ店</div>", """
async function render(frame, total, fps) {
  if (!S.R) await setup();
  const t = frame / fps, D = total / fps, k = ease(seg(t, 0, D));
  steam(t); setRobot(-1, t); S.plate.position.set(-9, 0, 0); setArm(0, REST); drawFace('smile');
  S.pb.position.y = 0;
  shoot(t, lerpV(V3(-0.6, 3.4, 5.6), V3(0.2, 1.9, 4.1), k), lerpV(V3(0, 0.6, -1.4), V3(0, 0.9, -0.9), k));
  const a = seg(t, 0.4, 0.9), b = seg(t, 1.0, 1.5);
  el('date').style.opacity = a; el('date').style.transform = `translateX(${-40 * (1 - easeOut(a))}px)`;
  el('place').style.opacity = b; el('place').style.transform = `translateX(${-40 * (1 - easeOut(b))}px)`;
}""")

# 2. tracking the robot as it curves in with the premium meat
b2 = beat("approach", "高級コースの肉を、ネコ型ロボットが運んでくる。……はずだった。",
          "<div id='t1' class='tel y absolute' style='left:0;right:0;bottom:60px;text-align:center;font-size:62px;opacity:0'>高価格帯コースの肉を運ぶ配膳ロボ</div>"
          "<div id='t2' class='tel r absolute' style='left:0;right:0;bottom:60px;text-align:center;font-size:72px;opacity:0'>……はずだった</div>", """
async function render(frame, total, fps) {
  if (!S.R) await setup();
  const t = frame / fps, D = total / fps;
  steam(t); drawFace('smile'); setArm(0, REST);
  const s = 0.92 * easeOut(seg(t, 0, D - 0.8)) ** 1.1, p = setRobot(s, t);
  S.plate.position.copy(trayPlate(p)); S.plate.rotation.y = 0;
  S.pb.position.y = Math.abs(Math.sin(t * 4)) * 0.025;
  const eye = V3(p.x + 1.9, 1.4, p.z + 3.5).add(shake(t, 1)), look = V3(p.x + 0.1, 1.0, p.z - 0.2);
  shoot(t, eye, look);
  el('t1').style.opacity = seg(t, 0.5, 0.9) * (1 - seg(t, D - 1.7, D - 1.5));
  const q = seg(t, D - 1.5, D - 1.2); el('t2').style.opacity = q; el('t2').style.transform = `scale(${1.4 - 0.4 * easeOut(q)})`;
}""")

# 3. the grab, frozen mid-carry
b3 = beat("grab", "その途中、隣の客の手が伸び、肉はそのまま別の席へ。",
          "<svg class='absolute inset-0' width='1280' height='720'><ellipse id='circ' cx='640' cy='360' rx='150' ry='105' fill='none' stroke='#e11' stroke-width='10' stroke-dasharray='1000' stroke-dashoffset='1000' opacity='0'/></svg>"
          "<div id='eh' class='tel y absolute' style='left:0;right:0;bottom:50px;text-align:center;font-size:110px;opacity:0'>えっ……!?</div>", """
const F = 2.0;
function grabState(t) {
  const s = 0.92 + 0.14 * t, p = robotAt(s);
  const reach = seg(t, 0.25, 0.95), back = seg(t, 1.25, 2.4);
  const tp = trayPlate(p);
  let dir, plate;
  if (t < 0.95) { dir = blendDir(REST, toward(SHOULDER, tp), ease(reach)); plate = tp; }
  else { dir = blendDir(toward(SHOULDER, trayPlate(robotAt(0.92 + 0.14 * 0.95))), V3(0.12, -0.3, 0.95).normalize(), ease(back)); plate = null; }
  return { s, p, dir, plate, lean: ease(reach) * (1 - 0.6 * ease(back)) };
}
async function render(frame, total, fps) {
  if (!S.R) await setup();
  const t = frame / fps, tt = Math.min(t, F), g = grabState(tt);
  steam(tt); drawFace('smile');
  setRobot(g.s, tt);
  const hand = setArm(g.lean, g.dir);
  if (g.plate) S.plate.position.copy(g.plate); else S.plate.position.copy(hand.clone().add(V3(0, -0.035, 0)));
  const f = easeOut(seg(t, F, F + 0.6));
  S.vtr.uniforms.uGray.value = t >= F ? 1 : 0;
  S.vtr.uniforms.uFlash.value = flashAfter(t, F, 0.18) * 0.6;
  const hand0 = setArm(grabState(F).lean, grabState(F).dir); setArm(g.lean, g.dir);
  const eyeA = V3(-2.15, 1.35, 1.25).add(shake(tt, 1)), lookA = V3(-0.75, 1.0, -0.7);
  const eyeF = hand0.clone().add(V3(-0.75, 0.2, 0.95));
  shoot(tt, lerpV(eyeA, eyeF, f), lerpV(lookA, hand0, f));
  const [cx, cy] = project(hand0);
  el('circ').setAttribute('cx', cx); el('circ').setAttribute('cy', cy);
  const c = seg(t, F + 0.5, F + 1.1); el('circ').setAttribute('opacity', c > 0 ? 1 : 0); el('circ').setAttribute('stroke-dashoffset', 1000 * (1 - easeOut(c)));
  const e = seg(t, F + 0.8, F + 1.1); el('eh').style.opacity = e; el('eh').style.transform = `scale(${1.5 - 0.5 * back(e)})`;
}""")

# 4. social media: blank post cards floating through the restaurant
b4 = beat("sns", "SNSには同様の投稿が相次ぎ、意図的な横取りを指摘する声も。",
          "<div id='tz' class='tel r absolute' style='left:0;right:0;bottom:60px;text-align:center;font-size:80px;opacity:0'>“横取り”の指摘も</div>", """
let cards = null;
function makeCards() {
  const tex = canvasTex(600, 240, (g, w, h) => {
    g.fillStyle = '#fff'; g.beginPath(); g.roundRect(0, 0, w, h, 34); g.fill();
    g.fillStyle = '#c9ced6'; g.beginPath(); g.arc(70, 70, 40, 0, 6.3); g.fill();
    g.fillStyle = '#9aa1ab'; g.beginPath(); g.roundRect(130, 46, 200, 22, 11); g.fill();
    g.fillStyle = '#d5d9df'; [[130, 96, 420], [130, 136, 380], [40, 176, 300]].forEach(([x, y, ww]) => { g.beginPath(); g.roundRect(x, y, ww, 20, 10); g.fill(); });
  });
  return [...Array(10)].map((_, i) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(0.75, 0.3), new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0, side: THREE.DoubleSide, fog: false }));
    m.userData = { a: i / 10 * Math.PI * 2 + rnd(i) * 0.4, r: 0.75 + rnd(i * 3) * 0.6, y: -0.35 + rnd(i * 5) * 0.95, d: 0.25 + i * 0.22 };
    S.scene.add(m); return m;
  });
}
async function render(frame, total, fps) {
  if (!S.R) await setup();
  if (!cards) cards = makeCards();
  const t = frame / fps; steam(t); drawFace('smile');
  const p = setRobot(1.55, t); setArm(0, REST); S.plate.position.set(-1.05, 0.748, -0.78);
  S.vtr.uniforms.uSepia.value = 1; S.vtr.uniforms.uDim.value = 1 - 0.45 * seg(t, 0, 0.6);
  const ang = -0.5 + t * 0.12, center = V3(-0.3, 1.0, -0.7);
  const eye = center.clone().add(V3(Math.sin(ang) * 3.4, 0.9, Math.cos(ang) * 3.4));
  cards.forEach((m) => {
    const u = m.userData, k = back(seg(t, u.d, u.d + 0.45)), a = u.a + t * 0.25;
    m.position.copy(center.clone().add(V3(Math.cos(a) * u.r, u.y + Math.sin(t * 1.3 + u.a) * 0.05, Math.sin(a) * u.r)));
    m.lookAt(eye); m.scale.setScalar(Math.max(0.001, k)); m.material.opacity = Math.min(1, k);
  });
  shoot(t, eye, center);
  const z = seg(t, 2.6, 2.9); el('tz').style.opacity = z; el('tz').style.transform = `scale(${1.4 - 0.4 * easeOut(z)})`;
}""", label="※イメージ")

# 5. the fix: the robot calls out, the hand withdraws; measures panel
b5 = beat("response", "運営元は謝罪。ほかの客の段の商品を取ろうとすると、ロボットが音声で知らせる機能を、全店に導入するとしています。",
          "<div id='bub' class='g absolute' style='left:0;top:0;padding:16px 24px;border-radius:24px;background:#fff;border:5px solid #c4161c;font-size:36px;font-weight:900;color:#c4161c;opacity:0;white-space:nowrap'>ピピッ！ 音声でお知らせ</div>"
          "<div id='panel' class='g absolute' style='right:40px;top:290px;width:470px;padding:22px 26px;border-radius:18px;background:rgba(255,255,255,.95);opacity:0'>"
          "<div style='font-size:24px;font-weight:900;color:#c4161c'>運営元（すかいらーくHD）の対策</div>"
          "<div class='it' style='font-size:26px;font-weight:700;margin-top:10px;opacity:0'>・利用手順の説明を充実</div>"
          "<div class='it' style='font-size:26px;font-weight:700;margin-top:6px;opacity:0'>・英語・中国語のイラスト掲示</div>"
          "<div class='it' style='font-size:26px;font-weight:700;margin-top:6px;opacity:0'>・誤った段に手 → 音声通知</div>"
          "<div id='all' style='margin-top:14px;font-size:34px;font-weight:900;color:#fff;background:#c4161c;text-align:center;border-radius:10px;padding:6px 0;opacity:0'>全店に導入へ</div></div>"
          "<div class='g absolute' style='left:24px;bottom:16px;font-size:16px;color:#fff;opacity:.85'>出典: J-CASTニュース（2026年10月2日）</div>", """
async function render(frame, total, fps) {
  if (!S.R) await setup();
  const t = frame / fps; steam(t);
  const p = setRobot(1.0, t), tp = trayPlate(p);
  S.plate.position.copy(tp);
  const reach = seg(t, 0.2, 0.9), wd = seg(t, 1.5, 2.1), alert = t > 0.95 && t < 3.0;
  setArm(ease(reach) * 0.8 * (1 - ease(wd)), blendDir(REST, toward(SHOULDER, tp), ease(reach) * 0.85 * (1 - ease(wd))));
  drawFace(alert ? 'alert' : 'smile');
  S.alertLight.intensity = alert ? 2.2 + Math.sin(t * 18) * 0.8 : 0;
  S.rings.forEach((m, i) => { const ph = alert ? ((t - 0.95) * 1.4 + i / 3) % 1 : 0; m.scale.setScalar(0.6 + ph * 2.2); m.material.opacity = alert ? (1 - ph) * 0.8 : 0; });
  const eye = V3(-1.6, 1.5, 2.6).add(shake(t, 0.6)), look = V3(-0.7, 1.05, -0.6);
  shoot(t, eye, look);
  const [hx, hy] = project(V3(p.x, 1.62, p.z));
  const b = seg(t, 0.95, 1.2) * (1 - seg(t, 2.9, 3.2)); el('bub').style.opacity = b;
  el('bub').style.transform = `translate(${hx + 40}px, ${hy - 90}px) scale(${0.6 + 0.4 * back(seg(t, 0.95, 1.25))})`;
  const q = seg(t, 3.0, 3.4); el('panel').style.opacity = q; el('panel').style.transform = `translateX(${60 * (1 - easeOut(q))}px)`;
  document.querySelectorAll('.it').forEach((d, i) => { d.style.opacity = seg(t, 3.5 + i * 0.5, 3.8 + i * 0.5); });
  const a = seg(t, 5.3, 5.6); el('all').style.opacity = a; el('all').style.transform = `scale(${1.3 - 0.3 * back(a)})`;
}""", label="※イメージ")

deck = {
    "$mulmocast": {"version": "1.1"},
    "canvasSize": {"width": 1280, "height": 720},
    "title": "配膳ロボの「横取り」（3D 再現VTR）",
    "description": "robot v1 と同じ記事・ナレーションを、ShapeScript で作ったモデルと three.js の 3D 場面で見せる版。",
    "lang": "ja",
    "speechParams": {"speakers": {"Narrator": {
        "voiceId": "Charon", "isDefault": True, "provider": "gemini", "model": "gemini-3.1-flash-tts-preview",
        "speechOptions": {"instruction": "テレビの再現VTRのナレーター風に、低めの声でドラマチックに、テンポよく読む。"}}}},
    "audioParams": {"bgm": {"kind": "path", "path": str(BGM)}, "bgmVolume": 0.22, "audioVolume": 1.0,
                    "padding": 0.3, "introPadding": 0.5, "closingPadding": 0.6, "outroPadding": 0.8},
    "beats": [b1, b2, b3, b4, b5],
}
(HERE / "robot-3d.json").write_text(json.dumps(deck, ensure_ascii=False, indent=1))
print("wrote", HERE / "robot-3d.json", (HERE / "robot-3d.json").stat().st_size // 1024, "KB")
