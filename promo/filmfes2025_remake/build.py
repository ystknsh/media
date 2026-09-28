#!/usr/bin/env python3
"""Build filmfes2025_remake.json — the AI Short Film Fes 2025 trailer, remade a year later.

A "what if we had made it with today's tools" remake of the 2025 announcement trailer
(../../filmfes2025/script.json): same structure and two voices, polished English narration,
every frame drawn by code written by Claude Opus 5.5. It is not an announcement: dates and
prize amounts are masked as XX on screen and never spoken, and the film opens and closes on
a "2025 REMAKE" slate.

Run from anywhere: python3 build.py
Beat lengths and the cue times inside each beat follow the Gemini narration measured on
2026-09-29 (TIMING / CUES below). If a line changes, regenerate its audio, measure its
pauses again, and move that beat's cues.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30

# (beat id, speaker, narration) — polished from the 2025 English version
LINES = [
    ("open", "Presenter", "Imagine it, and you can see it. When AI can make movies, what will you make?"),
    ("title", "CoHost", "AI Short Film Fes 2025. Powered by MulmoCast."),
    ("theme", "Presenter", "The theme: films made by people and AI, together."),
    # "Any genre. Three minutes or less. Anyone can enter." came back with no audio from Gemini twice
    ("rules", "CoHost", "Any genre, up to three minutes long, and open to everyone."),
    ("prizes", "CoHost", "There's prize money for the Grand Prix, plus Visual, Animation, Documentary, and Promotion awards."),
    ("judge", "Presenter", "Chairing the jury: Satoshi Nakajima of Singularity Society."),
    ("criteria", "CoHost", "Entries are judged on creativity, structure, technical craft, and how convincingly you build a world with AI."),
    ("dates", "CoHost", "Send in your film before the deadline. Winners are announced online."),
    ("experiment", "Presenter", "It's a film festival. It's also an experiment."),
    ("open_q", "CoHost", "Technology and ethics are still full of open questions. That's exactly where the surprises are."),
    ("prompt", "Presenter", "Type a prompt. It's the first step in turning your imagination into film. Now, bring your world to life."),
    ("together", "CoHost", "The future of film begins with you and AI, together."),
    ("close", "Presenter", "AI Short Film Fes 2025, powered by MulmoCast. Take your first step onto the screen."),
]
TEXT = {bid: (spk, txt) for bid, spk, txt in LINES}

SPEAKERS = {
    "Presenter": {
        "provider": "gemini", "model": "gemini-3.1-flash-tts-preview", "voiceId": "Aoede",
        "speechOptions": {"instruction": "A warm, confident film-festival trailer host. Clear and unhurried, with a sense of wonder."},
    },
    "CoHost": {
        "provider": "gemini", "model": "gemini-3.1-flash-tts-preview", "voiceId": "Charon",
        "speechOptions": {"instruction": "A clear, upbeat festival announcer. Crisp and friendly, never shouting."},
    },
}

# seconds per beat (>= its narration) and, per beat, the start time of each spoken phrase (measured)
TIMING = {"slate_in": 2.4, "open": 8.3, "title": 5.4, "theme": 6.3, "rules": 5.2, "prizes": 7.0, "judge": 5.9, "criteria": 8.3, "dates": 5.0, "experiment": 5.6, "open_q": 7.6, "prompt": 9.7, "together": 5.4, "close": 9.9, "slate_out": 4.0}
CUES = {"open": [0.34, 1.83, 3.76, 6.69], "title": [0.33, 3.36], "theme": [0.33, 1.86, 5.23], "rules": [0.33, 1.36, 2.99], "prizes": [1.5, 2.9, 3.6, 4.5, 5.5], "judge": [0.38, 1.99, 3.83], "criteria": [1.6, 2.52, 3.43, 4.6], "dates": [0.3, 2.96], "experiment": [0.6, 3.9], "open_q": [0.32, 4.7], "prompt": [0.33, 1.87, 5.37], "together": [0.32, 3.0], "close": [0.33, 3.93, 6.54]}
ORDER = ["slate_in", "open", "title", "theme", "rules", "prizes", "judge", "criteria", "dates",
         "experiment", "open_q", "prompt", "together", "close", "slate_out"]
TOTAL_FRAMES = sum(math.floor(TIMING[b] * FPS) for b in ORDER)

GOLD, GOLD2, CYAN, BG = "#e9c46a", "#f6e0a0", "#7fd8ff", "#05070b"
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600;800;900&family=JetBrains+Mono:wght@400;600&family=Instrument+Serif:ital@0;1&display=block" rel="stylesheet">'
CSS = f"""<style>
html,body{{background:#000;margin:0;}}
.stage{{position:relative;width:1280px;height:720px;overflow:hidden;background:{BG};color:#f4f1ea;font-family:'Inter Tight',sans-serif;}}
.abs{{position:absolute;}} .full{{position:absolute;left:0;top:0;width:1280px;height:720px;}}
.mono{{font-family:'JetBrains Mono',monospace;}} .serif{{font-family:'Instrument Serif',serif;}}
.gold{{color:{GOLD};}} .cyan{{color:{CYAN};}}
.vig{{position:absolute;inset:0;box-shadow:inset 0 0 200px 60px rgba(0,0,0,.8);pointer-events:none;}}
</style><div class='abs' style='font-family:Inter Tight;font-weight:800;opacity:0'>A<span style='font-family:Instrument Serif;font-style:italic'>A</span><span class='mono'>A</span></div>"""

COMMON_JS = r"""
const el = (id) => document.getElementById(id);
const clamp01 = (t) => Math.max(0, Math.min(1, t));
const seg = (t, a, b) => clamp01((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const ease = (t) => { t = clamp01(t); return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; };
const easeOut = (t) => 1 - Math.pow(1 - clamp01(t), 3);
const easeIn = (t) => Math.pow(clamp01(t), 3);
const back = (t) => { t = clamp01(t); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const fadeInOut = (t, a, b, f = 0.25) => Math.min(seg(t, a, a + f), 1 - seg(t, b - f, b));
const flashAfter = (t, start, dur = 0.12) => (t >= start ? 1 - seg(t, start, start + dur) : 0);
let fontsReady = false;
const waitFonts = async () => { if (!fontsReady) { await document.fonts.ready; fontsReady = true; } };
const rnd = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const pad = (n, w) => String(n).padStart(w, '0');
// fade the whole beat in and out so cuts between beats breathe
const beatFade = (t, D, i = 0.25, o = 0.25) => { el('bf').style.opacity = 1 - Math.min(seg(t, 0, i), 1 - seg(t, D - o, D)); };
// points covering text drawn in a font — targets for particle type
const textTargets = (txt, font, w, h, step, dx = 0, dy = 0) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  g.fillStyle = '#fff'; g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(txt, w / 2, h / 2);
  const d = g.getImageData(0, 0, w, h).data, pts = [];
  for (let y = 0; y < h; y += step) for (let x = 0; x < w; x += step) if (d[(y * w + x) * 4 + 3] > 128) pts.push([x + dx, y + dy]);
  return pts;
};
// tiny code-drawn films, shared by several beats
const miniFilm = (g, k, x, y, w, h, t) => {
  g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip();
  if (k === 0) {
    const sky = g.createLinearGradient(0, y, 0, y + h); sky.addColorStop(0, '#2b1a4d'); sky.addColorStop(0.55, '#ff8a5c'); sky.addColorStop(0.56, '#1b3a5c'); sky.addColorStop(1, '#0a1a2c');
    g.fillStyle = sky; g.fillRect(x, y, w, h);
    g.fillStyle = '#ffd59a'; g.beginPath(); g.arc(x + w * 0.5, y + h * 0.55, h * 0.18, Math.PI, 0); g.fill();
    g.strokeStyle = 'rgba(255,200,150,.6)'; g.lineWidth = Math.max(1, h / 70);
    for (let r = 0; r < 5; r++) { g.beginPath(); for (let i = 0; i <= w; i += 6) { const yy = y + h * (0.62 + r * 0.08) + Math.sin(i * 0.05 + t * 2 + r) * h * 0.02; i ? g.lineTo(x + i, yy) : g.moveTo(x + i, yy); } g.stroke(); }
  } else if (k === 1) {
    g.fillStyle = '#081426'; g.fillRect(x, y, w, h);
    for (let b = 0; b < 12; b++) {
      const bw = w / 12, bh = h * (0.35 + 0.5 * rnd(b * 9.1)), bx = x + b * bw;
      g.fillStyle = '#10243c'; g.fillRect(bx + 1, y + h - bh, bw - 2, bh);
      const s = Math.max(3, h / 30);
      for (let wy = y + h - bh + s * 1.5; wy < y + h - s; wy += s * 2.2) for (let wx = bx + s; wx < bx + bw - s; wx += s * 1.8)
        if (rnd(Math.floor(wx) * 3.3 + Math.floor(wy) * 7.7 + Math.floor(t * 3 + rnd(wx) * 5)) > 0.55) { g.fillStyle = 'rgba(255,214,140,.9)'; g.fillRect(wx, wy, s * 0.7, s); }
    }
  } else if (k === 2) {
    g.fillStyle = '#05060f'; g.fillRect(x, y, w, h);
    for (let i = 0; i < 300; i++) {
      const a = rnd(i) * 6.283 + t * 0.6 + (i % 2) * Math.PI, rr = Math.pow(rnd(i * 5.1), 0.7) * h * 0.55, sw = a + rr / h * 2.5;
      g.fillStyle = `rgba(${180 + 75 * rnd(i * 2)},${170 + 60 * rnd(i * 3)},255,${0.4 + 0.6 * rnd(i * 4)})`;
      g.fillRect(x + w / 2 + Math.cos(sw) * rr * 1.5, y + h / 2 + Math.sin(sw) * rr * 0.6, Math.max(1.5, h / 90), Math.max(1.5, h / 90));
    }
  } else if (k === 3) {
    g.fillStyle = '#071a1f'; g.fillRect(x, y, w, h);
    for (let i = 0; i < 38; i++) {
      const v = 0.2 + 0.8 * Math.abs(Math.sin(i * 0.7 + t * 5) * Math.sin(i * 0.23 + t * 1.3));
      g.fillStyle = `hsl(${170 + i * 2},80%,60%)`; g.fillRect(x + w * 0.04 + i * (w * 0.92) / 38, y + h / 2 - v * h * 0.38, (w * 0.92) / 38 - 2, v * h * 0.76);
    }
  } else {
    const bg = g.createLinearGradient(x, y, x + w, y + h); bg.addColorStop(0, '#1d1236'); bg.addColorStop(1, '#0a1630'); g.fillStyle = bg; g.fillRect(x, y, w, h);
    const cx = x + w * 0.5 + Math.sin(t * 0.8) * w * 0.02;
    g.fillStyle = '#05070c'; g.beginPath(); g.arc(cx, y + h * 0.42, h * 0.2, 0, 6.283); g.fill();
    g.beginPath(); g.ellipse(cx, y + h * 1.02, w * 0.3, h * 0.38, 0, Math.PI, 0); g.fill();
    g.strokeStyle = 'rgba(255,170,120,.9)'; g.lineWidth = Math.max(2, h / 45); g.beginPath(); g.arc(cx, y + h * 0.42, h * 0.2, -1.2, 0.6); g.stroke();
  }
  g.fillStyle = 'rgba(0,0,0,.16)'; for (let yy = y; yy < y + h; yy += 4) g.fillRect(x, yy, w, 1);
  g.restore();
};
"""

THREE_CDN = "".join(
    f"<script src='https://cdn.jsdelivr.net/npm/three@0.147.0/{p}.js'></script>"
    for p in ["build/three.min", "examples/js/shaders/CopyShader", "examples/js/shaders/LuminosityHighPassShader",
              "examples/js/postprocessing/EffectComposer", "examples/js/postprocessing/RenderPass",
              "examples/js/postprocessing/ShaderPass", "examples/js/postprocessing/UnrealBloomPass"]
)
# Lessons from One Year Apart's hologram, kept here: an opaque WebGL canvas (alpha:false), no tone
# mapping so canvas colours pass straight through, bloom threshold above the text colour so letters
# stay sharp, and ring holes whose chamfer is inset along the 45-degree edge (else the hole fills in).
THREE_JS = r"""
const chamfer = (w, h, c) => {
  const s = new THREE.Shape();
  s.moveTo(-w / 2 + c, -h / 2); s.lineTo(w / 2 - c, -h / 2); s.lineTo(w / 2, -h / 2 + c); s.lineTo(w / 2, h / 2 - c);
  s.lineTo(w / 2 - c, h / 2); s.lineTo(-w / 2 + c, h / 2); s.lineTo(-w / 2, h / 2 - c); s.lineTo(-w / 2, -h / 2 + c); s.closePath();
  return s;
};
const fitUV = (g, w, h) => { const p = g.attributes.position, uv = g.attributes.uv; for (let i = 0; i < p.count; i++) uv.setXY(i, p.getX(i) / w + 0.5, p.getY(i) / h + 0.5); uv.needsUpdate = true; return g; };
const ringOf = (w, h, c, th) => { const o = chamfer(w, h, c); o.holes.push(chamfer(w - th * 2, h - th * 2, Math.max(0.001, c - th * 0.4142))); return new THREE.ShapeGeometry(o); };
const dotTex = (rgb) => {
  const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
  const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.3, `rgba(${rgb},.8)`); r.addColorStop(1, `rgba(${rgb},0)`);
  g.fillStyle = r; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c);
};
const makeRenderer = (id, bloom = [0.8, 0.3, 0.95]) => {
  const R = new THREE.WebGLRenderer({ canvas: el(id), antialias: true, alpha: false, preserveDrawingBuffer: true });
  R.setPixelRatio(1); R.setSize(1280, 720, false); R.toneMapping = THREE.NoToneMapping;
  const scene = new THREE.Scene(); const cam = new THREE.PerspectiveCamera(35, 16 / 9, 0.1, 200);
  const composer = new THREE.EffectComposer(R); composer.addPass(new THREE.RenderPass(scene, cam));
  composer.addPass(new THREE.UnrealBloomPass(new THREE.Vector2(1280, 720), bloom[0], bloom[1], bloom[2]));
  return { R, scene, cam, composer };
};
"""


def B(bid, html, script, three=False):
    """One animated beat. `bf` is a black layer used by beatFade()."""
    b = {
        "id": bid,
        "duration": TIMING[bid],
        "image": {
            "type": "html_tailwind",
            "animation": {"fps": FPS},
            "html": FONTS + CSS + (THREE_CDN if three else "") + "<div class='stage'>" + html + "<div id='bf' class='full' style='background:#000;opacity:0'></div></div>",
            "script": COMMON_JS + (THREE_JS if three else "") + f"const D = {TIMING[bid]}; const C = {json.dumps(CUES.get(bid, []))}; const TOTAL_FRAMES = {TOTAL_FRAMES};\n" + script,
        },
    }
    if bid in TEXT:
        b["speaker"], b["text"] = TEXT[bid]
    else:
        b["text"] = ""
    return b


def spans(word, cls, extra=""):
    return "".join(f"<span class='{cls}' style='display:inline-block;{extra}'>{'&nbsp;' if c == ' ' else c}</span>" for c in word)


beats = {}

# ------------------------------------------------------------------ slate_in / slate_out: it is a remake
SLATE_HTML = f"""
<div class='full' style='background:radial-gradient(ellipse at 50% 50%,#10141c 0%,#030406 70%)'></div>
<div id='rule' class='abs' style='left:340px;top:318px;width:600px;height:1px;background:{GOLD};transform-origin:50% 50%;transform:scaleX(0)'></div>
<div id='s1' class='abs mono gold' style='left:0;top:262px;width:1280px;text-align:center;font-size:22px;letter-spacing:.6em;opacity:0'>2025 REMAKE</div>
<div id='s2' class='abs serif' style='left:0;top:338px;width:1280px;text-align:center;font-size:34px;font-style:italic;color:#e8e2d4;opacity:0'>The AI Short Film Fes 2025 trailer, remade a year later.</div>
<div id='s3' class='abs mono' style='left:0;top:410px;width:1280px;text-align:center;font-size:13px;letter-spacing:.24em;color:#8c8f98;opacity:0'>EVERY FRAME DRAWN IN CODE BY CLAUDE OPUS 5.5</div>
__EXTRA__
<div class='vig'></div>
"""
slate_js = """
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  el('rule').style.transform = `scaleX(${easeOut(seg(t, 0.15, 0.9))})`;
  el('s1').style.opacity = seg(t, 0.3, 0.7); el('s1').style.letterSpacing = lerp(0.9, 0.6, easeOut(seg(t, 0.3, 1.2))) + 'em';
  el('s2').style.opacity = seg(t, 0.6, 1.0);
  el('s3').style.opacity = seg(t, 0.9, 1.3);
  __MORE__
  beatFade(t, D, 0.3, 0.45);
}
"""
beats["slate_in"] = B("slate_in", SLATE_HTML.replace("__EXTRA__", ""), slate_js.replace("__MORE__", ""))
beats["slate_out"] = B("slate_out", SLATE_HTML.replace("__EXTRA__", """
<div id='s4' class='abs mono' style='left:0;top:470px;width:1280px;text-align:center;font-size:12px;letter-spacing:.14em;color:#6d7079;opacity:0;line-height:22px'>
NARRATION · GEMINI TTS &nbsp;&nbsp; MUSIC · ELEVENLABS &nbsp;&nbsp; MADE WITH MULMOCAST<br>
DATES AND PRIZE AMOUNTS ARE MASKED (XX) — THIS IS A REMAKE, NOT AN ANNOUNCEMENT
</div>"""), slate_js.replace("__MORE__", "el('s4').style.opacity = seg(t, 1.2, 1.6);"))

# ------------------------------------------------------------------ open: particles become the idea, then a screen
beats["open"] = B("open", """
<canvas id='cv' width='1280' height='720' class='full'></canvas>
<div id='q' class='abs serif' style='left:0;top:560px;width:1280px;text-align:center;font-size:40px;font-style:italic;color:#f4efe2;opacity:0'>What will you make?</div>
<div class='vig'></div>
""", """
const N = 2600; let P = null, T1 = null, T2 = null;
// the screen: a 16:9 outline and a play triangle
const screenPts = () => {
  const pts = [], x0 = 400, y0 = 150, w = 480, h = 270;
  for (let i = 0; i < 900; i++) { const u = i / 900, per = 2 * (w + h), d = u * per;
    pts.push(d < w ? [x0 + d, y0] : d < w + h ? [x0 + w, y0 + d - w] : d < 2 * w + h ? [x0 + w - (d - w - h), y0 + h] : [x0, y0 + h - (d - 2 * w - h)]); }
  for (let i = 0; i < 300; i++) { const u = rnd(i * 3.7), v = rnd(i * 5.3) * (1 - u); pts.push([600 + u * 90, 285 - 50 + v * 100 + u * 50]); }
  return pts;
};
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  if (!P) {
    P = []; for (let i = 0; i < N; i++) P.push([rnd(i), rnd(i + 0.5), rnd(i + 0.7), rnd(i + 0.9)]);
    T1 = textTargets('Imagine', "italic 230px 'Instrument Serif'", 1280, 400, 4, 0, 130);
    T2 = screenPts();
  }
  const c = el('cv'), g = c.getContext('2d');
  g.fillStyle = 'rgba(5,7,11,1)'; g.fillRect(0, 0, 1280, 720);
  g.globalCompositeOperation = 'lighter';
  // galaxy -> "Imagine" on "Imagine it" -> screen on "When AI can make movies"
  const a = ease(seg(t, C[0] - 0.1, C[0] + 1.0)), b = ease(seg(t, C[2] - 0.2, C[2] + 1.1));
  for (let i = 0; i < N; i++) {
    const [r1, r2, r3, r4] = P[i];
    const ang = r1 * 6.283 + t * (0.25 + r3 * 0.3), rad = 60 + Math.pow(r2, 0.6) * 520;
    const gx = 640 + Math.cos(ang) * rad, gy = 360 + Math.sin(ang) * rad * 0.42;
    const p1 = T1[i % T1.length], p2 = T2[i % T2.length];
    const jit = 1.2 * Math.sin(t * 3 + i);
    let x = lerp(gx, p1[0] + jit, a), y = lerp(gy, p1[1], a);
    x = lerp(x, p2[0], b); y = lerp(y, p2[1], b);
    const warm = 0.5 + 0.5 * r4;
    g.fillStyle = `rgba(255,${Math.round(200 + 50 * warm)},${Math.round(150 + 100 * (1 - warm))},${0.35 + 0.5 * r3})`;
    const s = 1.2 + r4 * 1.6; g.fillRect(x, y, s, s);
  }
  g.globalCompositeOperation = 'source-over';
  el('q').style.opacity = seg(t, C[3], C[3] + 0.4);
  el('q').style.transform = `translateY(${lerp(10, 0, easeOut(seg(t, C[3], C[3] + 0.5)))}px)`;
  beatFade(t, D, 0.4, 0.2);
}
""")

# ------------------------------------------------------------------ title: gold type, light leaks, a flare
TITLE = "AI SHORT FILM FES 2025"
beats["title"] = B("title", f"""
<div class='full' style='background:radial-gradient(ellipse at 50% 55%,#1a120a 0%,#050403 70%)'></div>
<div id='lk1' class='abs' style='width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(255,150,60,.35),transparent 60%);filter:blur(10px);mix-blend-mode:screen'></div>
<div id='lk2' class='abs' style='width:700px;height:700px;border-radius:50%;background:radial-gradient(circle,rgba(255,220,140,.25),transparent 60%);filter:blur(10px);mix-blend-mode:screen'></div>
<canvas id='dust' width='1280' height='720' class='full'></canvas>
<div id='tt' class='abs' style='left:0;top:250px;width:1280px;text-align:center;font-size:104px;font-weight:900;letter-spacing:.01em'>{spans(TITLE, 'tl', "background:linear-gradient(100deg,#8a6a2a 0%,#f6e0a0 40%,#fff8e1 50%,#f6e0a0 60%,#8a6a2a 100%);background-size:600px 100%;-webkit-background-clip:text;background-clip:text;color:transparent")}</div>
<div id='fl' class='abs' style='left:0;top:382px;width:1280px;height:4px;background:linear-gradient(90deg,transparent,rgba(255,236,190,.95),transparent);filter:blur(2px);transform-origin:50% 50%'></div>
<div id='pw' class='abs mono' style='left:0;top:414px;width:1280px;text-align:center;font-size:18px;letter-spacing:.5em;color:{GOLD};opacity:0'>POWERED BY MULMOCAST</div>
<div class='vig'></div>
""", """
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  document.querySelectorAll('.tl').forEach((sp, i) => {
    const p = easeOut(seg(t, C[0] - 0.1 + i * 0.025, C[0] + 0.5 + i * 0.025));
    sp.style.opacity = p; sp.style.transform = `translateY(${(1 - p) * 30}px)`;
    sp.style.backgroundPosition = `${lerp(-500, 700, seg(t, 0, D)) - sp.offsetLeft}px 0`;
  });
  el('lk1').style.left = lerp(-200, 500, seg(t, 0, D)) + 'px'; el('lk1').style.top = lerp(-250, -150, seg(t, 0, D)) + 'px';
  el('lk2').style.left = lerp(800, 400, seg(t, 0, D)) + 'px'; el('lk2').style.top = lerp(200, 150, seg(t, 0, D)) + 'px';
  const f = easeOut(seg(t, C[0] + 0.3, C[0] + 0.9));
  el('fl').style.transform = `scaleX(${f})`; el('fl').style.opacity = 0.9 * f * (1 - 0.6 * seg(t, C[0] + 1.2, D));
  el('pw').style.opacity = seg(t, C[1], C[1] + 0.4); el('pw').style.letterSpacing = lerp(0.8, 0.5, easeOut(seg(t, C[1], C[1] + 0.9))) + 'em';
  const g = el('dust').getContext('2d'); g.clearRect(0, 0, 1280, 720);
  for (let i = 0; i < 160; i++) {
    const x = (rnd(i) * 1400 + t * 18 * (0.3 + rnd(i * 2))) % 1400 - 60, y = rnd(i * 3) * 720 + Math.sin(t + i) * 8;
    g.fillStyle = `rgba(255,220,160,${0.15 + 0.5 * rnd(i * 4)})`; const s = 1 + 2.5 * rnd(i * 5); g.fillRect(x, y, s, s);
  }
  beatFade(t, D, 0.2, 0.25);
}
""")

# ------------------------------------------------------------------ theme: a hand-drawn line and an exact one meet
beats["theme"] = B("theme", f"""
<div class='full' style='background:radial-gradient(ellipse at 50% 45%,#0e1520 0%,#040507 70%)'></div>
<svg class='full' viewBox='0 0 1280 720'>
  <path id='hum' fill='none' stroke='{GOLD2}' stroke-width='5' stroke-linecap='round' stroke-linejoin='round' style='filter:drop-shadow(0 0 8px rgba(246,224,160,.6))'/>
  <path id='ai' fill='none' stroke='{CYAN}' stroke-width='3' stroke-linecap='square' style='filter:drop-shadow(0 0 8px rgba(127,216,255,.7))'/>
  <circle id='ring' cx='640' cy='330' r='10' fill='none' stroke='#fff' stroke-width='2' opacity='0'/>
</svg>
<div id='l1' class='abs serif' style='left:120px;top:250px;font-size:44px;font-style:italic;color:{GOLD2};opacity:0'>people</div>
<div id='l2' class='abs mono' style='right:130px;top:258px;font-size:28px;letter-spacing:.2em;color:{CYAN};opacity:0'>AI</div>
<div id='cap' class='abs serif' style='left:0;top:470px;width:1280px;text-align:center;font-size:46px;font-style:italic;color:#f4efe2;opacity:0'>films made by people and AI, together</div>
<canvas id='sp' width='1280' height='720' class='full' style='pointer-events:none'></canvas>
<div class='vig'></div>
""", """
let built = false, LH = 0, LA = 0;
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  if (!built) {
    // the human line wanders; the AI line is exact right angles and one arc
    let d = 'M 90 360';
    for (let i = 1; i <= 60; i++) { const x = 90 + i * 9.1, y = 330 + Math.sin(i * 0.35) * 40 + (rnd(i) - 0.5) * 16 + (1 - i / 60) * 30; d += ` L ${x.toFixed(1)} ${y.toFixed(1)}`; }
    el('hum').setAttribute('d', d);
    el('ai').setAttribute('d', 'M 1190 400 L 1060 400 L 1060 300 L 900 300 A 60 60 0 0 0 840 360 L 760 360 L 760 330 L 646 330');
    LH = el('hum').getTotalLength(); LA = el('ai').getTotalLength(); built = true;
  }
  const pa = ease(seg(t, 0.2, C[2]));          // both lines reach the centre on "together"
  el('hum').style.strokeDasharray = LH; el('hum').style.strokeDashoffset = LH * (1 - pa);
  el('ai').style.strokeDasharray = LA; el('ai').style.strokeDashoffset = LA * (1 - pa);
  el('l1').style.opacity = seg(t, 0.5, 0.9); el('l2').style.opacity = seg(t, 0.5, 0.9);
  // they meet on "together"
  const m = C[2];
  const r = easeOut(seg(t, m, m + 1.0));
  el('ring').setAttribute('r', 10 + r * 220); el('ring').setAttribute('opacity', t >= m ? (1 - r) * 0.9 : 0);
  el('cap').style.opacity = seg(t, C[0] + 0.2, C[0] + 0.7);
  const g = el('sp').getContext('2d'); g.clearRect(0, 0, 1280, 720);
  if (t >= m) {
    g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 140; i++) {
      const a = rnd(i) * 6.283, v = 80 + 260 * rnd(i * 2), k = easeOut(seg(t, m, m + 1.2));
      const x = 640 + Math.cos(a) * v * k, y = 330 + Math.sin(a) * v * k * 0.8;
      g.fillStyle = i % 2 ? `rgba(246,224,160,${1 - k})` : `rgba(127,216,255,${1 - k})`; g.fillRect(x, y, 3, 3);
    }
    g.globalCompositeOperation = 'source-over';
    const fl = flashAfter(t, m, 0.25); g.fillStyle = `rgba(255,255,255,${0.35 * fl})`; g.fillRect(0, 0, 1280, 720);
  }
  beatFade(t, D, 0.2, 0.25);
}
""")

# ------------------------------------------------------------------ rules: three statements, each with its own picture
beats["rules"] = B("rules", f"""
<div class='full' style='background:#06080c'></div>
<div class='abs' style='left:80px;top:150px;width:1120px;display:flex;justify-content:space-between'>
  <div id='k1' style='width:340px;opacity:0'><canvas id='g1' width='340' height='200' style='border-radius:8px;border:1px solid #2a3140'></canvas><div class='mono gold' style='margin-top:26px;font-size:15px;letter-spacing:.3em'>GENRE</div><div style='font-size:52px;font-weight:900;line-height:1.05'>ANY</div></div>
  <div id='k2' style='width:340px;opacity:0'><svg width='340' height='200' viewBox='0 0 340 200'><circle cx='170' cy='100' r='84' fill='none' stroke='#1c2330' stroke-width='10'/><circle id='arc' cx='170' cy='100' r='84' fill='none' stroke='{GOLD}' stroke-width='10' stroke-linecap='round' transform='rotate(-90 170 100)'/><text id='clk' x='170' y='114' text-anchor='middle' font-family='JetBrains Mono' font-size='40' fill='#f4efe2'>0:00</text></svg><div class='mono gold' style='margin-top:26px;font-size:15px;letter-spacing:.3em'>LENGTH</div><div style='font-size:52px;font-weight:900;line-height:1.05'>UP TO 3:00</div></div>
  <div id='k3' style='width:340px;opacity:0'><canvas id='g3' width='340' height='200'></canvas><div class='mono gold' style='margin-top:26px;font-size:15px;letter-spacing:.3em'>WHO</div><div style='font-size:52px;font-weight:900;line-height:1.05'>EVERYONE</div></div>
</div>
<div class='vig'></div>
""", """
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  [['k1', C[0]], ['k2', C[1]], ['k3', C[2]]].forEach(([id, c]) => {
    const p = easeOut(seg(t, c - 0.15, c + 0.35)); el(id).style.opacity = p; el(id).style.transform = `translateY(${(1 - p) * 26}px)`;
  });
  // any genre: the little films cut every 0.4 s
  const g1 = el('g1').getContext('2d'); miniFilm(g1, Math.floor(Math.max(0, t - C[0]) / 0.4) % 5, 0, 0, 340, 200, t);
  // up to three minutes: a clock that runs to 3:00
  const k = easeOut(seg(t, C[1], C[1] + 1.3)), secs = Math.round(k * 180), L = 2 * Math.PI * 84;
  el('arc').setAttribute('stroke-dasharray', L); el('arc').setAttribute('stroke-dashoffset', L * (1 - k));
  el('clk').textContent = Math.floor(secs / 60) + ':' + pad(secs % 60, 2);
  // everyone: people light up across a crowd
  const g3 = el('g3').getContext('2d'); g3.clearRect(0, 0, 340, 200);
  for (let r = 0; r < 5; r++) for (let q = 0; q < 12; q++) {
    const i = r * 12 + q, on = t >= C[2] + rnd(i) * 0.9, x = 16 + q * 27 + (r % 2) * 13, y = 22 + r * 38;
    g3.fillStyle = on ? (rnd(i * 7) > 0.5 ? '#f6e0a0' : '#7fd8ff') : '#1c2330';
    g3.beginPath(); g3.arc(x, y, 7, 0, 6.283); g3.fill(); g3.beginPath(); g3.ellipse(x, y + 18, 10, 8, 0, Math.PI, 0); g3.fill();
  }
  beatFade(t, D, 0.2, 0.25);
}
""")

# ------------------------------------------------------------------ prizes: award cards in 3D, amounts masked
AWARDS = ["GRAND PRIX", "VISUAL", "ANIMATION", "DOCUMENTARY", "PROMOTION"]
beats["prizes"] = B("prizes", f"""
<canvas id='gl' width='1280' height='720' class='full'></canvas>
<div id='pool' class='abs mono' style='left:0;top:44px;width:1280px;text-align:center;font-size:16px;letter-spacing:.4em;color:{GOLD};opacity:0'>PRIZE POOL · ¥XX</div>
""", """
const AW = __AW__; let S = null;
const cardTex = (name, grand) => {
  const c = document.createElement('canvas'); c.width = 512; c.height = 720; const g = c.getContext('2d');
  const bg = g.createLinearGradient(0, 0, 512, 720); bg.addColorStop(0, grand ? '#2a1d08' : '#0b1622'); bg.addColorStop(1, grand ? '#120c03' : '#050a10');
  g.fillStyle = bg; g.fillRect(0, 0, 512, 720);
  g.strokeStyle = grand ? '#f6d98b' : '#c9a24e'; g.lineWidth = 10; g.strokeRect(22, 22, 468, 676); g.lineWidth = 2; g.strokeRect(44, 44, 424, 632);
  g.fillStyle = grand ? '#f6e0a0' : '#e6cf95'; g.textAlign = 'center';
  g.font = "600 30px 'JetBrains Mono'"; g.fillText(grand ? 'AI SHORT FILM FES 2025' : 'AWARD', 256, 130);
  const words = name.split(' ');
  words.forEach((w, i) => {
    let fs = grand ? 92 : 64; g.font = `900 ${fs}px 'Inter Tight'`;
    while (g.measureText(w).width > 400) { fs -= 2; g.font = `900 ${fs}px 'Inter Tight'`; }
    g.fillText(w, 256, 330 + i * (grand ? 100 : 74) - (words.length - 1) * 40);
  });
  g.font = "800 56px 'Inter Tight'"; g.fillStyle = '#fff4d6'; g.fillText('¥XX', 256, 590);
  const t = new THREE.CanvasTexture(c); t.anisotropy = 8; return t;
};
const setup = () => {
  const s = makeRenderer('gl', [0.9, 0.35, 0.93]);
  s.scene.background = new THREE.Color(0x05060a); s.scene.fog = new THREE.FogExp2(0x05060a, 0.03);
  s.scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const key = new THREE.PointLight(0xffd79a, 2.2, 30); key.position.set(0, 3, 6); s.scene.add(key);
  s.cards = AW.map((name, i) => {
    const grand = i === 0, w = grand ? 2.3 : 1.7, h = w * 720 / 512;
    const face = new THREE.MeshBasicMaterial({ map: cardTex(name, grand), fog: false });
    const edge = new THREE.MeshStandardMaterial({ color: grand ? 0xf6d98b : 0xc9a24e, metalness: 1, roughness: 0.25, emissive: grand ? 0x6b4a10 : 0x3a2a0a });
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.06), [edge, edge, edge, edge, face, edge]);
    s.scene.add(m); return m;
  });
  const N = 700, pos = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) { pos[i * 3] = (rnd(i) - 0.5) * 24; pos[i * 3 + 1] = (rnd(i + 0.3) - 0.5) * 14; pos[i * 3 + 2] = -rnd(i + 0.6) * 18; }
  const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  s.dust = new THREE.Points(pg, new THREE.PointsMaterial({ size: 0.09, map: dotTex('255,215,140'), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  s.scene.add(s.dust);
  return s;
};
// where each card settles: the Grand Prix in front, four in an arc behind
const HOME = [[0, 0.1, 1.2, 0], [-5.0, 0.35, -1.2, 0.32], [-2.65, 0.75, -1.8, 0.14], [2.65, 0.75, -1.8, -0.14], [5.0, 0.35, -1.2, -0.32]];
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  if (!S) S = setup();
  S.cards.forEach((m, i) => {
    const a = C[i] - 0.25, k = easeOut(seg(t, a, a + 0.9)), [x, y, z, ry] = HOME[i];
    m.position.set(lerp(x * 2.2, x, k), lerp(y - 4, y, k) + Math.sin(t * 1.2 + i) * 0.05, lerp(z - 14, z, k));
    m.rotation.set(lerp(-0.6, 0, k), ry + lerp(Math.PI * 1.5, 0, k) + Math.sin(t * 0.7 + i) * 0.04, 0);
    m.visible = t >= a;
  });
  S.dust.rotation.y = t * 0.03; S.dust.position.y = t * 0.08;
  S.cam.position.set(lerp(0.4, -0.3, seg(t, 0, D)), lerp(0.3, 0.1, seg(t, 0, D)), lerp(10.5, 9.4, ease(seg(t, 0, D))));
  S.cam.lookAt(0, 0.4, 0);
  S.composer.render();
  el('pool').style.opacity = seg(t, 0.3, 0.8);
  beatFade(t, D, 0.2, 0.25);
}
""".replace("__AW__", json.dumps(AWARDS)), three=True)

# ------------------------------------------------------------------ judge: the chair of the jury, typeset
beats["judge"] = B("judge", f"""
<div class='full' style='background:linear-gradient(90deg,#07080b 0%,#0c0e13 100%)'></div>
<div id='ph' class='abs' style='left:520px;top:100px;width:700px;height:394px;overflow:hidden;border-radius:4px;box-shadow:0 30px 70px rgba(0,0,0,.6)'>
  <img id='img' src='assets/judge.png' style='width:700px;height:394px;object-fit:cover;transform-origin:62% 45%'>
  <div class='abs' style='inset:0;background:linear-gradient(90deg,rgba(7,8,11,.35),transparent 30%)'></div>
</div>
<div id='r1' class='abs' style='left:80px;top:230px;width:360px;height:2px;background:{GOLD};transform-origin:0 50%;transform:scaleX(0)'></div>
<div id='j1' class='abs mono gold' style='left:80px;top:196px;font-size:15px;letter-spacing:.34em;opacity:0'>CHAIR OF THE JURY</div>
<div id='j2' class='abs serif' style='left:76px;top:252px;font-size:66px;line-height:1.02;color:#f4efe2;opacity:0'>Satoshi<br>Nakajima</div>
<div id='j3' class='abs' style='left:80px;top:410px;font-size:22px;font-weight:600;color:#b9b3a6;opacity:0'>Singularity Society</div>
<div class='vig'></div>
""", """
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  const w = easeOut(seg(t, 0.05, 0.8));
  el('ph').style.clipPath = `inset(0 ${(1 - w) * 100}% 0 0)`;
  el('img').style.transform = `scale(${lerp(1.12, 1.02, seg(t, 0, D))})`;
  el('r1').style.transform = `scaleX(${easeOut(seg(t, 0.2, 0.8))})`;
  el('j1').style.opacity = seg(t, 0.25, 0.55);
  const n = easeOut(seg(t, C[1] - 0.15, C[1] + 0.45)); el('j2').style.opacity = n; el('j2').style.transform = `translateX(${(1 - n) * -24}px)`;
  el('j3').style.opacity = seg(t, C[2] - 0.1, C[2] + 0.3);
  beatFade(t, D, 0.2, 0.25);
}
""")

# ------------------------------------------------------------------ criteria: four ideas on one network
CRIT = ["CREATIVITY", "STRUCTURE", "TECHNICAL CRAFT", "A CONVINCING WORLD"]
HUBS = [[300, 250], [960, 220], [360, 520], [930, 500]]
beats["criteria"] = B("criteria", f"""
<canvas id='cv' width='1280' height='720' class='full'></canvas>
{''.join(f"<div id='w{i}' class='abs' style='left:{x - 250}px;top:{y + 26}px;width:500px;text-align:center;font-size:34px;font-weight:900;letter-spacing:.06em;color:#f4f8fb;opacity:0;text-shadow:0 0 18px rgba(127,216,255,.6)'>{w}</div>" for i, (w, (x, y)) in enumerate(zip(CRIT, HUBS)))}
<div class='vig'></div>
""", """
const HUBS = __HUBS__;
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  const g = el('cv').getContext('2d');
  g.fillStyle = '#04070c'; g.fillRect(0, 0, 1280, 720);
  const N = 70, pts = [];
  for (let i = 0; i < N; i++) pts.push([rnd(i) * 1280 + Math.sin(t * 0.4 + i) * 20, rnd(i + 0.5) * 720 + Math.cos(t * 0.35 + i * 1.3) * 16]);
  g.lineWidth = 1;
  for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {
    const dx = pts[i][0] - pts[j][0], dy = pts[i][1] - pts[j][1], d = Math.hypot(dx, dy);
    if (d < 170) { g.strokeStyle = `rgba(90,150,200,${0.18 * (1 - d / 170)})`; g.beginPath(); g.moveTo(...pts[i]); g.lineTo(...pts[j]); g.stroke(); }
  }
  pts.forEach((p) => { g.fillStyle = 'rgba(140,200,240,.5)'; g.fillRect(p[0] - 1.5, p[1] - 1.5, 3, 3); });
  // hubs switch on with their word; each new hub wires itself to the ones already lit
  const on = HUBS.map((_, i) => seg(t, C[i] - 0.1, C[i] + 0.35));
  for (let i = 0; i < 4; i++) for (let j = 0; j < i; j++) {
    const k = easeOut(seg(t, C[i], C[i] + 0.6)); if (k <= 0) continue;
    const [x1, y1] = HUBS[j], [x2, y2] = HUBS[i];
    g.strokeStyle = `rgba(127,216,255,${0.75})`; g.lineWidth = 2; g.beginPath(); g.moveTo(x1, y1); g.lineTo(lerp(x1, x2, k), lerp(y1, y2, k)); g.stroke();
  }
  const all = t >= C[3] + 0.8 ? 0.5 + 0.5 * Math.sin((t - C[3]) * 6) : 0;
  HUBS.forEach(([x, y], i) => {
    const k = on[i]; if (k <= 0) return;
    const r = 10 + 6 * back(k) + all * 6, gr = g.createRadialGradient(x, y, 0, x, y, r * 4);
    gr.addColorStop(0, 'rgba(200,240,255,.9)'); gr.addColorStop(1, 'rgba(127,216,255,0)');
    g.fillStyle = gr; g.beginPath(); g.arc(x, y, r * 4, 0, 6.283); g.fill();
    g.fillStyle = '#eaf9ff'; g.beginPath(); g.arc(x, y, r * 0.6, 0, 6.283); g.fill();
    el('w' + i).style.opacity = k; el('w' + i).style.transform = `translateY(${(1 - k) * 12}px)`;
  });
  beatFade(t, D, 0.2, 0.25);
}
""".replace("__HUBS__", json.dumps(HUBS)))

# ------------------------------------------------------------------ dates: a split-flap board, masked
ROWS = [("ENTRIES CLOSE", "XX.XX"), ("WINNERS ANNOUNCED", "XX.XX  ONLINE")]
flap_rows = "".join(
    f"<div class='abs mono gold' style='left:220px;top:{200 + r * 170}px;font-size:16px;letter-spacing:.34em'>{label}</div>"
    f"<div class='abs' style='left:220px;top:{232 + r * 170}px;display:flex;gap:8px'>"
    + "".join(f"<div class='fl' data-r='{r}' data-c='{c}' data-v='{ch}' style='width:58px;height:84px;border-radius:6px;background:linear-gradient(#171b22 49%,#0c0f14 51%);box-shadow:inset 0 -1px 0 #000,0 6px 14px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;font-family:JetBrains Mono;font-weight:600;font-size:52px;color:#f4efe2;position:relative;overflow:hidden'><span></span><div style='position:absolute;left:0;top:41px;width:58px;height:2px;background:#000'></div></div>" for c, ch in enumerate(value))
    + "</div>"
    for r, (label, value) in enumerate(ROWS)
)
beats["dates"] = B("dates", f"""
<div class='full' style='background:radial-gradient(ellipse at 50% 40%,#12151c 0%,#05060a 70%)'></div>
{flap_rows}
<div id='yr' class='abs serif gold' style='right:90px;top:120px;font-size:120px;font-style:italic;opacity:0'>2025</div>
<div class='vig'></div>
""", """
const CH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.';
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  document.querySelectorAll('.fl').forEach((f) => {
    const r = +f.dataset.r, c = +f.dataset.c, v = f.dataset.v, settle = C[r] + 0.25 + c * 0.07, start = C[r] - 0.35;
    const sp = f.querySelector('span');
    if (t < start) { sp.textContent = ''; f.style.opacity = 0.35; return; }
    f.style.opacity = 1;
    if (t >= settle || v === ' ') { sp.textContent = v === ' ' ? '' : v; sp.style.transform = 'scaleY(1)'; return; }
    const step = Math.floor(t * 22), ph = (t * 22) % 1;
    sp.textContent = CH[Math.floor(rnd(step * 13 + r * 7 + c) * CH.length)];
    sp.style.transform = `scaleY(${0.25 + 0.75 * Math.abs(Math.cos(ph * Math.PI))})`;
  });
  el('yr').style.opacity = 0.9 * seg(t, 0.2, 0.7);
  beatFade(t, D, 0.2, 0.25);
}
""")

# ------------------------------------------------------------------ experiment: film strip over a circuit board
beats["experiment"] = B("experiment", f"""
<div class='full' style='background:#040608'></div>
<svg id='cir' class='full' viewBox='0 0 1280 720' style='mix-blend-mode:screen'></svg>
<div id='strip' class='abs' style='left:0;top:250px;height:220px;display:flex;background:#0b0b0b;border-top:1px solid #222;border-bottom:1px solid #222'></div>
<div id='w1' class='abs' style='left:0;top:120px;width:1280px;text-align:center;font-size:60px;font-weight:900;letter-spacing:.02em;opacity:0'>A FILM FESTIVAL.</div>
<div id='w2' class='abs mono cyan' style='left:0;top:520px;width:1280px;text-align:center;font-size:44px;letter-spacing:.2em;opacity:0'>AN EXPERIMENT.</div>
<div class='vig'></div>
""", """
let built = false; const FR = 9;
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  if (!built) {
    let h = '';
    for (let i = 0; i < FR; i++) h += `<div style='width:300px;height:220px;flex:none;position:relative;background:repeating-linear-gradient(90deg,transparent 0 14px,#0b0b0b 14px 20px) 0 0/300px 20px repeat-x,repeating-linear-gradient(90deg,#d8cfbd 0 10px,transparent 10px 20px) 0 5px/300px 10px repeat-x'><canvas class='fc' width='270' height='160' style='position:absolute;left:15px;top:30px'></canvas><div style='position:absolute;left:0;bottom:4px;width:300px;height:10px;background:repeating-linear-gradient(90deg,#d8cfbd 0 10px,transparent 10px 20px)'></div></div>`;
    el('strip').innerHTML = h;
    let s = '';
    for (let i = 0; i < 26; i++) {
      let x = Math.round(rnd(i) * 32) * 40, y = Math.round(rnd(i + 0.4) * 18) * 40, d = `M ${x} ${y}`;
      for (let k = 0; k < 6; k++) { if (rnd(i * 9 + k) > 0.5) x += (rnd(i * 3 + k) > 0.5 ? 1 : -1) * 120; else y += (rnd(i * 5 + k) > 0.5 ? 1 : -1) * 80; d += ` L ${x} ${y}`; }
      s += `<path class='tr' d='${d}' fill='none' stroke='#39b8ff' stroke-width='2' opacity='.7'/><circle cx='${x}' cy='${y}' r='5' fill='#7fd8ff' class='nd' opacity='0'/>`;
    }
    el('cir').innerHTML = s; built = true;
  }
  el('strip').style.transform = `translateX(${-150 - t * 120}px) rotate(-3deg)`;
  document.querySelectorAll('.fc').forEach((c, i) => miniFilm(c.getContext('2d'), i % 5, 0, 0, 270, 160, t + i));
  document.querySelectorAll('.tr').forEach((p, i) => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L * (1 - easeOut(seg(t, C[1] - 0.3 + i * 0.03, C[1] + 0.8 + i * 0.03))); });
  document.querySelectorAll('.nd').forEach((n, i) => n.setAttribute('opacity', seg(t, C[1] + 0.6 + i * 0.03, C[1] + 0.8 + i * 0.03)));
  el('w1').style.opacity = seg(t, C[0] - 0.1, C[0] + 0.3);
  const k = easeOut(seg(t, C[1] - 0.05, C[1] + 0.4)); el('w2').style.opacity = k; el('w2').style.letterSpacing = lerp(0.6, 0.2, k) + 'em';
  beatFade(t, D, 0.2, 0.25);
}
""")

# ------------------------------------------------------------------ open questions: a maze whose walls fall into a dawn
beats["open_q"] = B("open_q", """
<canvas id='cv' width='1280' height='720' class='full'></canvas>
<div id='w1' class='abs serif' style='left:0;top:90px;width:1280px;text-align:center;font-size:46px;font-style:italic;color:#f4efe2;opacity:0'>open questions</div>
<div id='w2' class='abs serif' style='left:0;top:90px;width:1280px;text-align:center;font-size:46px;font-style:italic;color:#fff3d6;opacity:0'>that's where the surprises are</div>
<div class='vig'></div>
""", """
const GW = 24, GH = 12, CS = 40, OX = 160, OY = 180; let WALLS = null, PATH = null;
const buildMaze = () => {
  const vis = new Array(GW * GH).fill(false), walls = new Set();
  for (let y = 0; y < GH; y++) for (let x = 0; x < GW; x++) { walls.add(`h${x},${y}`); walls.add(`v${x},${y}`); }
  const stack = [[0, 0]]; vis[0] = true; let s = 1;
  while (stack.length) {
    const [x, y] = stack[stack.length - 1];
    const nb = [[1, 0], [-1, 0], [0, 1], [0, -1]].map(([dx, dy]) => [x + dx, y + dy, dx, dy]).filter(([nx, ny]) => nx >= 0 && ny >= 0 && nx < GW && ny < GH && !vis[ny * GW + nx]);
    if (!nb.length) { stack.pop(); continue; }
    const [nx, ny, dx, dy] = nb[Math.floor(rnd(s++) * nb.length)];
    if (dx === 1) walls.delete(`v${x + 1},${y}`); if (dx === -1) walls.delete(`v${x},${y}`);
    if (dy === 1) walls.delete(`h${x},${y + 1}`); if (dy === -1) walls.delete(`h${x},${y}`);
    vis[ny * GW + nx] = true; stack.push([nx, ny]);
  }
  const list = [];
  walls.forEach((w) => { const [x, y] = w.slice(1).split(',').map(Number); list.push(w[0] === 'h' ? [OX + x * CS, OY + y * CS, OX + (x + 1) * CS, OY + y * CS] : [OX + x * CS, OY + y * CS, OX + x * CS, OY + (y + 1) * CS]); });
  for (let x = 0; x < GW; x++) list.push([OX + x * CS, OY + GH * CS, OX + (x + 1) * CS, OY + GH * CS]);
  for (let y = 0; y < GH; y++) list.push([OX + GW * CS, OY + y * CS, OX + GW * CS, OY + (y + 1) * CS]);
  return list;
};
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  if (!WALLS) WALLS = buildMaze();
  const g = el('cv').getContext('2d');
  // the dawn behind the maze, revealed as the walls fall
  const open = seg(t, C[1] - 0.1, C[1] + 1.6);
  const sky = g.createLinearGradient(0, 0, 0, 720);
  sky.addColorStop(0, `rgb(${lerp(6, 40, open)},${lerp(8, 30, open)},${lerp(14, 70, open)})`);
  sky.addColorStop(0.62, `rgb(${lerp(8, 255, open)},${lerp(10, 150, open)},${lerp(18, 90, open)})`);
  sky.addColorStop(0.63, `rgb(${lerp(6, 30, open)},${lerp(8, 34, open)},${lerp(12, 60, open)})`); sky.addColorStop(1, '#05070b');
  g.fillStyle = sky; g.fillRect(0, 0, 1280, 720);
  if (open > 0) {
    const sy = lerp(520, 440, easeOut(open));
    const sun = g.createRadialGradient(640, sy, 0, 640, sy, 260); sun.addColorStop(0, `rgba(255,236,190,${open})`); sun.addColorStop(0.2, `rgba(255,190,110,${0.7 * open})`); sun.addColorStop(1, 'rgba(255,150,80,0)');
    g.fillStyle = sun; g.fillRect(0, 0, 1280, 720);
    g.save(); g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 14; i++) { const a = -Math.PI / 2 + (i - 6.5) * 0.16; g.strokeStyle = `rgba(255,220,160,${0.08 * open})`; g.lineWidth = 30; g.beginPath(); g.moveTo(640, sy); g.lineTo(640 + Math.cos(a) * 900, sy + Math.sin(a) * 900); g.stroke(); }
    g.restore();
  }
  // walls draw in from the entrance, then fall away on "That's exactly where the surprises are"
  g.lineCap = 'round';
  WALLS.forEach((w, i) => {
    const d = Math.hypot(w[0] - OX, w[1] - OY) / 1100;
    const drawn = seg(t, 0.1 + d * 1.6, 0.3 + d * 1.6); if (drawn <= 0) return;
    const fall = easeIn(seg(t, C[1] + rnd(i) * 0.9, C[1] + 0.6 + rnd(i) * 0.9));
    g.save(); g.translate((w[0] + w[2]) / 2, (w[1] + w[3]) / 2 + fall * 500); g.rotate(fall * (rnd(i * 3) - 0.5) * 3);
    g.strokeStyle = `rgba(160,190,220,${0.85 * drawn * (1 - fall)})`; g.lineWidth = 3;
    g.beginPath(); g.moveTo((w[0] - w[2]) / 2 * drawn, (w[1] - w[3]) / 2 * drawn); g.lineTo((w[2] - w[0]) / 2 * drawn, (w[3] - w[1]) / 2 * drawn); g.stroke(); g.restore();
  });
  el('w1').style.opacity = seg(t, C[0] + 0.2, C[0] + 0.6) * (1 - seg(t, C[1] - 0.3, C[1]));
  el('w2').style.opacity = seg(t, C[1] + 0.4, C[1] + 0.9);
  beatFade(t, D, 0.2, 0.25);
}
""")

# ------------------------------------------------------------------ prompt: the 2025 prompt, typed, becomes the scene
PROMPT = "At dawn by the sea, particles of light melt into the waves"
beats["prompt"] = B("prompt", f"""
<canvas id='sc' width='1280' height='720' class='full'></canvas>
<canvas id='pc' width='1280' height='720' class='full'></canvas>
<div id='box' class='abs' style='left:190px;top:320px;width:900px;height:74px;border-radius:14px;background:#f4f4f2;box-shadow:0 20px 60px rgba(0,0,0,.5);display:flex;align-items:center;padding:0 26px;box-sizing:border-box'>
  <span id='pt' class='mono' style='font-size:22px;color:#1a1c20;white-space:pre'></span><span id='caret' style='display:inline-block;width:2px;height:28px;background:#1a1c20;margin-left:2px'></span>
</div>
<div id='lab' class='abs mono' style='left:190px;top:286px;font-size:13px;letter-spacing:.3em;color:#8c8f98'>PROMPT</div>
<div class='vig'></div>
""", """
const TXT = __P__; let PTS = null;
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  // "Type a prompt." — typing runs until the second sentence ends
  const n = Math.floor(clamp01((t - C[0] - 0.1) / (C[2] - C[0] - 0.4)) * TXT.length);
  el('pt').textContent = TXT.slice(0, n);
  el('caret').style.opacity = n < TXT.length || Math.floor(t * 3) % 2 ? 1 : 0.1;
  // "Now, bring your world to life." — the letters come apart and fall into a dawn sea
  const go = C[2], dis = seg(t, go, go + 0.35), fly = seg(t, go, go + 2.2);
  el('box').style.opacity = 1 - dis; el('lab').style.opacity = 1 - dis;
  el('box').style.transform = `scale(${lerp(1, 1.04, dis)})`;
  if (!PTS) PTS = textTargets(TXT, "22px 'JetBrains Mono'", 900, 74, 2, 190 - 450 + 450 + (26 - (900 - 26) / 2) + 440, 320);
  const sc = el('sc').getContext('2d');
  const sceneK = easeOut(seg(t, go + 0.3, go + 2.4));
  sc.fillStyle = '#05070b'; sc.fillRect(0, 0, 1280, 720);
  if (sceneK > 0) {
    sc.globalAlpha = sceneK;
    const sky = sc.createLinearGradient(0, 0, 0, 430); sky.addColorStop(0, '#1b1a3c'); sky.addColorStop(0.7, '#e98a6a'); sky.addColorStop(1, '#ffd2a0');
    sc.fillStyle = sky; sc.fillRect(0, 0, 1280, 430);
    const sy = lerp(470, 395, easeOut(seg(t, go + 0.5, D)));
    const sun = sc.createRadialGradient(640, sy, 0, 640, sy, 140); sun.addColorStop(0, '#fff6e0'); sun.addColorStop(0.35, 'rgba(255,214,150,.9)'); sun.addColorStop(1, 'rgba(255,170,110,0)');
    sc.fillStyle = sun; sc.fillRect(0, 0, 1280, 430);
    const sea = sc.createLinearGradient(0, 430, 0, 720); sea.addColorStop(0, '#5a4a6e'); sea.addColorStop(1, '#0c1426');
    sc.fillStyle = sea; sc.fillRect(0, 430, 1280, 290);
    for (let r = 0; r < 18; r++) {
      const y0 = 436 + r * r * 0.9 + r * 3; sc.strokeStyle = `rgba(255,${200 - r * 4},${160 - r * 3},${0.5 - r * 0.02})`; sc.lineWidth = 1 + r * 0.12; sc.beginPath();
      for (let x = 0; x <= 1280; x += 8) { const y = y0 + Math.sin(x * (0.02 - r * 0.0006) + t * (1.6 - r * 0.03) + r) * (1 + r * 0.35); x ? sc.lineTo(x, y) : sc.moveTo(x, y); }
      sc.stroke();
    }
    sc.globalAlpha = 1;
  }
  const pc = el('pc').getContext('2d'); pc.clearRect(0, 0, 1280, 720);
  if (dis > 0) {
    pc.globalCompositeOperation = 'lighter';
    PTS.forEach(([x, y], i) => {
      if (i % 2) return;
      const k = easeOut(clamp01((fly - rnd(i) * 0.3) / 0.7));
      const tx = 640 + (rnd(i * 3) - 0.5) * 900 * (0.3 + rnd(i * 5)), ty = 440 + rnd(i * 7) * 240;
      const px = lerp(x, tx, k) + Math.sin(t * 2 + i) * 3 * k, py = lerp(y, ty, k) - Math.sin(k * Math.PI) * 80;
      const a = (1 - 0.6 * k) * (0.6 + 0.4 * Math.sin(t * 8 + i * 1.7));
      pc.fillStyle = `rgba(255,${230 - 40 * k},${200 - 60 * k},${a})`; pc.fillRect(px, py, 2, 2);
    });
    pc.globalCompositeOperation = 'source-over';
  }
  beatFade(t, D, 0.2, 0.25);
}
""".replace("__P__", json.dumps(PROMPT)))

# ------------------------------------------------------------------ together: two ribbons braid into one line
beats["together"] = B("together", """
<canvas id='cv' width='1280' height='720' class='full'></canvas>
<div id='w' class='abs serif' style='left:0;top:600px;width:1280px;text-align:center;font-size:40px;font-style:italic;color:#f4efe2;opacity:0'>you and AI, together</div>
<div class='vig'></div>
""", """
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  const g = el('cv').getContext('2d');
  g.fillStyle = 'rgba(4,6,10,1)'; g.fillRect(0, 0, 1280, 720);
  g.globalCompositeOperation = 'lighter';
  const grow = easeOut(seg(t, 0.1, C[1] + 0.8)), merge = ease(seg(t, C[1], C[1] + 1.2));
  const top = lerp(720, 90, grow);
  [[246, 224, 160, 0], [127, 216, 255, Math.PI]].forEach(([r, gg, b, ph]) => {
    for (let pass = 0; pass < 3; pass++) {
      g.strokeStyle = `rgba(${r},${gg},${b},${[0.08, 0.2, 0.9][pass]})`; g.lineWidth = [22, 9, 2.5][pass]; g.beginPath();
      for (let y = 720; y >= top; y -= 4) {
        const k = (720 - y) / 630, amp = 150 * (1 - merge) * (0.4 + 0.6 * Math.sin(k * Math.PI));
        const x = 640 + Math.sin(k * 9 + t * 2.2 + ph) * amp;
        y === 720 ? g.moveTo(x, y) : g.lineTo(x, y);
      }
      g.stroke();
    }
  });
  const star = seg(t, C[1] + 0.9, C[1] + 1.3);
  if (star > 0) { const gr = g.createRadialGradient(640, top, 0, 640, top, 120); gr.addColorStop(0, `rgba(255,255,255,${star})`); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 1280, 720); }
  g.globalCompositeOperation = 'source-over';
  el('w').style.opacity = seg(t, C[1] - 0.2, C[1] + 0.3);
  beatFade(t, D, 0.2, 0.3);
}
""")

# ------------------------------------------------------------------ close: the title on a hologram, and a step toward it
beats["close"] = B("close", f"""
<canvas id='gl' width='1280' height='720' class='full'></canvas>
""", """
const TW = 1500, TH = 1100, PW = 7.5, PH = 5.5, CH = 0.45; let S = null;
const setup = () => {
  const s = makeRenderer('gl', [0.8, 0.3, 0.95]);
  s.scene.background = new THREE.Color(0x030b12); s.scene.fog = new THREE.FogExp2(0x030b12, 0.045);
  s.scene.add(new THREE.AmbientLight(0x3a6a88, 0.5));
  const key = new THREE.PointLight(0x5fd0ff, 2.4, 12, 1.6); key.position.set(0, -2.9, 1.8); s.scene.add(key);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: 0x06121b, metalness: 0.75, roughness: 0.32 }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = -3.8; s.scene.add(floor);
  const grid = new THREE.GridHelper(60, 60, 0x1f5f80, 0x0f3246); grid.position.y = -3.79; grid.material.transparent = true; grid.material.opacity = 0.45; s.scene.add(grid);
  const ped = new THREE.Group(); ped.position.set(0, -3.62, 0.2); s.scene.add(ped);
  const metal = new THREE.MeshStandardMaterial({ color: 0x0c1c28, metalness: 0.9, roughness: 0.28 });
  const d1 = new THREE.Mesh(new THREE.CylinderGeometry(2.25, 2.45, 0.28, 96), metal); ped.add(d1);
  const d2 = new THREE.Mesh(new THREE.CylinderGeometry(1.75, 1.95, 0.22, 96), metal); d2.position.y = 0.25; ped.add(d2);
  const glow = new THREE.MeshBasicMaterial({ color: 0x9fe8ff });
  [[2.3, 0.15, 0.03], [1.85, 0.37, 0.035], [1.35, 0.38, 0.02]].forEach(([r, y, tk]) => { const ring = new THREE.Mesh(new THREE.TorusGeometry(r, tk, 12, 160), glow); ring.rotation.x = Math.PI / 2; ring.position.y = y; ped.add(ring); });
  s.dash = new THREE.Group(); s.dash.position.y = 0.4; ped.add(s.dash);
  for (let k = 0; k < 18; k++) { const arc = new THREE.Mesh(new THREE.TorusGeometry(1.6, 0.025, 8, 24, Math.PI * 2 / 18 * 0.55), glow); arc.rotation.x = Math.PI / 2; arc.rotation.z = k * Math.PI * 2 / 18; s.dash.add(arc); }
  const scr = new THREE.Group(); s.scene.add(scr);
  s.tc = document.createElement('canvas'); s.tc.width = TW; s.tc.height = TH;
  s.tex = new THREE.CanvasTexture(s.tc); s.tex.anisotropy = 8;
  scr.add(new THREE.Mesh(fitUV(new THREE.ShapeGeometry(chamfer(PW, PH, CH)), PW, PH), new THREE.MeshBasicMaterial({ map: s.tex, transparent: true, depthWrite: false, fog: false })));
  const f1 = new THREE.Mesh(ringOf(PW + 0.16, PH + 0.16, CH + 0.05, 0.075), new THREE.MeshBasicMaterial({ color: 0xe2f8ff, fog: false })); f1.position.z = 0.01; scr.add(f1);
  const back = new THREE.Mesh(new THREE.ShapeGeometry(chamfer(PW + 0.3, PH + 0.3, CH + 0.1)), new THREE.MeshBasicMaterial({ color: 0x02070c, fog: false })); back.position.z = -0.12; scr.add(back);
  const N = 420, pos = new Float32Array(N * 3); s.seed = []; for (let i = 0; i < N; i++) s.seed.push([rnd(i * 1.7), rnd(i * 2.3), rnd(i * 3.1), rnd(i * 4.9)]);
  s.pg = new THREE.BufferGeometry(); s.pg.setAttribute('position', new THREE.BufferAttribute(pos, 3)); s.pos = pos;
  s.scene.add(new THREE.Points(s.pg, new THREE.PointsMaterial({ size: 0.07, map: dotTex('170,230,255'), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })));
  return s;
};
const face = (g, t) => {
  g.clearRect(0, 0, TW, TH);
  const bg = g.createLinearGradient(0, 0, 0, TH); bg.addColorStop(0, 'rgba(12,46,70,.94)'); bg.addColorStop(1, 'rgba(5,22,36,.97)'); g.fillStyle = bg; g.fillRect(0, 0, TW, TH);
  g.fillStyle = 'rgba(160,230,255,.05)'; for (let y = (t * 60) % 6; y < TH; y += 6) g.fillRect(0, y, TW, 2);
  for (let k = 0; k < 5; k++) { miniFilm(g, k, 120 + k * 256, 80, 236, 136, t + k); g.strokeStyle = 'rgba(150,225,255,.75)'; g.lineWidth = 2; g.strokeRect(120 + k * 256, 80, 236, 136); }
  const k = easeOut(seg(t, C[0] - 0.1, C[0] + 0.7));
  g.globalAlpha = k; g.textAlign = 'center';
  g.shadowColor = 'rgba(110,210,255,.8)'; g.shadowBlur = 22; g.fillStyle = '#e4f2f9';
  g.font = "900 128px 'Inter Tight'"; g.fillText('AI SHORT FILM', TW / 2, 470); g.fillText('FES 2025', TW / 2, 610);
  g.shadowBlur = 0; g.fillText('AI SHORT FILM', TW / 2, 470); g.fillText('FES 2025', TW / 2, 610);
  g.globalAlpha = seg(t, C[1] - 0.1, C[1] + 0.4); g.font = "600 34px 'JetBrains Mono'"; g.fillStyle = '#9fdcf5'; g.fillText('POWERED BY MULMOCAST', TW / 2, 720);
  g.globalAlpha = 1;
  g.font = "600 22px 'JetBrains Mono'"; g.fillStyle = 'rgba(150,225,255,.7)'; g.textAlign = 'left'; g.fillText('2025 REMAKE', 120, 1010);
};
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  if (!S) S = setup();
  // "Take your first step onto the screen." — the camera walks toward it
  const step = ease(seg(t, C[2] - 0.2, D));
  S.cam.position.set(lerp(0.6, 0.55, step), lerp(-0.3, -0.55, step), lerp(12.4, 9.0, step)); S.cam.lookAt(0.55, -0.65, 0);
  S.dash.rotation.y = t * 0.6;
  for (let i = 0; i < S.seed.length; i++) {
    const [a, b, c, d] = S.seed[i], h = (b + t * (0.25 + 0.35 * c)) % 1, r = (0.3 + 1.2 * a) * (1 - h * 0.25), ang = d * 6.283 + t * 0.5;
    S.pos[i * 3] = Math.cos(ang) * r; S.pos[i * 3 + 1] = -3.1 + h * 3.2; S.pos[i * 3 + 2] = 0.2 + Math.sin(ang) * r * 0.6;
  }
  S.pg.attributes.position.needsUpdate = true;
  face(S.tc.getContext('2d'), t); S.tex.needsUpdate = true;
  S.composer.render();
  beatFade(t, D, 0.25, 0.3);
}
""", three=True)

deck = {
    "$mulmocast": {"version": "1.1"},
    "title": "AI Short Film Fes 2025 — trailer remake",
    "description": "A remake of the AI Short Film Fes 2025 trailer, a year later: every frame drawn in code by Claude Opus 5.5. Dates and prize amounts are masked; not an announcement.",
    "lang": "en",
    "canvasSize": {"width": 1280, "height": 720},
    "speechParams": {"speakers": SPEAKERS},
    "audioParams": {"padding": 0, "introPadding": 0, "closingPadding": 0, "outroPadding": 0,
                    "bgmVolume": 0.1, "audioVolume": 1.0, "bgm": {"kind": "path", "path": "bgm/bgm.mp3"}},
    "beats": [beats[b] for b in ORDER],
}
# ONLY=open,title,... writes just those narration beats (plain placeholders) — for generating the narration
# in small batches under the Gemini TTS per-minute limit (a failed run keeps nothing, so a big batch wastes quota)
if os.environ.get("ONLY"):
    keep = os.environ["ONLY"].split(",")
    deck["beats"] = [{"id": b, "speaker": TEXT[b][0], "text": TEXT[b][1], "image": {"type": "html_tailwind", "html": "<div></div>"}} for b in ORDER if b in keep]
    deck["audioParams"].pop("bgm")

with open(os.path.join(HERE, "filmfes2025_remake.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("ok", TOTAL_FRAMES, "frames", round(TOTAL_FRAMES / FPS, 2), "s")
