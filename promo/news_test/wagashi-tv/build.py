"""wagashi v2 — the same article and narration as wagashi v1, dressed as a TV news segment.

B-roll stills come from Nano Banana 2 (gemini-3.1-flash-image-preview) via assets.json:
  mulmo images -g -o gen assets.json  ->  copy gen/assets/images/*.png to assets/
Everything on top (channel bug, lower thirds, numbers) is html_tailwind animation.
"""
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
// Ken Burns on the B-roll still, then the lower third wipes in
function broll(t, D, z0, z1, x0, x1) {
  var k = P(t, 0, D);
  $('bg').style.transform = 'translateX(' + (x0 + (x1 - x0) * k) + 'px) scale(' + (z0 + (z1 - z0) * k) + ')';
  var a = eout(P(t, 0.25, 0.7)), b = eout(P(t, 0.45, 0.95));
  $('ltag').style.clipPath = 'inset(0 ' + (100 - a * 100) + '% 0 0)';
  $('lbar').style.clipPath = 'inset(0 ' + (100 - b * 100) + '% 0 0)';
  $('ltxt').style.opacity = 1;
}
"""
RED, NAVY = "#d7141a", "#0d1b33"
STYLE = ("<style>.g{font-family:'Hiragino Sans','Helvetica Neue',sans-serif}"
         ".panel{background:rgba(10,20,40,.72);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.18);border-radius:14px}</style>")


def chrome(img, headline, tag, inner=""):
    return (f"{STYLE}<div class='g relative overflow-hidden' style='width:1280px;height:720px;background:#000;color:#fff'>"
            f"<img id='bg' src='assets/{img}.png' class='absolute' style='left:0;top:0;width:1280px;height:720px;object-fit:cover;transform-origin:50% 50%'>"
            "<div class='absolute inset-0' style='background:linear-gradient(180deg,rgba(0,0,0,.35),transparent 22%,transparent 60%,rgba(0,0,0,.55))'></div>"
            f"{inner}"
            # channel bug
            f"<div class='absolute flex items-center' style='left:36px;top:28px'><div style='width:14px;height:40px;background:{RED}'></div>"
            "<div class='ml-3 font-black' style='font-size:30px;letter-spacing:.06em;text-shadow:0 2px 8px rgba(0,0,0,.6)'>MULMO NEWS</div></div>"
            "<div class='absolute text-right' style='right:32px;top:30px;font-size:17px;opacity:.9;text-shadow:0 1px 4px #000'>※映像はAI生成のイメージです</div>"
            # lower third
            f"<div class='absolute' style='left:60px;bottom:64px'>"
            f"<div id='ltag' class='inline-block px-4 py-1 font-bold' style='font-size:24px;background:{RED};clip-path:inset(0 100% 0 0)'>{tag}</div>"
            f"<div id='lbar' style='margin-top:4px;padding:12px 30px 14px;background:linear-gradient(90deg,#fff 0,#fff 92%,rgba(255,255,255,.85));clip-path:inset(0 100% 0 0);box-shadow:0 8px 24px rgba(0,0,0,.35)'>"
            f"<div id='ltxt' class='font-black' style='font-size:50px;line-height:1.1;color:{NAVY};opacity:0'>{headline}</div></div></div>"
            f"<div class='absolute' style='left:0;right:0;bottom:0;height:34px;background:{NAVY};display:flex;align-items:center;padding:0 24px;font-size:17px'>"
            "<span class='font-bold mr-4' style='color:#ffcc33'>出典</span>帝国データバンク（2026年10月3日）</div>"
            "</div>")


def beat(bid, text, img, headline, tag, inner, script):
    return {"id": bid, "text": text,
            "image": {"type": "html_tailwind", "html": chrome(img, headline, tag, inner), "script": HELPERS + script, "animation": {"fps": 30}}}


b1 = beat("open", "和菓子店の倒産が、過去最多のペースです。", "img-closed-shop", "和菓子店の倒産 過去最多ペース", "経済", "", """
function render(frame, total, fps) { var t = frame / fps; broll(t, total / fps, 1.12, 1.0, 30, -10); }""")

b2 = beat("count", "帝国データバンクによると、今年1月から9月で22件。", "img-wagashi-tray", "1〜9月の倒産 22件", "経済", """
<div id='pn' class='panel absolute' style='right:60px;top:110px;width:380px;padding:22px 28px;opacity:0'>
  <div style='font-size:22px;opacity:.85'>和菓子店の倒産（1〜9月）</div>
  <div class='flex items-end'><div id='n' class='font-black' style='font-size:150px;line-height:1;color:#fff'>0</div><div class='font-bold' style='font-size:50px;margin:0 0 18px 10px'>件</div></div>
  <div id='rec' class='inline-block px-3 py-1 font-bold' style='font-size:24px;background:#d7141a;opacity:0'>過去最多ペース</div>
</div>""", """
function render(frame, total, fps) {
  var t = frame / fps; broll(t, total / fps, 1.0, 1.1, 0, -30);
  var p = P(t, 0.5, 0.9); $('pn').style.opacity = p; $('pn').style.transform = 'translateX(' + (40 * (1 - eout(p))) + 'px)';
  $('n').textContent = Math.round(22 * eout(P(t, 0.8, 2.4)));
  var r = P(t, 2.5, 2.8); $('rec').style.opacity = r; $('rec').style.transform = 'scale(' + (1.3 - 0.3 * eback(r)) + ')';
}""")

b3 = beat("shinise", "2020年以降の138件では、業歴100年以上の老舗が24件。50年以上なら半数です。", "img-old-sign", "業歴100年以上の老舗も 24件", "経済", """
<div id='pn' class='panel absolute' style='left:60px;top:100px;width:600px;padding:20px 24px;opacity:0'>
  <div style='font-size:22px;opacity:.85'>2020年以降の倒産 138件のうち</div>
  <div id='grid' class='relative mt-3' style='height:228px'></div>
  <div class='flex gap-5 mt-2' style='font-size:20px;white-space:nowrap'>
    <div id='l1' style='opacity:0'><span style='color:#ff4d4d'>●</span> 業歴100年以上 <b style='font-size:26px'>24件</b>（17.4%）</div>
    <div id='l2' style='opacity:0'><span style='color:#f0b429'>●</span> 50年以上 <b style='font-size:26px'>半数</b></div>
  </div>
</div>""", """
var g = $('grid'), dots = [];
for (var i = 0; i < 138; i++) {
  var d = document.createElement('div');
  d.style.cssText = 'position:absolute;width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,.35);left:' + ((i % 23) * 24) + 'px;top:' + (Math.floor(i / 23) * 38) + 'px';
  g.appendChild(d); dots.push(d);
}
function render(frame, total, fps) {
  var t = frame / fps; broll(t, total / fps, 1.15, 1.02, -20, 20);
  $('pn').style.opacity = P(t, 0.4, 0.8);
  for (var i = 0; i < 138; i++) {
    var red = i < 24 && t > 1.4 + i * 0.03, gold = i < 69 && t > 3.8 + (i - 24) * 0.02;
    dots[i].style.background = red ? '#ff4d4d' : (gold ? '#f0b429' : 'rgba(255,255,255,.35)');
    dots[i].style.transform = 'scale(' + (red || gold ? 1.15 : 1) + ')';
  }
  $('l1').style.opacity = P(t, 1.5, 1.9); $('l2').style.opacity = P(t, 3.9, 4.3);
}""")

b4 = beat("pressure", "原材料高に、職人の高齢化、技術の継承。値上げしにくいことも重荷です。", "img-craftsman", "原材料高・職人の高齢化が直撃", "経済", """
<div class='absolute' style='right:60px;top:110px;width:400px'>
  <div class='it panel' style='padding:14px 22px;font-size:32px;font-weight:800;margin-bottom:12px;opacity:0'><span style='color:#ff4d4d'>▶</span> 原材料高</div>
  <div class='it panel' style='padding:14px 22px;font-size:32px;font-weight:800;margin-bottom:12px;opacity:0'><span style='color:#ff4d4d'>▶</span> 職人の高齢化</div>
  <div class='it panel' style='padding:14px 22px;font-size:32px;font-weight:800;margin-bottom:12px;opacity:0'><span style='color:#ff4d4d'>▶</span> 技術の継承</div>
  <div class='it panel' style='padding:14px 22px;font-size:32px;font-weight:800;opacity:0'><span style='color:#ff4d4d'>▶</span> 値上げへの抵抗感</div>
</div>""", """
function render(frame, total, fps) {
  var t = frame / fps; broll(t, total / fps, 1.0, 1.14, 0, 40);
  document.querySelectorAll('.it').forEach(function (d, i) { var p = P(t, 0.5 + i * 0.9, 0.9 + i * 0.9); d.style.opacity = p; d.style.transform = 'translateX(' + (60 * (1 - eout(p))) + 'px)'; });
}""")

b5 = beat("hope", "一方、インバウンドや通販、「ネオ和菓子」で伸びる店もあります。", "img-tourists", "インバウンドや通販で活路も", "経済", """
<div class='absolute flex gap-4' style='left:60px;top:110px'>
  <div class='it panel' style='padding:12px 22px;font-size:30px;font-weight:800;opacity:0'>インバウンド</div>
  <div class='it panel' style='padding:12px 22px;font-size:30px;font-weight:800;opacity:0'>OEM製造</div>
  <div class='it panel' style='padding:12px 22px;font-size:30px;font-weight:800;opacity:0'>ネット通販</div>
  <div class='it panel' style='padding:12px 22px;font-size:30px;font-weight:800;opacity:0'>ネオ和菓子</div>
</div>""", """
function render(frame, total, fps) {
  var t = frame / fps; broll(t, total / fps, 1.12, 1.0, -30, 10);
  document.querySelectorAll('.it').forEach(function (d, i) { var p = P(t, 0.6 + i * 0.4, 1.0 + i * 0.4); d.style.opacity = p; d.style.transform = 'translateY(' + (30 * (1 - eback(p))) + 'px)'; });
}""")

deck = {
    "$mulmocast": {"version": "1.1"},
    "canvasSize": {"width": 1280, "height": 720},
    "title": "和菓子店の倒産、過去最多ペース（TVニュース風）",
    "description": "wagashi v1 と同じ記事・ナレーションを、Nano Banana 2 の B-roll とテレビ風テロップで見せる版。",
    "lang": "ja",
    "speechParams": {"speakers": {"Anchor": {
        "voiceId": "Kore", "isDefault": True, "provider": "gemini", "model": "gemini-3.1-flash-tts-preview",
        "speechOptions": {"instruction": "落ち着いた夕方のニュースのアナウンサー。明瞭で、やや速めのテンポ。"}}}},
    "audioParams": {"bgm": {"kind": "path", "path": str(REPO / "samples/opus55-motion/ideas-news/assets/news-bed.mp3")},
                    "bgmVolume": 0.2, "audioVolume": 1.0, "padding": 0.3, "introPadding": 0.4,
                    "closingPadding": 0.6, "outroPadding": 0.8},
    "movieParams": {"transition": {"type": "fade", "duration": 0.3}},
    "beats": [b1, b2, b3, b4, b5],
}
(HERE / "wagashi-tv.json").write_text(json.dumps(deck, ensure_ascii=False, indent=1))
print("wrote", HERE / "wagashi-tv.json")
