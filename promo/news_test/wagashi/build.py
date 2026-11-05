"""30-second news explainer: 和菓子店の倒産（帝国データバンク, 2026-10-03）. All visuals are html_tailwind; only TTS costs."""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
REPO = pathlib.Path(__file__).resolve().parents[4] / "mulmo-presentations"

HELPERS = """
function clamp01(x) { return Math.max(0, Math.min(1, x)); }
function P(t, a, b) { return clamp01((t - a) / (b - a)); }
function eout(x) { return 1 - Math.pow(1 - x, 3); }
function eback(x) { var c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); }
function $(id) { return document.getElementById(id); }
"""
INK, PAPER, RED, GOLD, AI = "#2b1a12", "#f6efe1", "#b3261e", "#c8963e", "#25365c"
FONT = ("<style>.m{font-family:'Hiragino Mincho ProN','Yu Mincho',serif}.g{font-family:'Hiragino Sans','Helvetica Neue',sans-serif}"
        ".manju{border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff7ea,#ead6b4 55%,#c9a77a)}</style>")


def chrome(inner):
    return (f"{FONT}<div class='m relative overflow-hidden' style='width:1280px;height:720px;color:{INK};"
            f"background:radial-gradient(900px 600px at 50% 40%,#fbf6ea,{PAPER} 60%,#e9dcc2)'>"
            "<div class='absolute inset-0' style='opacity:.18;background:repeating-linear-gradient(90deg,transparent 0 38px,#d8c7a5 38px 39px)'></div>"
            f"{inner}"
            f"<div class='g absolute left-0 top-0 flex items-center' style='height:46px'>"
            f"<div class='h-full px-5 flex items-center font-bold text-white' style='background:{RED};letter-spacing:.2em'>NEWS</div>"
            f"<div class='h-full px-5 flex items-center font-bold' style='background:{INK};color:{PAPER}'>和菓子店の倒産 過去最多ペース</div></div>"
            f"<div class='g absolute right-6 bottom-4 text-sm' style='opacity:.65'>出典: 帝国データバンク（2026年10月3日）</div>"
            "</div>")


def beat(bid, text, inner, script):
    return {"id": bid, "text": text,
            "image": {"type": "html_tailwind", "html": chrome(inner), "script": HELPERS + script, "animation": {"fps": 30}}}


# 1. Title: brush-wipe headline + red seal
b1 = beat("open", "和菓子店の倒産が、過去最多のペースです。", f"""
<div class='absolute' style='left:120px;top:170px'>
  <div id='k' class='g font-bold tracking-[0.4em] text-2xl' style='color:{RED};opacity:0'>2026年 1〜9月</div>
  <div class='relative mt-4' style='font-size:118px;line-height:1.15;font-weight:800'>
    <div style='overflow:hidden'><div id='l1' style='clip-path:inset(0 100% 0 0)'>和菓子店の倒産</div></div>
    <div style='overflow:hidden'><div id='l2' style='clip-path:inset(0 100% 0 0)'>過去最多ペース</div></div>
  </div>
</div>
<div id='seal' class='absolute flex items-center justify-center' style='right:120px;top:330px;width:190px;height:190px;border:9px solid {RED};color:{RED};border-radius:14px;font-size:62px;font-weight:900;line-height:1.05;text-align:center;opacity:0;transform:rotate(-8deg)'>過去<br>最多</div>
<div id='mj' class='manju absolute' style='left:1010px;top:150px;width:120px;height:90px;opacity:0'></div>
""", """
function render(frame, total, fps) {
  var t = frame / fps;
  $('k').style.opacity = P(t, 0.1, 0.5);
  $('l1').style.clipPath = 'inset(0 ' + (100 - eout(P(t, 0.3, 1.2)) * 100) + '% 0 0)';
  $('l2').style.clipPath = 'inset(0 ' + (100 - eout(P(t, 0.9, 1.8)) * 100) + '% 0 0)';
  var s = P(t, 2.0, 2.25); $('seal').style.opacity = s;
  $('seal').style.transform = 'rotate(-8deg) scale(' + (2.4 - 1.4 * eout(s)) + ')';
  var m = P(t, 0.6, 1.3); $('mj').style.opacity = m; $('mj').style.transform = 'translateY(' + (-40 * (1 - eback(m))) + 'px)';
}""")

# 2. Count: 22 manju fall into a box, counter
b2 = beat("count", "帝国データバンクによると、今年1月から9月で22件。", f"""
<div class='absolute' style='left:110px;top:180px'>
  <div class='g text-2xl font-bold' style='opacity:.7'>和菓子店の倒産件数（1〜9月）</div>
  <div class='flex items-end mt-2'><div id='n' style='font-size:240px;line-height:1;font-weight:900;color:{RED}'>0</div><div style='font-size:72px;font-weight:800;margin:0 0 30px 14px'>件</div></div>
  <div id='pace' class='g mt-2 px-4 py-2 inline-block text-2xl font-bold text-white' style='background:{INK};opacity:0'>過去最多のペース</div>
</div>
<div class='absolute' style='left:640px;top:140px;width:540px;height:470px;border-bottom:6px solid {INK}'>
  <div id='box' class='absolute inset-0'></div>
</div>
""", """
var N = 22, box = $('box'), mj = [];
for (var i = 0; i < N; i++) {
  var d = document.createElement('div'); d.className = 'manju absolute';
  var col = i % 6, row = Math.floor(i / 6);
  d.style.cssText = 'width:80px;height:60px;left:' + (12 + col * 88 + (row % 2) * 40) + 'px;bottom:' + (6 + row * 64) + 'px';
  box.appendChild(d); mj.push(d);
}
function render(frame, total, fps) {
  var t = frame / fps, shown = 0;
  for (var i = 0; i < N; i++) {
    var a = 0.4 + i * 0.13, p = P(t, a, a + 0.45);
    mj[i].style.opacity = p > 0 ? 1 : 0;
    mj[i].style.transform = 'translateY(' + (-560 * (1 - eout(p))) + 'px)';
    if (p >= 1) shown++;
  }
  $('n').textContent = shown;
  $('pace').style.opacity = P(t, 3.9, 4.3);
}""")

# 3. Old shops: 138 dots, 24 = 100+ years, half = 50+ years
b3 = beat("shinise", "2020年以降の138件では、業歴100年以上の老舗が24件。50年以上なら半数です。", f"""
<div class='absolute' style='left:90px;top:110px'>
  <div class='g text-2xl font-bold' style='opacity:.7'>2020年以降の倒産 138件</div>
</div>
<div id='grid' class='absolute' style='left:90px;top:170px;width:620px'></div>
<div class='absolute' style='left:780px;top:210px'>
  <div id='c1' style='opacity:0'><div class='g text-2xl font-bold'>業歴100年以上</div>
    <div class='flex items-end'><div style='font-size:120px;line-height:1;font-weight:900;color:{RED}'>24</div><div class='text-5xl font-bold mb-3 ml-2'>件</div><div class='g text-3xl font-bold mb-4 ml-4' style='color:{RED}'>17.4%</div></div></div>
  <div id='c2' class='mt-10' style='opacity:0'><div class='g text-2xl font-bold'>業歴50年以上</div>
    <div style='font-size:96px;line-height:1.1;font-weight:900;color:{GOLD}'>半数</div></div>
</div>
""", f"""
var g = $('grid'), dots = [];
for (var i = 0; i < 138; i++) {{
  var d = document.createElement('div');
  d.style.cssText = 'position:absolute;width:30px;height:30px;border-radius:50%;background:#d9c7a6;left:' + ((i % 15) * 41) + 'px;top:' + (Math.floor(i / 15) * 41) + 'px';
  g.appendChild(d); dots.push(d);
}}
function render(frame, total, fps) {{
  var t = frame / fps;
  for (var i = 0; i < 138; i++) {{
    var p = P(t, 0.05 + i * 0.006, 0.35 + i * 0.006); dots[i].style.opacity = p; dots[i].style.transform = 'scale(' + eback(p) + ')';
    var red = i < 24 && t > 1.5 + i * 0.03, gold = i < 69 && t > 4.2 + (i - 24) * 0.02;
    dots[i].style.background = red ? '{RED}' : (gold ? '{GOLD}' : '#d9c7a6');
  }}
  var a = P(t, 1.6, 2.1); $('c1').style.opacity = a; $('c1').style.transform = 'translateX(' + (30 * (1 - eout(a))) + 'px)';
  var b = P(t, 4.3, 4.8); $('c2').style.opacity = b; $('c2').style.transform = 'translateX(' + (30 * (1 - eout(b))) + 'px)';
}}""")

# 4. Pressures: weights stack on a manju that squashes
b4 = beat("pressure", "原材料高に、職人の高齢化、技術の継承。値上げしにくいことも重荷です。", f"""
<div id='stack' class='absolute' style='left:410px;top:0;width:460px;height:720px'></div>
<div id='mj' class='manju absolute' style='left:490px;top:520px;width:300px;height:150px;transform-origin:50% 100%'></div>
<div class='absolute' style='left:0;right:0;top:670px;height:8px;background:{INK}'></div>
""", f"""
var L = ['原材料高', '職人の高齢化', '技術承継の難しさ', '値上げへの抵抗感'], C = ['{RED}', '{AI}', '{INK}', '{GOLD}'], st = $('stack'), ws = [];
L.forEach(function (s, i) {{
  var d = document.createElement('div');
  d.className = 'g absolute flex items-center justify-center text-white font-bold';
  d.style.cssText += 'left:' + (20 + (i % 2) * 20) + 'px;width:400px;height:74px;font-size:34px;border-radius:6px;background:' + C[i];
  d.textContent = s; st.appendChild(d); ws.push(d);
}});
function render(frame, total, fps) {{
  var t = frame / fps, landed = 0;
  ws.forEach(function (d, i) {{
    var a = 0.3 + i * 1.15, p = P(t, a, a + 0.5), sq = 0;
    for (var k = 0; k < 4; k++) if (t > 0.8 + k * 1.15) sq = k + 1;
    var y = 520 - (i + 1) * 78 + Math.min(sq, 4) * 9;
    d.style.top = (-100 + (y + 100) * (p * p)) + 'px'; d.style.opacity = p > 0 ? 1 : 0;
    if (p >= 1) landed++;
  }});
  var bounce = 0; for (var k = 0; k < 4; k++) {{ var q = P(t, 0.8 + k * 1.15, 1.1 + k * 1.15); bounce += Math.sin(q * Math.PI) * 0.06; }}
  var sy = 1 - landed * 0.09 - bounce;
  $('mj').style.transform = 'scale(' + (1 + (1 - sy) * 0.5) + ',' + sy + ')';
}}""")

# 5. Way out: chips rise, light warms up
b5 = beat("hope", "一方、インバウンドや通販、「ネオ和菓子」で伸びる店もあります。", f"""
<div id='glow' class='absolute inset-0' style='opacity:0;background:radial-gradient(700px 420px at 50% 55%,rgba(255,214,140,.75),transparent 70%)'></div>
<div class='absolute w-full text-center' style='top:120px'>
  <div id='h' style='font-size:64px;font-weight:800;opacity:0'>活路を開く店も</div>
</div>
<div id='chips' class='absolute flex justify-center gap-6 w-full' style='top:330px'></div>
<div id='mj' class='manju absolute' style='left:590px;top:520px;width:100px;height:76px;opacity:0'></div>
""", f"""
var L = ['インバウンド', 'OEM製造', 'ネット通販', 'ネオ和菓子'], ch = $('chips'), cs = [];
L.forEach(function (s) {{
  var d = document.createElement('div');
  d.className = 'g px-7 py-5 font-bold text-white';
  d.style.cssText += 'font-size:36px;border-radius:999px;background:{RED};box-shadow:0 10px 24px rgba(120,40,20,.25)';
  d.textContent = s; ch.appendChild(d); cs.push(d);
}});
function render(frame, total, fps) {{
  var t = frame / fps;
  $('glow').style.opacity = eout(P(t, 0.2, 2.5));
  $('h').style.opacity = P(t, 0.2, 0.7);
  cs.forEach(function (d, i) {{ var p = P(t, 0.9 + i * 0.45, 1.5 + i * 0.45); d.style.opacity = p; d.style.transform = 'translateY(' + (80 * (1 - eback(p))) + 'px)'; }});
  var m = P(t, 3.0, 3.6); $('mj').style.opacity = m; $('mj').style.transform = 'translateY(' + (Math.sin(t * 3) * 6) + 'px) scale(' + eback(m) + ')';
}}""")

script = {
    "$mulmocast": {"version": "1.1"},
    "canvasSize": {"width": 1280, "height": 720},
    "title": "和菓子店の倒産、過去最多ペース",
    "description": "帝国データバンク（2026-10-03）の記事を30秒で紹介するテスト。映像は html_tailwind のみ。",
    "lang": "ja",
    "speechParams": {"speakers": {"Anchor": {
        "voiceId": "Kore", "isDefault": True, "provider": "gemini", "model": "gemini-3.1-flash-tts-preview",
        "speechOptions": {"instruction": "落ち着いた夕方のニュースのアナウンサー。明瞭で、やや速めのテンポ。"}}}},
    "audioParams": {"bgm": {"kind": "path", "path": str(REPO / "samples/opus55-motion/ideas-news/assets/news-bed.mp3")},
                    "bgmVolume": 0.2, "audioVolume": 1.0, "padding": 0.3, "introPadding": 0.4,
                    "closingPadding": 0.6, "outroPadding": 0.8},
    "beats": [b1, b2, b3, b4, b5],
}
(HERE / "wagashi-news.json").write_text(json.dumps(script, ensure_ascii=False, indent=1))
print("wrote", HERE / "wagashi-news.json")
