#!/usr/bin/env python3
"""Build blvckout_30s.json (fan-made 30s promo for BLVCKOUT). Run from anywhere."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.environ.get("VOICE", "Algenib")
LOGO = open(os.path.join(HERE, "images/logo.svg")).read().replace('role="img"', 'role="img" width="100%" height="100%"')

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Noto+Sans+JP:wght@500;700;900&display=block" rel="stylesheet">'
CSS = """<style>
.stage{position:relative;width:1280px;height:720px;overflow:hidden;background:#070707;color:#f5f5f3;font-family:'Noto Sans JP',sans-serif;}
.abs{position:absolute;}
.lat{font-family:'Barlow Condensed',sans-serif;letter-spacing:.08em;}
.muted{color:#a6a6a2;}
.photo{position:absolute;inset:0;width:1280px;height:720px;object-fit:cover;filter:grayscale(1) contrast(1.15);}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(7,7,7,0) 40%,rgba(7,7,7,.85) 100%);}
.glow{filter:drop-shadow(0 0 6px rgba(255,255,255,.7));}
.wave{position:absolute;left:-80px;bottom:0;width:1440px;height:300px;object-fit:cover;object-position:bottom;-webkit-mask-image:linear-gradient(#0000,#000 45%);mask-image:linear-gradient(#0000,#000 45%);opacity:.85;}
</style>"""

COMMON_JS = r"""
const el = (id) => document.getElementById(id);
const clamp01 = (t) => Math.max(0, Math.min(1, t));
const seg = (t, a, b) => clamp01((t - a) / (b - a));
const ease = (t) => { t = clamp01(t); return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; };
const easeOut = (t) => 1 - Math.pow(1 - clamp01(t), 3);
const lerp = (a, b, k) => a + (b - a) * k;
let fontsReady = false;
const waitFonts = async () => { if (!fontsReady) { await document.fonts.ready; fontsReady = true; } };
const G = (p, m, s) => Math.exp(-((p - m) * (p - m)) / (2 * s * s));
const pqrst = (p) => 0.12 * G(p, 0.12, 0.02) - 0.15 * G(p, 0.285, 0.008) + 1.0 * G(p, 0.31, 0.01) - 0.3 * G(p, 0.335, 0.008) + 0.22 * G(p, 0.55, 0.04);
// scrolling ECG: newest sample at the right edge. amp in px, bpm may vary.
const ecgPath = (t, bpm, w, h, amp, speed) => {
  let d = '';
  for (let x = 0; x <= w; x += 3) {
    const tau = t - (w - x) / speed;
    const ph = tau * bpm / 60;
    const p = ph - Math.floor(ph);
    const y = h / 2 - (tau < 0 ? 0 : pqrst(p) * amp);
    d += (x === 0 ? 'M' : 'L') + x + ' ' + y.toFixed(1);
  }
  return d;
};
const setOp = (id, v) => { el(id).style.opacity = v; };
const fadeInOut = (t, a, b, f = 0.25) => Math.min(seg(t, a, a + f), 1 - seg(t, b - f, b));
"""


def beat(bid, text, duration, html, script):
    b = {"id": bid, "duration": duration, "image": {"type": "html_tailwind", "animation": True, "html": FONTS + "\n" + CSS + html, "script": COMMON_JS + script}}
    if text:
        b["speaker"] = "Narrator"
        b["text"] = text
    else:
        b["text"] = ""
    return b


def ecg_svg(sid, top, h=160, opacity=1):
    return f'<svg class="abs glow" style="left:0;top:{top}px;opacity:{opacity}" width="1280" height="{h}"><path id="{sid}" fill="none" stroke="#f5f5f3" stroke-width="2.5" stroke-linejoin="round"/></svg>'


# ---------- 1. ignite (0-3s) ----------
b1 = beat("ignite", "", 3.0, f"""<div class="stage">
{ecg_svg('ecg', 280, 160)}
<div id="bpm" class="abs lat" style="left:64px;top:560px;font-size:28px;font-weight:600;opacity:0"><span class="muted" style="font-size:18px">HEART RATE</span><br><span id="bpmv" style="font-size:64px">62</span> <span class="muted" style="font-size:22px">BPM</span></div>
<div id="c1" class="abs" style="left:0;width:1280px;top:130px;text-align:center;font-size:44px;font-weight:900;letter-spacing:.12em;opacity:0">極限まで上げて、</div>
<div id="c2" class="abs" style="left:0;width:1280px;top:480px;text-align:center;font-size:44px;font-weight:900;letter-spacing:.12em;opacity:0">一気に落とす。</div>
</div>""", r"""
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  el('ecg').setAttribute('d', ecgPath(t, 62, 1280, 160, 70, 420));
  setOp('bpm', seg(t, 0.3, 0.8));
  setOp('c1', seg(t, 0.9, 1.3));
  setOp('c2', seg(t, 1.7, 2.1));
  el('c2').style.transform = 'translateY(' + (1 - easeOut(seg(t, 1.7, 2.1))) * -20 + 'px)';
}
""")

# ---------- 2. move (3-11s) ----------
SHOTS = [("burpee", 0.0), ("climber", 1.4), ("crowd", 2.8), ("burpee", 4.2), ("climber", 5.2), ("crowd", 6.2)]
WORDS = [("HIIT", 0.15, 1.3, 180), ("BURPEE", 1.5, 2.7, 150), ("25s × 8 SETS", 2.9, 4.1, 120), ("50 PEOPLE", 4.3, 5.1, 150), ("ALL IN.", 5.3, 6.1, 170), ("PUSH YOUR LIMITS.", 6.3, 8.0, 120)]
imgs = "\n".join(f'<img id="s{i}" class="photo" src="image:{n}" style="opacity:0">' for i, (n, _) in enumerate(SHOTS))
words = "\n".join(f'<div id="w{i}" class="abs lat" style="left:0;width:1280px;top:{360 - sz // 2 - 20}px;text-align:center;font-size:{sz}px;font-weight:700;line-height:1;opacity:0;text-shadow:0 0 30px rgba(0,0,0,.8)">{w}</div>' for i, (w, a, b, sz) in enumerate(WORDS))
b2 = beat("move", "限界まで、上げろ。", 8.0, f"""<div class="stage">
{imgs}
<div class="vig"></div>
{words}
<div class="abs" style="left:0;top:600px;width:1280px;height:120px;background:linear-gradient(transparent,rgba(7,7,7,.9))"></div>
{ecg_svg('ecg', 590, 120)}
<div class="abs lat" style="left:64px;top:470px;font-weight:600"><span class="muted" style="font-size:18px">HEART RATE</span><br><span id="bpmv" style="font-size:72px">62</span> <span class="muted" style="font-size:22px">BPM</span></div>
<div id="tag" class="abs lat muted" style="right:64px;top:48px;font-size:24px;font-weight:600">01 — MOVE</div>
<div id="flash" class="abs" style="inset:0;background:#fff;opacity:0"></div>
</div>""", "const SHOTS = " + json.dumps(SHOTS) + ";\nconst WORDS = " + json.dumps(WORDS) + ";" + r"""
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  const bpm = Math.round(lerp(62, 188, easeOut(seg(t, 0.0, 7.2))));
  el('bpmv').textContent = bpm;
  el('ecg').setAttribute('d', ecgPath(t + 3, bpm, 1280, 120, 55, 520));
  let flash = 0;
  SHOTS.forEach(([n, s], i) => {
    const e = (i + 1 < SHOTS.length ? SHOTS[i + 1][1] : 8.1);
    const on = t >= s && t < e;
    const k = seg(t, s, e);
    const img = el('s' + i);
    img.style.opacity = on ? 1 : 0;
    const shake = t > 6.2 ? Math.sin(t * 90) * 6 : 0;
    img.style.transform = 'scale(' + (1.05 + 0.12 * k) + ') translate(' + ((i % 2 ? -1 : 1) * 20 * k + shake) + 'px,' + shake * 0.6 + 'px)';
    if (i > 0 && t >= s) flash = Math.max(flash, 1 - seg(t, s, s + 0.12));
  });
  el('flash').style.opacity = flash * 0.55;
  WORDS.forEach(([w, a, b], i) => {
    const e = el('w' + i);
    e.style.opacity = fadeInOut(t, a, b, 0.08);
    e.style.transform = 'scale(' + (1.25 - 0.25 * easeOut(seg(t, a, a + 0.25))) + ')';
  });
}
""")

# ---------- 3. blackout (11-13s) ----------
b3 = beat("blackout", "", 2.0, """<div class="stage" style="background:#000">
<svg class="abs" style="left:0;top:350px" width="1280" height="20"><line id="flat" x1="0" y1="10" x2="0" y2="10" stroke="#f5f5f3" stroke-width="2" opacity=".8"/></svg>
</div>""", r"""
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  el('flat').setAttribute('x2', 1280 * easeOut(seg(t, 1.0, 1.9)));
}
""")

# ---------- 4. breathe (13-20s) ----------
b4 = beat("breathe", "そして、止まれ。", 7.0, """<div class="stage">
<img id="med" class="photo" src="image:meditate" style="opacity:0">
<div class="vig"></div>
<img id="wv" class="wave" src="image:wave">
<div id="tag" class="abs lat muted" style="right:64px;top:48px;font-size:24px;font-weight:600;opacity:0">02 — BREATHE</div>
<div id="c1" class="abs" style="left:0;width:1280px;top:300px;text-align:center;font-size:52px;font-weight:900;letter-spacing:.2em;opacity:0">深い静寂へ。</div>
<div class="abs lat" style="left:64px;top:470px;font-weight:600"><span class="muted" style="font-size:18px">HEART RATE</span><br><span id="bpmv" style="font-size:72px">188</span> <span class="muted" style="font-size:22px">BPM</span></div>
""" + ecg_svg('ecg', 590, 120, 0.8) + """
</div>""", r"""
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  const bpm = Math.round(lerp(188, 54, easeOut(seg(t, 0.2, 6.5))));
  el('bpmv').textContent = bpm;
  el('ecg').setAttribute('d', ecgPath(t, bpm, 1280, 120, lerp(55, 35, seg(t, 0, 6)), 300));
  const m = el('med');
  m.style.opacity = ease(seg(t, 0.3, 2.2));
  m.style.transform = 'scale(' + (1.15 - 0.1 * seg(t, 0, 7)) + ')';
  el('wv').style.transform = 'translateX(' + (-40 + 60 * seg(t, 0, 7)) + 'px)';
  el('wv').style.opacity = 0.85 * seg(t, 0.5, 2.5);
  setOp('tag', seg(t, 0.6, 1.2));
  setOp('c1', fadeInOut(t, 3.2, 6.8, 0.6));
}
""")

# ---------- 5. protocol / metrics (20-25s) ----------
b5 = beat("protocol", "心拍を、支配しろ。", 5.0, """<div class="stage">
<div class="abs lat muted" style="left:90px;top:56px;font-size:24px;font-weight:600">BLVCKOUT PROTOCOL</div>
<div id="h" class="abs" style="left:90px;top:88px;font-size:40px;font-weight:900;letter-spacing:.08em;opacity:0">心拍の落差で、ととのいを測る。</div>
<svg class="abs" style="left:90px;top:170px" width="1100" height="440" viewBox="0 0 1100 440">
 <line x1="0" y1="400" x2="1100" y2="400" stroke="#ffffff29" stroke-width="1"/>
 <path id="curve" fill="none" stroke="#f5f5f3" stroke-width="3" stroke-linejoin="round" class="glow"/>
 <g id="sw" opacity="0"><line id="swl" stroke="#f5f5f3" stroke-width="1.5" stroke-dasharray="4 5"/></g>
 <g id="dots"></g>
</svg>
<div id="labels"></div>
<div id="phases" class="abs lat muted" style="left:90px;top:584px;width:1100px;height:30px;font-size:18px;font-weight:600"></div>
</div>""", r"""
const W = 1100, H = 400;
const yOf = (b) => H - (b - 40) / 160 * (H - 20);
const segs = [[0, .05, 70, 70], [.05, .25, 70, 176], [.25, .45, 176, 62], [.45, .62, 62, 188], [.62, .88, 188, 52], [.88, 1, 52, 68]];
const bpmAt = (x) => { for (const [a, b, s, e] of segs) if (x <= b) { const k = (x - a) / (b - a); const up = e > s; const f = up ? 1 - Math.pow(1 - k, 2) : 1 - Math.pow(1 - k, 3); return s + (e - s) * f; } return 68; };
const pts = []; for (let i = 0; i <= 400; i++) { const x = i / 400; pts.push([x * W, yOf(bpmAt(x) + Math.sin(i * 1.7) * 1.5)]); }
const LBL = [['IGNITE', '瞬発の神', .12, 2.0], ['PEAK', '限界王', .62, 2.4], ['RECOVER', '回復の鬼', .69, 2.8], ['STILL', '瞑想の達人', .88, 3.2], ['SWING', 'ととのいマスター', .95, 3.6]];
const PH = [['01 MOVE', .05, .25], ['02 BREATHE', .25, .45], ['01 MOVE', .45, .62], ['02 BREATHE', .62, .88], ['03 CONNECT', .88, 1]];
let built = false;
const build = () => {
  if (built) return; built = true;
  const L = el('labels');
  LBL.forEach(([en, ja, x], i) => {
    const px = x * W, py = yOf(bpmAt(x));
    const d = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    d.setAttribute('cx', px); d.setAttribute('cy', en === 'SWING' ? (yOf(188) + yOf(52)) / 2 : py); d.setAttribute('r', 7); d.setAttribute('fill', '#070707'); d.setAttribute('stroke', '#f5f5f3'); d.setAttribute('stroke-width', 3); d.id = 'd' + i; d.style.opacity = 0;
    el('dots').appendChild(d);
    const above = en === 'PEAK' || en === 'IGNITE';
    const div = document.createElement('div');
    div.className = 'abs'; div.id = 'l' + i;
    const still = en === 'STILL';
    const top = en === 'SWING' ? 170 + (yOf(188) + yOf(52)) / 2 - 30 : still ? 170 + py - 30 : 170 + py + (above ? -78 : 18);
    const left = en === 'SWING' ? 90 + px - 190 : still ? 90 + px - 180 : 90 + px - 80;
    div.style.cssText = 'left:' + left + 'px;top:' + top + 'px;width:160px;text-align:' + (en === 'SWING' || en === 'STILL' ? 'right' : 'center') + ';opacity:0;white-space:nowrap';
    div.innerHTML = '<div class="lat" style="font-size:30px;font-weight:700;line-height:1">' + en + '</div><div class="muted" style="font-size:15px;font-weight:700;margin-top:4px">' + ja + '</div>';
    L.appendChild(div);
  });
  const P = el('phases');
  PH.forEach(([n, a, b]) => { const s = document.createElement('div'); s.className = 'abs'; s.style.cssText = 'left:' + a * W + 'px;width:' + (b - a) * W + 'px;text-align:center;border-top:1px solid #ffffff29;padding-top:6px'; s.textContent = n; P.appendChild(s); });
  const sx = .95 * W; const l = el('swl'); l.setAttribute('x1', sx); l.setAttribute('x2', sx); l.setAttribute('y1', yOf(188)); l.setAttribute('y2', yOf(52));
};
async function render(frame, totalFrames, fps) {
  await waitFonts();
  build();
  const t = frame / fps;
  setOp('h', seg(t, 0.2, 0.7));
  const k = easeOut(seg(t, 0.3, 2.2));
  const n = Math.max(2, Math.round(k * pts.length));
  el('curve').setAttribute('d', pts.slice(0, n).map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(''));
  LBL.forEach(([, , , s], i) => { setOp('l' + i, seg(t, s, s + 0.25)); setOp('d' + i, seg(t, s, s + 0.15)); el('l' + i).style.transform = 'translateY(' + (1 - easeOut(seg(t, s, s + 0.3))) * 12 + 'px)'; });
  el('sw').setAttribute('opacity', seg(t, 3.5, 3.8));
}
""")

# ---------- 6. cta (25-30s) ----------
b6 = beat("cta", "ととのいは、自分でつくれ。", 5.0, f"""<div class="stage">
<img id="wv" class="wave" src="image:wave" style="height:340px">
<div id="logo" class="abs" style="left:290px;top:190px;width:700px;height:70px;opacity:0">{LOGO}</div>
<div id="cp" class="abs" style="left:0;width:1280px;top:292px;text-align:center;font-size:50px;font-weight:900;letter-spacing:.06em;opacity:0">ととのいは、自分でつくれ。</div>
<div id="en" class="abs lat muted" style="left:0;width:1280px;top:372px;text-align:center;font-size:22px;letter-spacing:.35em;opacity:0">MASTER YOUR TOTONOI.</div>
<div id="info" class="abs lat" style="left:0;width:1280px;top:450px;text-align:center;font-size:38px;font-weight:600;letter-spacing:.12em;opacity:0">2026.11.23 MON — TOKYO · YOGA</div>
<div id="line" class="abs" style="left:0;width:1280px;top:510px;text-align:center;font-size:20px;font-weight:700;opacity:0"><span style="border:1px solid #ffffff6b;padding:8px 26px">公式LINEから応募</span></div>
<div class="abs muted" style="right:28px;bottom:18px;font-size:13px;opacity:.7">fan-made video</div>
</div>""", r"""
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  const lg = el('logo');
  lg.style.opacity = ease(seg(t, 0.1, 0.9));
  lg.style.transform = 'scale(' + (1.12 - 0.12 * easeOut(seg(t, 0.1, 1.6))) + ')';
  lg.style.filter = 'blur(' + (1 - seg(t, 0.1, 0.9)) * 8 + 'px)';
  setOp('cp', seg(t, 0.7, 1.2));
  setOp('en', seg(t, 1.3, 1.8));
  setOp('info', seg(t, 2.0, 2.5));
  el('info').style.transform = 'translateY(' + (1 - easeOut(seg(t, 2.0, 2.5))) * 16 + 'px)';
  setOp('line', seg(t, 2.6, 3.1));
  el('wv').style.transform = 'translateX(' + (-40 + 50 * seg(t, 0, 5)) + 'px)';
}
""")

STYLE = "Black-and-white fine-art sports photography, deep black background (#070707), single hard rim light, heavy film grain, high contrast, cinematic, 16:9. Figures are backlit silhouettes with faces in shadow and not identifiable. No text, no logos, no letters, no watermark."
images = {
    "wave": {"type": "image", "source": {"kind": "path", "path": "images/hero-wave.jpg"}},
    "burpee": {"type": "imagePrompt", "prompt": STYLE + " A lone athlete at the top of an explosive burpee jump in a dark studio, arms stretched overhead, sweat droplets flying and catching the light, dust in the air."},
    "climber": {"type": "imagePrompt", "prompt": STYLE + " Low-angle close shot of a person doing fast mountain climbers on the floor of a dark studio, motion blur on the legs, intense effort, rim light along the back and arms."},
    "crowd": {"type": "imagePrompt", "prompt": STYLE + " About fifty people in a dark event hall doing jumping squats in perfect sync, seen from behind and slightly above, a strobe of white light cutting through haze, energetic and unified."},
    "meditate": {"type": "imagePrompt", "prompt": STYLE + " A single person sitting cross-legged in meditation in the center of a vast dark room, eyes closed, calm, soft pale light falling from above through thin mist, deep stillness, lots of empty black space."},
}

script = {
    "$mulmocast": {"version": "1.1"},
    "title": "BLVCKOUT 30s (fan-made)",
    "lang": "ja",
    "canvasSize": {"width": 1280, "height": 720},
    "audioParams": {"padding": 0, "introPadding": 0, "closingPadding": 0, "outroPadding": 0, "bgmVolume": 0.35, "ttsVolume": 1.4},
    "speechParams": {"speakers": {"Narrator": {"provider": "gemini", "model": "gemini-3.1-flash-tts-preview", "voiceId": VOICE,
        "speechOptions": {"instruction": "低く渋い声で、感情を抑え、一語一語を噛みしめるようにゆっくり話してください。映画の予告編のナレーターのように。"}}}},
    "imageParams": {"provider": "google", "model": "gemini-3-pro-image-preview", "images": images},
    "beats": [b1, b2, b3, b4, b5, b6],
}
bgm = os.path.join(HERE, "bgm/bgm_duck.mp3")
if os.path.exists(bgm):
    script["audioParams"]["bgm"] = {"kind": "path", "path": "bgm/bgm_duck.mp3"}
json.dump(script, open(os.path.join(HERE, "blvckout_30s.json"), "w"), ensure_ascii=False, indent=1)
print("wrote blvckout_30s.json", "with bgm" if "bgm" in script["audioParams"] else "without bgm")
