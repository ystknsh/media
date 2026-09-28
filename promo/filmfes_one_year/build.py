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
    "close": "One year apart. What will you make next?",
}
# seconds; each is >= its narration (archive 6.82, melt 4.49, code 7.37, compare 5.33, close 4.61)
TIMING = {"archive": 6.9, "melt": 4.6, "cut": 0.9, "code": 7.4, "compare": 5.4, "close": 4.8}

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
    <span class='mono' style='margin-left:14px;font-size:14px;color:#8aa0b4'>trailer_2026.js</span>
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
# The 2026 panel is drawn over the 2025 frame's geometry: panel x 210-960, y 20-570, word lines centred at x 585.
panel_words = "".join(
    f"<div id='cw{i}' style='position:absolute;left:0;width:1170px;top:{150 + i * 108}px;text-align:center;font-size:84px;line-height:84px;font-weight:800;letter-spacing:.03em;color:#eaf7ff;text-shadow:0 0 18px rgba(120,210,255,.55)'>{letters(w, 'cl' + str(i))}</div>"
    for i, w in enumerate(WORDS)
)
tiles = "".join(
    f"<div style='position:absolute;left:{262 + k * 138}px;top:52px;width:124px;height:72px;border-radius:4px;background:linear-gradient(135deg,hsl({190 + k * 14},60%,{22 + (k % 2) * 8}%),hsl({210 + k * 9},55%,12%));border:1px solid rgba(160,220,255,.35)'></div>"
    for k in range(5)
)
compare_html = f"""
<video id='v' src='{FOOTAGE}' muted playsinline preload='metadata' style='position:absolute;left:0;top:0;width:2px;height:2px;opacity:0'></video>
<canvas id='cv' width='1280' height='720' class='full'></canvas>
<div id='new' class='full' style='clip-path:inset(0 0 0 1280px)'>
  <div class='full' style='background:radial-gradient(ellipse at 45% 45%,#0e2d3f 0%,#061720 55%,#03090d 100%)'></div>
  <svg class='full' viewBox='0 0 1280 720'>
    <polygon points='250,20 920,20 960,70 960,520 920,570 250,570 210,520 210,70' fill='rgba(8,30,44,.85)' stroke='#7fd8ff' stroke-width='3' style='filter:drop-shadow(0 0 10px #39b8ff)'/>
    <polygon points='262,34 908,34 944,76 944,512 908,556 262,556 226,512 226,76' fill='none' stroke='rgba(127,216,255,.35)' stroke-width='1'/>
    <ellipse cx='585' cy='620' rx='190' ry='26' fill='none' stroke='#9fe6ff' stroke-width='3' style='filter:drop-shadow(0 0 12px #39b8ff)'/>
  </svg>
  {tiles}
  <div class='abs' style='left:0;top:0;width:1170px'>{panel_words}</div>
  <svg id='guides' class='full' viewBox='0 0 1280 720' style='opacity:0'></svg>
</div>
<div id='bar' class='abs' style='top:0;width:3px;height:720px;background:#fff;box-shadow:0 0 18px rgba(255,255,255,.9)'></div>
<div id='l25' class='abs mono warm' style='left:40px;top:36px;font-size:14px;letter-spacing:.2em;padding:6px 10px;background:rgba(0,0,0,.55);border-radius:4px'>2025 · VIDEO MODEL</div>
<div id='l26' class='abs mono cool' style='right:40px;top:36px;font-size:14px;letter-spacing:.2em;padding:6px 10px;background:rgba(0,0,0,.55);border-radius:4px'>2026 · CODE BY CLAUDE OPUS 5.5</div>
"""
compare_js = """
const FREEZE = __FREEZE__;
let boxes = null;
async function render(frame, totalFrames, fps) {
  await waitFonts();
  const t = frame / fps;
  // the preview from the last beat arrives as the right half; "Same words." holds at the middle
  const s1 = ease(seg(t, 0.0, 0.9)), s2 = ease(seg(t, 3.55, 4.6));
  const x = lerp(lerp(1280, 640, s1), 0, s2);
  el('new').style.clipPath = `inset(0 0 0 ${x}px)`;
  el('bar').style.left = (x - 1.5) + 'px';
  el('bar').style.opacity = x > 2 && x < 1278 ? 1 : 0;
  el('l25').style.opacity = clamp01((x - 300) / 200);
  el('l26').style.opacity = seg(t, 0.3, 0.6);
  // "Every letter," — a box lights on each letter in turn
  if (!boxes) {
    boxes = [...document.querySelectorAll('[class^="cl"]')].map((sp) => { const r = sp.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; });
    const svg = el('guides');
    let g = '';
    boxes.forEach((b, i) => { g += `<rect class='bx' x='${b[0]}' y='${b[1] + 8}' width='${b[2]}' height='${b[3] - 16}' fill='none' stroke='#ff4fd8' stroke-width='1.5' opacity='0'/>`; });
    [0, 1, 2].forEach((i) => {
      const r = el('cw' + i).getBoundingClientRect(); const base = r.top + 76, cap = r.top + 16;
      g += `<line class='gl' x1='190' x2='980' y1='${base}' y2='${base}' stroke='#ff4fd8' stroke-width='1' stroke-dasharray='6 5' opacity='0'/>`;
      g += `<line class='gl' x1='190' x2='980' y1='${cap}' y2='${cap}' stroke='#ff4fd8' stroke-width='1' stroke-dasharray='2 6' opacity='0'/>`;
      g += `<text class='gl' x='992' y='${base + 4}' fill='#ff9be9' font-family='JetBrains Mono' font-size='12' opacity='0'>baseline ${Math.round(base)}px</text>`;
    });
    svg.innerHTML = g;
  }
  el('guides').style.opacity = 1;
  const bx = [...document.querySelectorAll('.bx')];
  bx.forEach((r, i) => {
    const at = 2.35 + i * (0.8 / bx.length);
    r.setAttribute('opacity', (t >= at ? 1 - 0.75 * seg(t, at + 0.25, at + 0.9) : 0) * (1 - seg(t, 4.9, 5.2)));
  });
  document.querySelectorAll('.gl').forEach((g, i) => g.setAttribute('opacity', seg(t, 3.7 + i * 0.05, 4.1 + i * 0.05) * (1 - seg(t, 4.9, 5.2))));
  // hand over: the words lift toward the title
  const lift = ease(seg(t, 5.0, 5.4));
  [0, 1, 2].forEach((i) => { el('cw' + i).style.transform = `translateY(${-lift * (40 + i * 20)}px)`; el('cw' + i).style.opacity = 1 - lift; });
  return paint('v', 'cv', FREEZE);
}
""".replace("__FREEZE__", str(FREEZE))

# ---------------------------------------------------------------- 6. close: one year apart
TITLE = "AI SHORT FILM FES"
title_spans = "".join(
    f"<span class='tl' style='display:inline-block;{'width:26px' if c == ' ' else ''}'>{c if c != ' ' else '&nbsp;'}</span>" for c in TITLE
)
close_html = f"""
<div class='full' style='background:radial-gradient(ellipse at 50% 40%,#0c2331 0%,#050a0e 60%,#020304 100%)'></div>
<div class='abs' style='left:0;top:170px;width:1280px;text-align:center;font-size:96px;font-weight:900;letter-spacing:.02em;color:#f4f8fb'>{title_spans}</div>
<div id='tlw' class='abs' style='left:340px;top:330px;width:600px;height:60px'>
  <div id='lnw' class='abs' style='left:10px;top:17px;width:580px;height:2px;background:linear-gradient(90deg,#e9dcc4,#bfe8ff);transform-origin:0 50%;transform:scaleX(0)'></div>
  <div id='d1' class='abs' style='left:0;top:8px;width:20px;height:20px;border-radius:10px;background:#e9dcc4;opacity:0'></div>
  <div id='d2' class='abs' style='left:580px;top:8px;width:20px;height:20px;border-radius:10px;background:#bfe8ff;box-shadow:0 0 16px #39b8ff;opacity:0'></div>
  <div id='t1' class='abs mono warm' style='left:-30px;top:38px;width:80px;text-align:center;font-size:18px;opacity:0'>2025</div>
  <div id='t2' class='abs mono cool' style='left:550px;top:38px;width:80px;text-align:center;font-size:18px;opacity:0'>2026</div>
  <div id='tm' class='abs serif' style='left:0;width:600px;top:-26px;text-align:center;font-size:24px;font-style:italic;color:#c9d6de;opacity:0'>one year</div>
</div>
<div id='q' class='abs serif' style='left:0;top:430px;width:1280px;text-align:center;font-size:54px;font-style:italic;color:#f4f1ea;opacity:0'>What will you make next?</div>
<div id='pw' class='abs mono' style='left:0;top:560px;width:1280px;text-align:center;font-size:15px;letter-spacing:.32em;color:#8fc9e8;opacity:0'>POWERED BY MULMOCAST</div>
<div id='cr' class='abs mono' style='left:0;top:640px;width:1280px;text-align:center;font-size:12px;letter-spacing:.08em;color:#5c7a8c;opacity:0'>{TOTAL_FRAMES} frames, rendered from code written by Claude Opus 5.5 · archive footage: AI Short Film Fes 2025 trailer</div>
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
  el('t2').style.opacity = seg(t, 1.5, 1.7); el('tm').style.opacity = seg(t, 1.0, 1.4);
  // "What will you make next?"
  el('q').style.opacity = seg(t, 2.75, 3.1); el('q').style.transform = `translateY(${lerp(12, 0, easeOut(seg(t, 2.75, 3.2)))}px)`;
  el('pw').style.opacity = seg(t, 3.5, 3.8); el('cr').style.opacity = 0.9 * seg(t, 3.7, 4.0);
  el('fade').style.opacity = seg(t, 4.55, 4.8);
}
"""

deck = {
    "$mulmocast": {"version": "1.1"},
    "title": "One Year Apart — AI Short Film Fes",
    "description": "The 2025 AI Short Film Fes trailer was filmed by a video model; in 2026 every frame is drawn by code written by Claude Opus 5.5.",
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
