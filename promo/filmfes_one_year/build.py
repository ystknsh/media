#!/usr/bin/env python3
"""Build filmfes_one_year.json — "One Year Apart", a 30 s look at how the AI Short Film Fes trailer changed in a year.

2025: the festival trailer was described shot by shot and filmed by a video model.
2026: every frame of this film is drawn by code written by Claude Opus 5.5 (html_tailwind animation);
the 2025 footage is shown by seeking the original trailer in a <video>, not by re-encoding it.

Run from anywhere: python3 build.py
Beat durations are fitted to the Gemini narration measured on 2026-09-28 (see TIMING below). If a line
changes, regenerate the audio, measure its pauses again, and move the cue times in that beat.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
# resolved by mulmocast against this script's folder
FOOTAGE = "../../filmfes2025/output/script_en.mp4"

NARRATION = {
    "archive": "A year ago, we made this trailer by describing every shot to a video model.",
    "melt": "It looked like cinema. Until you read it.",
    "cut": "",
    "code": "This year, Claude Opus 5.5 wrote the code that draws every frame.",
    "compare": "Same words. Every letter, exactly where it belongs.",
    "close": "One year apart. The trailer we wish we'd made.",
}
# seconds; each is >= its narration (archive 6.82, melt 4.49, code 7.37, compare 5.33, close 5.33 incl. its trailing silence)
TIMING = {"archive": 6.9, "melt": 4.6, "cut": 0.9, "code": 7.4, "compare": 5.4, "close": 5.3}

TOTAL_FRAMES = sum(math.floor(d * FPS) for d in TIMING.values())
START_FRAME = {}
_acc = 0
for _k, _d in TIMING.items():
    START_FRAME[_k] = _acc
    _acc += math.floor(_d * FPS)

SPEAKER = {
    "provider": "gemini",
    "model": "gemini-3.1-flash-tts-preview",
    "voiceId": "Charon",
    "speechOptions": {
        "instruction": "A calm, warm documentary narrator. Unhurried, intimate, slightly wry. Leave a small breath between sentences.",
    },
}

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600;800;900&family=JetBrains+Mono:wght@400;600&family=Instrument+Serif:ital@0;1&display=block" rel="stylesheet">'
CSS = """<style>
html,body{background:#000;margin:0;}
.stage{position:relative;width:1280px;height:720px;overflow:hidden;background:#050608;color:#f4f1ea;font-family:'Inter Tight',sans-serif;}
.abs{position:absolute;}
.mono{font-family:'JetBrains Mono',monospace;}
.serif{font-family:'Instrument Serif',serif;}
.warm{color:#e9dcc4;}
.cool{color:#bfe8ff;}
.full{position:absolute;left:0;top:0;width:1280px;height:720px;}
</style>"""

# rules/mulmo-deck-animation-helpers.js, plus seekTo / rnd / grain for the footage beats
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
const setOp = (id, v) => { el(id).style.opacity = v; };
const flashAfter = (t, start, dur = 0.12) => (t >= start ? 1 - seg(t, start, start + dur) : 0);
let fontsReady = false;
const waitFonts = async () => { if (!fontsReady) { await document.fonts.ready; fontsReady = true; } };
// deterministic noise: same frame, same pixels
const rnd = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
// seek a <video> and resolve once that exact frame is decoded
const seekTo = (v, t) => new Promise((res) => {
  const go = () => {
    if (Math.abs(v.currentTime - t) < 0.0005) return res();
    v.addEventListener('seeked', function h() { v.removeEventListener('seeked', h); res(); });
    v.currentTime = t;
  };
  if (v.readyState >= 2) go(); else v.addEventListener('loadeddata', go, { once: true });
});
// film grain into a small canvas stretched over the frame
const grain = (id, frame, amount) => {
  const c = el(id), g = c.getContext('2d'), img = g.createImageData(c.width, c.height), d = img.data;
  for (let i = 0; i < c.width * c.height; i++) {
    const v = 128 + (rnd(frame * 7919 + i) - 0.5) * 255 * amount;
    d[i * 4] = d[i * 4 + 1] = d[i * 4 + 2] = v; d[i * 4 + 3] = 255;
  }
  g.putImageData(img, 0, 0);
};
// mulmocast re-seeks every <video> to the beat's own time after render() returns, so a <video> never
// shows the time we asked for; seek it ourselves and paint the decoded frame into a canvas instead.
const paint = async (vid, cid, t, sx = 0, sy = 0, sw = 1280, sh = 720) => {
  await seekTo(el(vid), t);
  const c = el(cid); c.getContext('2d').drawImage(el(vid), sx, sy, sw, sh, 0, 0, c.width, c.height);
};
const pad = (n, w) => String(n).padStart(w, '0');
const tc = (sec) => { const f = Math.floor(sec * 30 + 1e-6); const s = Math.floor(f / 30); return '00:' + pad(Math.floor(s / 60), 2) + ':' + pad(s % 60, 2) + ':' + pad(f % 30, 2); };
const TOTAL_FRAMES = __TOTAL__;
"""

WARM_FILTER = "sepia(.28) saturate(.85) contrast(1.06) brightness(.94)"
GRAIN = "<canvas id='grain' width='320' height='180' class='full' style='mix-blend-mode:overlay;opacity:.32'></canvas>"
VIGNETTE = "<div class='full' style='box-shadow:inset 0 0 180px 50px rgba(0,0,0,.85)'></div>"


def beat(bid, html, script):
    b = {
        "id": bid,
        "text": NARRATION[bid],
        "duration": TIMING[bid],
        "image": {
            "type": "html_tailwind",
            "animation": {"fps": FPS},
            "html": FONTS + CSS + "<div class='stage'>" + html + "</div>",
            "script": COMMON_JS.replace("__TOTAL__", str(TOTAL_FRAMES)) + f"const START = {START_FRAME[bid]};\n" + script,
        },
    }
    if NARRATION[bid]:
        b["speaker"] = "Narrator"
    return b


def letters(word, cls="", style=""):
    return "".join(f"<span class='{cls}' style='display:inline-block;{style}'>{c}</span>" for c in word)


# ---------------------------------------------------------------- 1. archive: the 2025 trailer, as it was made
# Each shot shows the prompt that produced it (translated from the 2025 script's moviePrompt / imagePrompt).
SHOTS = [
    # beat time in, source time, prompt
    (0.00, 1.4, "white type dissolves into particles, spreading like a galaxy"),
    (1.62, 8.2, "the festival logo appears with light leaks"),
    (3.10, 14.4, "a human hand and a robot arm reach toward each other"),
    (4.30, 34.2, "five award cards float like holograms"),
    (5.42, 95.9, "a holographic screen lights up with the festival logo"),
]
archive_html = f"""
<div id='scr' class='full' style='transform-origin:50% 50%'>
  <video id='v' src='{FOOTAGE}' muted playsinline preload='metadata' style='position:absolute;left:0;top:0;width:2px;height:2px;opacity:0'></video>
  <canvas id='cv' width='1280' height='720' class='full' style='filter:{WARM_FILTER}'></canvas>
  {GRAIN}{VIGNETTE}
  <div id='flash' class='full' style='background:#fff4e0;opacity:0'></div>
</div>
<div id='black' class='full' style='background:#000'></div>
<div class='abs mono warm' style='left:48px;top:42px;font-size:14px;letter-spacing:.2em'><span id='rec' style='color:#ff5a4e'>&#9679;</span>&nbsp; ARCHIVE — AI SHORT FILM FES 2025 TRAILER</div>
<div id='yr' class='abs serif warm' style='right:52px;top:14px;font-size:118px;font-style:italic;line-height:1;opacity:.92'>2025</div>
<div class='abs' style='left:0;bottom:0;width:1280px;height:170px;background:linear-gradient(#0000,rgba(0,0,0,.78))'></div>
<div class='abs mono' style='left:48px;bottom:74px;font-size:13px;letter-spacing:.2em;color:#9d917d'>PROMPT <span id='shotn'>01</span> / 05 → VIDEO MODEL</div>
<div class='abs mono warm' style='left:48px;bottom:36px;font-size:24px'><span style='color:#ffb86b'>&gt;</span> <span id='pr'></span><span id='caret' style='color:#ffb86b'>&#9612;</span></div>
<div id='tc' class='abs mono' style='right:52px;bottom:40px;font-size:13px;letter-spacing:.14em;color:#9d917d'></div>
"""
archive_js = """
const SHOTS = __SHOTS__;
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  let i = 0; for (let k = 0; k < SHOTS.length; k++) if (t >= SHOTS[k][0]) i = k;
  const [tin, src, prompt] = SHOTS[i];
  const vt = src + (t - tin);
  // a slow push on the whole screen, gate weave, and a flicker that film would have
  const push = lerp(1.06, 1.0, easeOut(seg(t, 0, 6.9)));
  const wx = (rnd(frame * 3.1) - 0.5) * 2.2, wy = (rnd(frame * 5.7) - 0.5) * 1.6;
  el('scr').style.transform = `translate(${wx}px,${wy}px) scale(${push})`;
  el('scr').style.filter = `brightness(${1 + (rnd(frame * 1.3) - 0.5) * 0.06})`;
  el('flash').style.opacity = (i > 0 ? flashAfter(t, tin, 0.1) * 0.55 : 0);
  el('black').style.opacity = 1 - seg(t, 0, 0.5);
  // the prompt types in at the start of each shot
  const n = Math.floor((t - tin - 0.08) * 46);
  el('pr').textContent = prompt.slice(0, Math.max(0, n));
  el('caret').style.opacity = Math.floor(t * 3) % 2 ? 0.2 : 1;
  el('shotn').textContent = pad(i + 1, 2);
  el('rec').style.opacity = Math.floor(t * 2) % 2 ? 0.25 : 1;
  el('tc').textContent = 'SRC ' + tc(vt);
  grain('grain', frame, 0.55);
  return paint('v', 'cv', vt);
}
""".replace("__SHOTS__", json.dumps(SHOTS))

# ---------------------------------------------------------------- 2. melt: freeze, push into the misspelling
# 2025 frame geometry (1280x720): the INOATIVITY line spans x 345-785, centre y 258.
FREEZE = 97.85
melt_html = f"""
<div id='scr' class='full' style='transform-origin:565px 258px'>
  <video id='v' src='{FOOTAGE}' muted playsinline preload='metadata' style='position:absolute;left:0;top:0;width:2px;height:2px;opacity:0'></video>
  <canvas id='cv' width='1280' height='720' class='full' style='filter:{WARM_FILTER}'></canvas>
  <svg class='full' viewBox='0 0 1280 720'>
    <path id='ring' d='M 330 262 C 330 206, 520 208, 570 210 C 700 212, 812 214, 806 258 C 800 306, 640 310, 560 308 C 450 306, 332 304, 338 250' fill='none' stroke='#ff4d3d' stroke-width='3.2' stroke-linecap='round' vector-effect='non-scaling-stroke'/>
  </svg>
  {GRAIN}{VIGNETTE}
</div>
<div id='crtT' class='abs' style='left:0;top:0;width:1280px;height:0;background:#000'></div>
<div id='crtB' class='abs' style='left:0;bottom:0;width:1280px;height:0;background:#000'></div>
<div id='line' class='abs' style='left:0;top:359px;width:1280px;height:2px;background:#fff;opacity:0;box-shadow:0 0 16px #fff'></div>
<div id='hud' class='abs mono warm' style='left:48px;top:42px;font-size:14px;letter-spacing:.2em'><span style='color:#ff5a4e'>&#9679;</span>&nbsp; ARCHIVE — AI SHORT FILM FES 2025 TRAILER</div>
<div id='pause' class='abs mono warm' style='right:52px;top:42px;font-size:14px;letter-spacing:.2em;opacity:0'>&#10074;&#10074;&nbsp; {'00:01:37:25'}</div>
<div id='note' class='abs mono' style='left:0;width:1280px;top:548px;text-align:center;opacity:0'><span style='display:inline-block;padding:10px 22px;border-radius:8px;background:rgba(10,6,4,.86);font-size:30px;color:#ff6a5a'>“INOATIVITY” <span style='color:#f4f1ea'>— not a word.</span></span></div>
<div id='card' class='abs' style='left:60px;top:470px;width:300px;height:169px;border:6px solid #f1ece2;box-shadow:0 18px 40px rgba(0,0,0,.6);transform-origin:50% 50%;opacity:0;overflow:hidden;background:#000'>
  <video id='v2' src='{FOOTAGE}' muted playsinline preload='metadata' style='position:absolute;left:0;top:0;width:2px;height:2px;opacity:0'></video>
  <canvas id='cv2' width='300' height='169' style='position:absolute;left:0;top:0;filter:{WARM_FILTER}'></canvas>
  <div class='abs' style='left:18px;top:94px;width:118px;height:3px;background:#ff4d3d'></div>
</div>
<div id='cardl' class='abs mono' style='left:60px;top:652px;font-size:15px;color:#ff6a5a;opacity:0;padding:4px 10px;border-radius:5px;background:rgba(10,6,4,.86)'>also: “TECHNAL QUALITY”</div>
"""
melt_js = """
const FREEZE = __FREEZE__;
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  // play on into the frame, slowing to a stop as "It looked like cinema." ends
  const vt = lerp(FREEZE - 0.55, FREEZE, easeOut(seg(t, 0, 1.9)));
  const frozen = t >= 1.9;
  el('pause').style.opacity = frozen ? 1 : 0;
  // "Until you read it." — push into the misspelled line
  const z = lerp(1, 2.05, ease(seg(t, 2.35, 3.35)));
  const wx = frozen ? 0 : (rnd(frame * 3.1) - 0.5) * 2.2;
  el('scr').style.transform = `translate(${wx}px,0) scale(${z})`;
  el('cv').style.filter = `${'__WARM__'} saturate(${lerp(1, 0.55, seg(t, 1.9, 2.6))})`;
  const ring = el('ring'), L = 1500;
  ring.style.strokeDasharray = L; ring.style.strokeDashoffset = L * (1 - easeOut(seg(t, 3.0, 3.55)));
  el('note').style.opacity = seg(t, 3.25, 3.5);
  el('note').style.transform = `translateY(${lerp(10, 0, easeOut(seg(t, 3.25, 3.6)))}px)`;
  // a second slip from the same trailer, pinned like a photo
  const c = back(seg(t, 3.55, 3.95));
  el('card').style.opacity = seg(t, 3.55, 3.65);
  el('card').style.transform = `rotate(${lerp(-14, -4, c)}deg) scale(${lerp(0.6, 1, c)})`;
  el('cardl').style.opacity = seg(t, 3.8, 3.95);
  // CRT switch-off into the cut
  const off = seg(t, 4.28, 4.52);
  const sy = t < 4.28 ? 1 : Math.max(0.004, 1 - easeIn(off));
  // black bars close in from top and bottom (scaling the stage showed the page behind it)
  const bar = 360 * (1 - sy) - (t >= 4.46 ? 0 : 0);
  el('crtT').style.height = bar + 'px'; el('crtB').style.height = bar + 'px';
  el('scr').style.filter = `brightness(${1 + 1.5 * off})`;
  el('line').style.opacity = t >= 4.46 ? 1 - seg(t, 4.52, 4.6) : 0;
  grain('grain', frame, frozen ? 0.35 : 0.55);
  await paint('v', 'cv', vt);
  await paint('v2', 'cv2', 46.0);
}
""".replace("__FREEZE__", str(FREEZE)).replace("__WARM__", WARM_FILTER)

# ---------------------------------------------------------------- 3. cut: 2025 rolls over to 2026
cut_html = """
<div id='dot' class='abs' style='left:0;top:359px;width:1280px;height:2px;background:#fff;box-shadow:0 0 16px #fff'></div>
<div class='abs mono' style='left:0;top:300px;width:1280px;text-align:center;font-size:104px;font-weight:600;letter-spacing:.06em;line-height:120px;height:120px;overflow:hidden'>
  <span id='y1' style='display:inline-block;height:120px;line-height:120px;vertical-align:top;color:#e9dcc4'>202</span><span style='display:inline-block;height:120px;overflow:hidden;vertical-align:top'><span id='roll' style='display:block'><span style='display:block;height:120px;line-height:120px;color:#e9dcc4'>5</span><span style='display:block;height:120px;line-height:120px;color:#bfe8ff'>6</span></span></span>
</div>
"""
cut_js = """
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  // the CRT line collapses to a point, then the year appears and rolls over
  const k = easeIn(seg(t, 0, 0.2));
  el('dot').style.transform = `scaleX(${1 - k * 0.998})`;
  el('dot').style.opacity = 1 - seg(t, 0.18, 0.26);
  const yr = el('y1').parentElement;
  yr.style.opacity = seg(t, 0.2, 0.3);
  const r = ease(seg(t, 0.42, 0.66));
  el('roll').style.transform = `translateY(${-120 * r}px)`;
  el('y1').style.color = r > 0.5 ? '#bfe8ff' : '#e9dcc4';
  yr.style.transform = `scale(${lerp(1, 1.06, easeOut(seg(t, 0.42, 0.9)))})`;
}
"""

# ---------------------------------------------------------------- 4. code: the frames are written, not filmed
CODE = [
    ("<span class='k'>async function</span> <span class='f'>render</span>(frame, total, fps) {", None),
    ("  <span class='k'>const</span> t = frame / fps;", None),
    ("  <span class='f'>word</span>(<span class='s'>'CREATIVITY'</span>,  { y: <span class='n'>0</span> });", "w0"),
    ("  <span class='f'>word</span>(<span class='s'>'INNOVATION'</span>,  { y: <span class='n'>1</span> });", "w1"),
    ("  <span class='f'>word</span>(<span class='s'>'CO-CREATION'</span>, { y: <span class='n'>2</span> });", "w2"),
    ("  <span class='f'>glow</span>(t);", "glow"),
    ("}", None),
]
WORDS = ["CREATIVITY", "INNOVATION", "CO-CREATION"]
code_lines = "".join(
    f"<div class='cl' style='height:42px;white-space:pre'><span class='ln'>{i + 1:>2}</span>  <span class='ct' data-full=\"{line.replace(chr(34), '&quot;')}\"></span></div>"
    for i, (line, _) in enumerate(CODE)
)
preview_words = "".join(
    f"<div id='pw{i}' style='height:66px;line-height:66px;text-align:center;font-size:52px;font-weight:800;letter-spacing:.04em;color:#eaf7ff'>{letters(w, 'pl' + str(i))}</div>"
    for i, w in enumerate(WORDS)
)
THUMBS = 24
thumbs = "".join(
    f"<div class='th' style='flex:none;width:96px;height:54px;margin-right:10px;border-radius:4px;background:#0b1a24;border:1px solid #1d3a4a;position:relative;overflow:hidden'>"
    + "".join(f"<div class='tb' style='position:absolute;left:{18 + (2 - j) * 3 if j != 1 else 20}px;top:{12 + j * 11}px;height:5px;border-radius:2px;background:#bfe8ff;width:0'></div>" for j in range(3))
    + f"<div class='abs mono' style='right:4px;bottom:2px;font-size:8px;color:#5c8aa3' data-n='{k}'></div></div>"
    for k in range(THUMBS)
)
code_html = f"""
<style>
.k{{color:#ff7ab2}} .f{{color:#7cc7ff}} .s{{color:#ffd580}} .n{{color:#b9f18c}} .ln{{color:#3a4654}}
</style>
<div class='full' style='background:radial-gradient(ellipse at 70% 30%,#0d1c26 0%,#05080b 70%)'></div>
<div class='full' style='background-image:linear-gradient(rgba(120,190,230,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(120,190,230,.05) 1px,transparent 1px);background-size:40px 40px'></div>
<div id='ed' class='abs' style='left:48px;top:100px;width:620px;height:430px;border-radius:14px;background:#0b1016;border:1px solid #1e2a36;box-shadow:0 30px 60px rgba(0,0,0,.5);overflow:hidden'>
  <div style='height:44px;display:flex;align-items:center;padding:0 16px;border-bottom:1px solid #1e2a36;gap:8px'>
    <span style='width:11px;height:11px;border-radius:6px;background:#ff5f57'></span><span style='width:11px;height:11px;border-radius:6px;background:#febc2e'></span><span style='width:11px;height:11px;border-radius:6px;background:#28c840'></span>
    <span class='mono' style='margin-left:14px;font-size:14px;color:#8aa0b4'>trailer_2025_remake.js</span>
    <span id='chip' class='mono' style='margin-left:auto;font-size:13px;padding:4px 10px;border-radius:999px;background:#2a1b12;color:#ffb86b;border:1px solid #6b3f1f;opacity:0'>&#10022; written by Claude Opus 5.5</span>
  </div>
  <div class='mono' style='padding:24px 20px;font-size:20.5px;color:#d6e2ee'>{code_lines}</div>
</div>
<div id='vp' class='abs' style='left:696px;top:100px;width:536px;height:301.5px;border-radius:10px;background:#04121a;border:1px solid #1d3a4a;overflow:hidden;transform-origin:0 0'>
  <div id='glow' class='abs' style='left:0;top:0;width:536px;height:301.5px;background:radial-gradient(ellipse at 50% 55%,rgba(80,200,255,.35),transparent 65%);opacity:0'></div>
  <div class='abs' style='left:0;top:44px;width:536px;transform:scale(.72);transform-origin:50% 0'>{preview_words}</div>
</div>
<div class='abs mono' style='left:696px;top:72px;font-size:13px;letter-spacing:.2em;color:#5c8aa3'>PREVIEW · 1280×720</div>
<div id='fc' class='abs mono' style='left:696px;top:420px;font-size:22px;letter-spacing:.12em;color:#8fc9e8'></div>
<div id='stripw' class='abs' style='left:48px;top:572px;width:1168px;height:90px;overflow:hidden;opacity:0'>
  <div class='abs mono' style='left:0;top:0;font-size:12px;letter-spacing:.2em;color:#5c8aa3'>EVERY FRAME, RENDERED</div>
  <div id='strip' class='abs' style='left:0;top:26px;display:flex'>{thumbs}</div>
</div>
<div id='yr' class='abs mono cool' style='right:56px;top:14px;font-size:44px;font-weight:600;letter-spacing:.06em'>2026</div>
"""
code_js = """
const CUES = __CUES__;
let inited = false;
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  const lines = [...document.querySelectorAll('.ct')];
  // "This year," — the editor slides in; "Claude Opus 5.5" — its author chip
  const e = easeOut(seg(t, 0.15, 0.75));
  el('ed').style.transform = `translateY(${lerp(30, 0, e)}px)`; el('ed').style.opacity = e;
  el('vp').style.opacity = easeOut(seg(t, 0.4, 0.9));
  const ch = back(seg(t, 1.5, 1.85)); el('chip').style.opacity = seg(t, 1.5, 1.6); el('chip').style.transform = `scale(${ch})`;
  // "wrote the code" — typed line by line, fast
  const T0 = 1.0, CPS = 62;
  let budget = Math.max(0, (t - T0) * CPS);
  const done = [];
  lines.forEach((ln, i) => {
    const tmp = document.createElement('div'); tmp.innerHTML = ln.dataset.full;
    const plain = tmp.textContent;
    const take = Math.min(plain.length, Math.floor(budget)); budget -= plain.length;
    done.push(take >= plain.length);
    // cut the highlighted HTML at `take` visible characters
    let left = take; const walk = (node) => {
      for (const c of [...node.childNodes]) {
        if (left <= 0) { c.remove(); continue; }
        if (c.nodeType === 3) { if (c.textContent.length > left) c.textContent = c.textContent.slice(0, left); left -= c.textContent.length; }
        else walk(c);
      }
    };
    walk(tmp); ln.innerHTML = tmp.innerHTML;
  });
  // "that draws" — each word() line, once typed, draws its word letter by letter
  CUES.forEach(([lineIdx, wi], k) => {
    if (wi === null) return;
    const lettersEl = [...document.querySelectorAll('.pl' + wi)];
    const doneAt = T0 + [...document.querySelectorAll('.ct')].slice(0, lineIdx + 1).reduce((s, ln) => { const d = document.createElement('div'); d.innerHTML = ln.dataset.full; return s + d.textContent.length; }, 0) / CPS;
    lettersEl.forEach((sp, j) => {
      const p = seg(t, doneAt + j * 0.035, doneAt + j * 0.035 + 0.22);
      sp.style.opacity = p; sp.style.transform = `translateY(${lerp(18, 0, easeOut(p))}px)`;
      sp.style.filter = `blur(${lerp(6, 0, p)}px)`;
    });
  });
  const glowAt = 4.5;
  el('glow').style.opacity = 0.9 * easeOut(seg(t, glowAt, glowAt + 0.5));
  // "every frame" — the film's own frame counter and a strip of rendered frames
  const gf = START + frame;
  el('fc').textContent = 'FRAME ' + pad(gf, 4) + ' / ' + pad(TOTAL_FRAMES, 4);
  el('stripw').style.opacity = easeOut(seg(t, 5.1, 5.5));
  const run = Math.max(0, t - 5.1);
  el('strip').style.transform = `translateX(${-run * 260}px)`;
  document.querySelectorAll('.th').forEach((th, k) => {
    const p = clamp01((k + 1) / 10);
    th.querySelectorAll('.tb').forEach((b, j) => { b.style.width = (clamp01(p * 3 - j) * [60, 60, 66][j]) + 'px'; });
    th.lastElementChild.textContent = pad(START + Math.floor(fps * 5.1) + k * 12, 4);
  });
  // hand over: the preview grows toward full frame while the rest falls away
  const h = ease(seg(t, 6.95, 7.4));
  const sx = lerp(1, 1280 / 536, h);
  el('vp').style.transform = `translate(${lerp(0, -696, h)}px,${lerp(0, -100, h)}px) scale(${sx})`;
  el('ed').style.opacity = e * (1 - h);
  el('stripw').style.opacity = easeOut(seg(t, 5.1, 5.5)) * (1 - h);
  el('fc').style.opacity = 1 - h;
  el('yr').style.opacity = 1 - h;
}
""".replace("__CUES__", json.dumps([(i, (int(c[1:]) if c and c.startswith("w") else None)) for i, (_, c) in enumerate(CODE)]))

# ---------------------------------------------------------------- 5. compare: the same panel, a year apart
# The 2026 side is a Three.js scene: a hologram screen on a pedestal, framed to sit where the 2025 frame's
# panel sits (x 210-960, y 20-570) so the slider compares like with like. The screen's face is a canvas
# texture redrawn every frame — thumbnails, the three words, and the type guides all live on that texture,
# so they stay registered to the glass when the camera moves.
THREE_CDN = "".join(
    f"<script src='https://cdn.jsdelivr.net/npm/three@0.147.0/{p}.js'></script>"
    for p in [
        "build/three.min",
        "examples/js/shaders/CopyShader",
        "examples/js/shaders/LuminosityHighPassShader",
        "examples/js/postprocessing/EffectComposer",
        "examples/js/postprocessing/RenderPass",
        "examples/js/postprocessing/ShaderPass",
        "examples/js/postprocessing/UnrealBloomPass",
    ]
)
compare_html = f"""{THREE_CDN}
<div class='abs' style='font-family:Inter Tight;font-weight:800;opacity:0'>A</div>
<video id='v' src='{FOOTAGE}' muted playsinline preload='metadata' style='position:absolute;left:0;top:0;width:2px;height:2px;opacity:0'></video>
<canvas id='cv' width='1280' height='720' class='full'></canvas>
<div id='new' class='full' style='clip-path:inset(0 0 0 1280px)'>
  <div class='full' style='background:#030b12'></div>
  <canvas id='gl' width='1280' height='720' class='full'></canvas>
</div>
<div id='bar' class='abs' style='top:0;width:3px;height:720px;background:#fff;box-shadow:0 0 18px rgba(255,255,255,.9)'></div>
<div id='l25' class='abs mono warm' style='left:40px;top:36px;font-size:14px;letter-spacing:.2em;padding:6px 10px;background:rgba(0,0,0,.55);border-radius:4px'>2025 · VIDEO MODEL</div>
<div id='l26' class='abs mono cool' style='right:40px;top:36px;font-size:14px;letter-spacing:.2em;padding:6px 10px;background:rgba(0,0,0,.55);border-radius:4px'>2026 · CODE BY CLAUDE OPUS 5.5</div>
"""
compare_js = """
const FREEZE = __FREEZE__;
const WORDS = ['CREATIVITY', 'INNOVATION', 'CO-CREATION'];
const TW = 1500, TH = 1100;             // screen texture, 2x the panel's on-screen size
const PW = 7.5, PH = 5.5, CH = 0.45;    // screen size and corner chamfer, world units
let S = null;

const chamfer = (w, h, c) => {
  const s = new THREE.Shape();
  s.moveTo(-w / 2 + c, -h / 2); s.lineTo(w / 2 - c, -h / 2); s.lineTo(w / 2, -h / 2 + c); s.lineTo(w / 2, h / 2 - c);
  s.lineTo(w / 2 - c, h / 2); s.lineTo(-w / 2 + c, h / 2); s.lineTo(-w / 2, h / 2 - c); s.lineTo(-w / 2, -h / 2 + c); s.closePath();
  return s;
};
// ShapeGeometry's uv is the raw xy; remap it to 0..1 over the panel
const fitUV = (g, w, h) => { const p = g.attributes.position, uv = g.attributes.uv; for (let i = 0; i < p.count; i++) uv.setXY(i, p.getX(i) / w + 0.5, p.getY(i) / h + 0.5); uv.needsUpdate = true; return g; };
// the hole's chamfer is the outer one inset along the 45-degree edge; a larger one pokes out of the outline,
// the triangulation then fills the hole, and the frame becomes a tinted sheet over the whole screen
const ringOf = (w, h, c, th) => { const o = chamfer(w, h, c); o.holes.push(chamfer(w - th * 2, h - th * 2, Math.max(0.001, c - th * 0.4142))); return new THREE.ShapeGeometry(o); };
const radialTex = (inner, outer) => {
  const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
  const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, inner); gr.addColorStop(1, outer);
  g.fillStyle = gr; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(c);
};
const beamTex = () => {
  const c = document.createElement('canvas'); c.width = 8; c.height = 256; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 256, 0, 0); gr.addColorStop(0, 'rgba(120,220,255,.55)'); gr.addColorStop(1, 'rgba(120,220,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 8, 256); return new THREE.CanvasTexture(c);
};

const setup = () => {
  // alpha:false — with an alpha channel, the half-transparent glass let the 2025 frame underneath show through
  const R = new THREE.WebGLRenderer({ canvas: el('gl'), antialias: true, alpha: false, preserveDrawingBuffer: true });
  R.setPixelRatio(1); R.setSize(1280, 720, false); R.toneMapping = THREE.NoToneMapping;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x030b12); scene.fog = new THREE.FogExp2(0x030b12, 0.045);
  const cam = new THREE.PerspectiveCamera(35, 16 / 9, 0.1, 200);
  scene.add(new THREE.AmbientLight(0x3a6a88, 0.5));
  const key = new THREE.PointLight(0x5fd0ff, 2.4, 12, 1.6); key.position.set(0, -2.9, 1.8); scene.add(key);

  // floor with a faint grid, and the back wall's light strips
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: 0x06121b, metalness: 0.75, roughness: 0.32 }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = -3.8; scene.add(floor);
  const grid = new THREE.GridHelper(60, 60, 0x1f5f80, 0x0f3246); grid.position.y = -3.79; grid.material.transparent = true; grid.material.opacity = 0.45; scene.add(grid);
  for (let i = -6; i <= 6; i++) {
    if (Math.abs(i) < 2) continue;
    const strip = new THREE.Mesh(new THREE.PlaneGeometry(0.05, 9), new THREE.MeshBasicMaterial({ color: 0x2a86b0, transparent: true, opacity: 0.35 + 0.25 * rnd(i + 20) }));
    strip.position.set(i * 1.6, 1, -7 - rnd(i) * 2); scene.add(strip);
  }
  // pylons either side of the screen
  [-1, 1].forEach((sgn) => {
    const py = new THREE.Mesh(new THREE.BoxGeometry(0.34, 7.2, 0.34), new THREE.MeshStandardMaterial({ color: 0x0a1a26, metalness: 0.85, roughness: 0.3 }));
    py.position.set(sgn * 4.55, -0.1, -0.45); scene.add(py);
    const lit = new THREE.Mesh(new THREE.PlaneGeometry(0.05, 6.2), new THREE.MeshBasicMaterial({ color: 0x1f7fae }));
    lit.position.set(sgn * 4.55 - sgn * 0.0, -0.1, -0.27); scene.add(lit);
  });

  // pedestal: stacked discs, glowing rings, a turning dashed ring, and the light beam up to the screen
  const ped = new THREE.Group(); ped.position.set(0, -3.62, 0.2); scene.add(ped);
  const metal = new THREE.MeshStandardMaterial({ color: 0x0c1c28, metalness: 0.9, roughness: 0.28 });
  const d1 = new THREE.Mesh(new THREE.CylinderGeometry(2.25, 2.45, 0.28, 96), metal); d1.position.y = 0; ped.add(d1);
  const d2 = new THREE.Mesh(new THREE.CylinderGeometry(1.75, 1.95, 0.22, 96), metal); d2.position.y = 0.25; ped.add(d2);
  const glowMat = new THREE.MeshBasicMaterial({ color: 0x9fe8ff });
  [[2.3, 0.15, 0.03], [1.85, 0.37, 0.035], [1.35, 0.38, 0.02]].forEach(([r, y, tk]) => {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(r, tk, 12, 160), glowMat); ring.rotation.x = Math.PI / 2; ring.position.y = y; ped.add(ring);
  });
  const dash = new THREE.Group(); dash.position.y = 0.4; ped.add(dash);
  for (let k = 0; k < 18; k++) {
    const arc = new THREE.Mesh(new THREE.TorusGeometry(1.6, 0.025, 8, 24, Math.PI * 2 / 18 * 0.55), glowMat);
    arc.rotation.x = Math.PI / 2; arc.rotation.z = k * Math.PI * 2 / 18; dash.add(arc);
  }
  const beam = new THREE.Mesh(new THREE.CylinderGeometry(1.45, 1.6, 0.5, 96, 1, true),
    new THREE.MeshBasicMaterial({ map: beamTex(), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
  beam.position.y = 0.66; ped.add(beam);

  // the screen: glow behind, the textured face, an outer and an inner frame
  const scr = new THREE.Group(); scene.add(scr);
  const halo = new THREE.Mesh(new THREE.PlaneGeometry(12, 9), new THREE.MeshBasicMaterial({ map: radialTex('rgba(40,140,230,.35)', 'rgba(0,0,0,0)'), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  halo.position.z = -0.25; scr.add(halo);
  const tc = document.createElement('canvas'); tc.width = TW; tc.height = TH;
  const tex = new THREE.CanvasTexture(tc); tex.anisotropy = 8;
  const face = new THREE.Mesh(fitUV(new THREE.ShapeGeometry(chamfer(PW, PH, CH)), PW, PH), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, fog: false }));
  scr.add(face);
  const frame = new THREE.Mesh(ringOf(PW + 0.16, PH + 0.16, CH + 0.05, 0.075), new THREE.MeshBasicMaterial({ color: 0xe2f8ff, fog: false })); frame.position.z = 0.01; scr.add(frame);
  const frame2 = new THREE.Mesh(ringOf(PW - 0.22, PH - 0.22, CH - 0.1, 0.012), new THREE.MeshBasicMaterial({ color: 0x5cc8f0, transparent: true, opacity: 0.55, fog: false })); frame2.position.z = 0.01; scr.add(frame2);
  const back = new THREE.Mesh(new THREE.ShapeGeometry(chamfer(PW + 0.3, PH + 0.3, CH + 0.1)), new THREE.MeshBasicMaterial({ color: 0x02070c, fog: false }));
  back.position.z = -0.12; scr.add(back);

  // particles rising through the beam and drifting around the screen
  const N = 520, pos = new Float32Array(N * 3), seed = [];
  for (let i = 0; i < N; i++) seed.push([rnd(i * 1.7), rnd(i * 2.3), rnd(i * 3.1), rnd(i * 4.9)]);
  const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const dot = document.createElement('canvas'); dot.width = dot.height = 64; const dg = dot.getContext('2d');
  const rg = dg.createRadialGradient(32, 32, 0, 32, 32, 32); rg.addColorStop(0, 'rgba(255,255,255,1)'); rg.addColorStop(0.3, 'rgba(170,230,255,.8)'); rg.addColorStop(1, 'rgba(170,230,255,0)');
  dg.fillStyle = rg; dg.fillRect(0, 0, 64, 64);
  const pts = new THREE.Points(pg, new THREE.PointsMaterial({ size: 0.07, map: new THREE.CanvasTexture(dot), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, color: 0xbfeaff }));
  scene.add(pts);

  const composer = new THREE.EffectComposer(R);
  composer.addPass(new THREE.RenderPass(scene, cam));
  composer.addPass(new THREE.UnrealBloomPass(new THREE.Vector2(1280, 720), 0.8, 0.3, 0.95));
  return { R, scene, cam, composer, tc, tex, dash, pos, pg, seed, N, scr, beam };
};

// ---- the screen's face, drawn in texture pixels (1500 x 1100)
const thumb = (g, k, x, y, w, h, t) => {
  g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip();
  if (k === 0) {            // sunset over the sea
    const sky = g.createLinearGradient(0, y, 0, y + h); sky.addColorStop(0, '#2b1a4d'); sky.addColorStop(0.55, '#ff8a5c'); sky.addColorStop(0.56, '#1b3a5c'); sky.addColorStop(1, '#0a1a2c');
    g.fillStyle = sky; g.fillRect(x, y, w, h);
    g.fillStyle = '#ffd59a'; g.beginPath(); g.arc(x + w * 0.5, y + h * 0.55, h * 0.18, Math.PI, 0); g.fill();
    g.strokeStyle = 'rgba(255,200,150,.6)'; g.lineWidth = 2;
    for (let r = 0; r < 5; r++) { g.beginPath(); for (let i = 0; i <= w; i += 6) { const yy = y + h * (0.62 + r * 0.08) + Math.sin(i * 0.05 + t * 2 + r) * 3; i ? g.lineTo(x + i, yy) : g.moveTo(x + i, yy); } g.stroke(); }
  } else if (k === 1) {     // a city at night
    g.fillStyle = '#081426'; g.fillRect(x, y, w, h);
    for (let b = 0; b < 12; b++) {
      const bw = w / 12, bh = h * (0.35 + 0.5 * rnd(b * 9.1)), bx = x + b * bw;
      g.fillStyle = '#10243c'; g.fillRect(bx + 1, y + h - bh, bw - 2, bh);
      for (let wy = y + h - bh + 6; wy < y + h - 4; wy += 9) for (let wx = bx + 4; wx < bx + bw - 4; wx += 7) {
        if (rnd(wx * 3.3 + wy * 7.7 + Math.floor(t * 3 + rnd(wx) * 5)) > 0.55) { g.fillStyle = 'rgba(255,214,140,.9)'; g.fillRect(wx, wy, 3, 4); }
      }
    }
  } else if (k === 2) {     // a turning galaxy
    g.fillStyle = '#05060f'; g.fillRect(x, y, w, h);
    for (let i = 0; i < 260; i++) {
      const a = rnd(i) * 6.283 + t * 0.6 + (i % 2) * Math.PI, rr = Math.pow(rnd(i * 5.1), 0.7) * h * 0.55, sw = a + rr * 0.04;
      g.fillStyle = `rgba(${180 + 75 * rnd(i * 2)},${170 + 60 * rnd(i * 3)},255,${0.4 + 0.6 * rnd(i * 4)})`;
      g.fillRect(x + w / 2 + Math.cos(sw) * rr * 1.5, y + h / 2 + Math.sin(sw) * rr * 0.6, 2, 2);
    }
  } else if (k === 3) {     // a waveform
    g.fillStyle = '#071a1f'; g.fillRect(x, y, w, h);
    for (let i = 0; i < 38; i++) {
      const v = 0.2 + 0.8 * Math.abs(Math.sin(i * 0.7 + t * 5) * Math.sin(i * 0.23 + t * 1.3));
      g.fillStyle = `hsl(${170 + i * 2},80%,60%)`; g.fillRect(x + 8 + i * (w - 16) / 38, y + h / 2 - v * h * 0.38, (w - 16) / 38 - 2, v * h * 0.76);
    }
  } else {                  // a portrait in rim light
    const bg = g.createLinearGradient(x, y, x + w, y + h); bg.addColorStop(0, '#1d1236'); bg.addColorStop(1, '#0a1630'); g.fillStyle = bg; g.fillRect(x, y, w, h);
    const cx = x + w * 0.5 + Math.sin(t * 0.8) * 4;
    g.fillStyle = '#05070c'; g.beginPath(); g.arc(cx, y + h * 0.42, h * 0.2, 0, 6.283); g.fill();
    g.beginPath(); g.ellipse(cx, y + h * 1.02, w * 0.3, h * 0.38, 0, Math.PI, 0); g.fill();
    g.strokeStyle = 'rgba(255,170,120,.9)'; g.lineWidth = 3; g.beginPath(); g.arc(cx, y + h * 0.42, h * 0.2, -1.2, 0.6); g.stroke();
  }
  // scanlines over each thumbnail
  g.fillStyle = 'rgba(0,0,0,.18)'; for (let yy = y; yy < y + h; yy += 4) g.fillRect(x, yy, w, 1);
  g.restore();
  g.strokeStyle = 'rgba(150,225,255,.75)'; g.lineWidth = 2; g.strokeRect(x, y, w, h);
  g.fillStyle = 'rgba(150,225,255,.8)'; g.font = "600 15px 'JetBrains Mono'"; g.fillText('SCENE ' + pad(k + 1, 2), x + 8, y + h + 22);
};

const drawFace = (tc, t, frame) => {
  const g = tc.getContext('2d');
  g.clearRect(0, 0, TW, TH);
  const bg = g.createLinearGradient(0, 0, 0, TH); bg.addColorStop(0, 'rgba(12,46,70,.94)'); bg.addColorStop(1, 'rgba(5,22,36,.97)');
  g.fillStyle = bg; g.fillRect(0, 0, TW, TH);
  // fine dot grid and slow scanlines
  g.fillStyle = 'rgba(120,200,240,.10)'; for (let y = 20; y < TH; y += 30) for (let x = 20; x < TW; x += 30) g.fillRect(x, y, 2, 2);
  g.fillStyle = 'rgba(160,230,255,.05)'; const off = (t * 60) % 6; for (let y = off; y < TH; y += 6) g.fillRect(0, y, TW, 2);
  const sweep = ((t * 0.45) % 1.3) * TH; const sg = g.createLinearGradient(0, sweep - 90, 0, sweep); sg.addColorStop(0, 'rgba(160,230,255,0)'); sg.addColorStop(1, 'rgba(160,230,255,.10)');
  g.fillStyle = sg; g.fillRect(0, sweep - 90, TW, 90);
  // thumbnails
  for (let k = 0; k < 5; k++) thumb(g, k, 120 + k * 256, 70, 236, 136, t + k);
  // the three words, lifting away at the end of the beat
  const lift = ease(seg(t, 5.0, 5.4));
  g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.font = "800 150px 'Inter Tight'";
  const rows = [470, 680, 890];
  const boxes = [];
  WORDS.forEach((w, i) => {
    const y = rows[i] - lift * (60 + i * 30);
    g.save(); g.globalAlpha = 1 - lift;
    // kept just under the bloom threshold (0.95) so the letters stay sharp; the glow is the canvas shadow
    g.shadowColor = 'rgba(110,210,255,.8)'; g.shadowBlur = 22; g.fillStyle = '#e4f2f9'; g.fillText(w, TW / 2, y);
    g.shadowBlur = 0; g.fillText(w, TW / 2, y);
    g.restore();
    // letter boxes, measured from the same font the words were drawn with
    let x = TW / 2 - g.measureText(w).width / 2;
    for (const ch of w) { const cw = g.measureText(ch).width; boxes.push([x, y - 110, cw, 112, i]); x += cw; }
  });
  // "Every letter," — a box lights on each letter in turn; "exactly where it belongs" — baselines and cap lines
  const gone = 1 - seg(t, 4.9, 5.2);
  boxes.forEach((b, j) => {
    const at = 2.35 + j * (0.8 / boxes.length);
    const a = (t >= at ? 1 - 0.7 * seg(t, at + 0.25, at + 0.9) : 0) * gone;
    if (a <= 0) return;
    g.strokeStyle = `rgba(255,95,220,${a})`; g.lineWidth = 2; g.strokeRect(b[0] + 1, b[1], b[2] - 2, b[3]);
  });
  rows.forEach((y, i) => {
    const a = seg(t, 3.7 + i * 0.08, 4.1 + i * 0.08) * gone;
    if (a <= 0) return;
    g.strokeStyle = `rgba(255,95,220,${a * 0.9})`; g.lineWidth = 2;
    g.setLineDash([12, 9]); g.beginPath(); g.moveTo(60, y + 2); g.lineTo(TW - 60, y + 2); g.stroke();
    g.setLineDash([3, 10]); g.beginPath(); g.moveTo(60, y - 108); g.lineTo(TW - 60, y - 108); g.stroke();
    g.setLineDash([]);
    g.fillStyle = `rgba(255,160,235,${a})`; g.font = "600 20px 'JetBrains Mono'"; g.textAlign = 'left';
    g.fillText('baseline', TW - 190, y - 10); g.textAlign = 'center'; g.font = "800 150px 'Inter Tight'";
  });
  // HUD strip along the bottom edge: this film's own frame count
  g.textAlign = 'left'; g.font = "600 22px 'JetBrains Mono'"; g.fillStyle = 'rgba(150,225,255,.85)';
  const gf = START + frame;
  g.fillText('RENDER ' + pad(gf, 4) + ' / ' + pad(TOTAL_FRAMES, 4) + '   30 FPS   1280×720', 120, 1010);
  g.fillStyle = 'rgba(150,225,255,.25)'; g.fillRect(120, 1030, 1260, 6);
  g.fillStyle = 'rgba(170,235,255,.95)'; g.fillRect(120, 1030, 1260 * gf / TOTAL_FRAMES, 6);
  // edge ticks
  g.fillStyle = 'rgba(150,225,255,.55)';
  for (let y = 250; y < 960; y += 24) { g.fillRect(34, y, y % 96 === 58 ? 26 : 12, 2); g.fillRect(TW - 34 - (y % 96 === 58 ? 26 : 12), y, y % 96 === 58 ? 26 : 12, 2); }
};

async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  if (!S) S = setup();
  // camera: a slow drift that keeps the screen where the 2025 panel was
  const k = ease(seg(t, 0, 5.4));
  S.cam.position.set(lerp(0.85, 0.3, k), lerp(-0.25, -0.4, k), lerp(11.7, 11.25, k));
  S.cam.lookAt(0.55, -0.65, 0);
  S.scr.position.y = Math.sin(t * 1.3) * 0.04;
  S.dash.rotation.y = t * 0.6;
  S.beam.material.opacity = 0.85 + 0.15 * Math.sin(t * 9);
  for (let i = 0; i < S.N; i++) {
    const [a, b, c, d] = S.seed[i];
    let x, y, z;
    if (i < S.N * 0.55) {       // inside the beam, rising and fading into the screen
      const h = (b + t * (0.25 + 0.35 * c)) % 1;
      const r = (0.3 + 1.2 * a) * (1 - h * 0.25), ang = d * 6.283 + t * 0.5;
      x = Math.cos(ang) * r; z = 0.2 + Math.sin(ang) * r * 0.6; y = -3.1 + h * 3.2;
    } else {                    // dust drifting through the room
      x = (a - 0.5) * 16 + Math.sin(t * 0.3 + d * 6) * 0.3; y = -3.2 + ((b * 7 + t * 0.12 * (0.5 + c)) % 7); z = (c - 0.5) * 8 - 1;
    }
    S.pos[i * 3] = x; S.pos[i * 3 + 1] = y; S.pos[i * 3 + 2] = z;
  }
  S.pg.attributes.position.needsUpdate = true;
  drawFace(S.tc, t, frame); S.tex.needsUpdate = true;
  S.composer.render();

  // the slider: the preview from the last beat arrives as the right half, then sweeps across on "exactly"
  const s1 = ease(seg(t, 0.0, 0.9)), s2 = ease(seg(t, 3.55, 4.6));
  const x = lerp(lerp(1280, 640, s1), 0, s2);
  el('new').style.clipPath = `inset(0 0 0 ${x}px)`;
  el('bar').style.left = (x - 1.5) + 'px';
  el('bar').style.opacity = x > 2 && x < 1278 ? 1 : 0;
  el('l25').style.opacity = clamp01((x - 300) / 200);
  el('l26').style.opacity = seg(t, 0.3, 0.6);
  return paint('v', 'cv', FREEZE);
}
""".replace("__FREEZE__", str(FREEZE))

# ---------------------------------------------------------------- 6. close: one year apart
TITLE = "AI SHORT FILM FES 2025"
title_spans = "".join(
    f"<span class='tl' style='display:inline-block;{'width:26px' if c == ' ' else ''}'>{c if c != ' ' else '&nbsp;'}</span>" for c in TITLE
)
close_html = f"""
<div class='full' style='background:radial-gradient(ellipse at 50% 40%,#0c2331 0%,#050a0e 60%,#020304 100%)'></div>
<div class='abs' style='left:0;top:150px;width:1280px;text-align:center;font-size:88px;font-weight:900;letter-spacing:.02em;color:#f4f8fb'>{title_spans}</div>
<div id='sub' class='abs mono' style='left:0;top:262px;width:1280px;text-align:center;font-size:17px;letter-spacing:.34em;color:#8fc9e8;opacity:0'>THE TRAILER, REMADE ONE YEAR LATER</div>
<div id='tlw' class='abs' style='left:340px;top:330px;width:600px;height:60px'>
  <div id='lnw' class='abs' style='left:10px;top:17px;width:580px;height:2px;background:linear-gradient(90deg,#e9dcc4,#bfe8ff);transform-origin:0 50%;transform:scaleX(0)'></div>
  <div id='d1' class='abs' style='left:0;top:8px;width:20px;height:20px;border-radius:10px;background:#e9dcc4;opacity:0'></div>
  <div id='d2' class='abs' style='left:580px;top:8px;width:20px;height:20px;border-radius:10px;background:#bfe8ff;box-shadow:0 0 16px #39b8ff;opacity:0'></div>
  <div id='t1' class='abs mono warm' style='left:-90px;top:38px;width:200px;text-align:center;font-size:18px;opacity:0'>2025 · original</div>
  <div id='t2' class='abs mono cool' style='left:490px;top:38px;width:200px;text-align:center;font-size:18px;opacity:0'>2026 · remake</div>
  <div id='tm' class='abs serif' style='left:0;width:600px;top:-26px;text-align:center;font-size:24px;font-style:italic;color:#c9d6de;opacity:0'>one year</div>
</div>
<div id='q' class='abs serif' style='left:0;top:430px;width:1280px;text-align:center;font-size:54px;font-style:italic;color:#f4f1ea;opacity:0'>The trailer we wish we’d made.</div>
<div id='pw' class='abs mono' style='left:0;top:560px;width:1280px;text-align:center;font-size:15px;letter-spacing:.32em;color:#8fc9e8;opacity:0'>POWERED BY MULMOCAST</div>
<div id='cr' class='abs mono' style='left:0;top:640px;width:1280px;text-align:center;font-size:12px;letter-spacing:.08em;color:#5c7a8c;opacity:0'>A 2026 remake of the AI Short Film Fes 2025 trailer · {TOTAL_FRAMES} frames, rendered from code written by Claude Opus 5.5 · archive footage: the original 2025 trailer</div>
<div id='fade' class='full' style='background:#000;opacity:0'></div>
"""
close_js = """
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  // the letters gather from where the compare words scattered
  document.querySelectorAll('.tl').forEach((sp, i) => {
    const p = easeOut(seg(t, 0.0 + i * 0.03, 0.75 + i * 0.03));
    const dx = (rnd(i * 13.7) - 0.5) * 700, dy = (rnd(i * 7.3) - 0.2) * 420, rot = (rnd(i * 3.1) - 0.5) * 90;
    sp.style.transform = `translate(${dx * (1 - p)}px,${dy * (1 - p)}px) rotate(${rot * (1 - p)}deg)`;
    sp.style.opacity = seg(t, i * 0.03, 0.3 + i * 0.03);
    sp.style.filter = `blur(${(1 - p) * 8}px)`;
  });
  // "One year apart." — two points and the line between them
  el('d1').style.opacity = seg(t, 0.45, 0.6); el('t1').style.opacity = seg(t, 0.5, 0.7);
  el('lnw').style.transform = `scaleX(${ease(seg(t, 0.6, 1.5))})`;
  const p2 = back(seg(t, 1.45, 1.8)); el('d2').style.opacity = seg(t, 1.45, 1.55); el('d2').style.transform = `scale(${p2})`;
  el('t2').style.opacity = seg(t, 1.5, 1.7); el('tm').style.opacity = seg(t, 1.0, 1.4); el('sub').style.opacity = seg(t, 0.7, 1.1);
  // "The trailer we wish we'd made."
  el('q').style.opacity = seg(t, 2.85, 3.2); el('q').style.transform = `translateY(${lerp(12, 0, easeOut(seg(t, 2.85, 3.3)))}px)`;
  el('pw').style.opacity = seg(t, 3.7, 4.0); el('cr').style.opacity = 0.9 * seg(t, 3.9, 4.2);
  el('fade').style.opacity = seg(t, 5.05, 5.3);
}
"""

deck = {
    "$mulmocast": {"version": "1.1"},
    "title": "One Year Apart — the AI Short Film Fes 2025 trailer, remade",
    "description": "A look back: the AI Short Film Fes 2025 trailer, filmed by a video model, remade a year later with every frame drawn by code written by Claude Opus 5.5.",
    "lang": "en",
    "canvasSize": {"width": 1280, "height": 720},
    "speechParams": {"speakers": {"Narrator": SPEAKER}},
    "audioParams": {
        "padding": 0, "introPadding": 0, "closingPadding": 0, "outroPadding": 0,
        "bgmVolume": 0.22, "audioVolume": 1.0,
        "bgm": {"kind": "path", "path": "bgm/bgm.mp3"},
    },
    "beats": [
        beat("archive", archive_html, archive_js),
        beat("melt", melt_html, melt_js),
        beat("cut", cut_html, cut_js),
        beat("code", code_html, code_js),
        beat("compare", compare_html, compare_js),
        beat("close", close_html, close_js),
    ],
}

with open(os.path.join(HERE, "filmfes_one_year.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("ok", TOTAL_FRAMES, "frames")
