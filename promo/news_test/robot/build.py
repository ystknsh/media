"""30-second reenactment-VTR style piece: 配膳ロボの「横取り」（J-CASTニュース, 2026-10-02). html_tailwind only; costs = TTS + BGM."""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
BGM = HERE / "assets" / "vtr-bed.mp3"

HELPERS = """
function clamp01(x) { return Math.max(0, Math.min(1, x)); }
function P(t, a, b) { return clamp01((t - a) / (b - a)); }
function eout(x) { return 1 - Math.pow(1 - x, 3); }
function einout(x) { return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
function eback(x) { var c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); }
function $(id) { return document.getElementById(id); }
// deterministic film grain: same frame -> same noise
var GC = $('grain').getContext('2d'), GI = GC.createImageData(320, 180);
function grain(frame) {
  var s = (frame * 9301 + 49297) % 233280;
  for (var i = 0; i < GI.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; var v = s / 233280 * 255; GI.data[i] = GI.data[i + 1] = GI.data[i + 2] = v; GI.data[i + 3] = 34; }
  GC.putImageData(GI, 0, 0);
}
function cam(t, scale, ox, oy) {   // handheld camera: slow drift + small shake
  var jx = Math.sin(t * 1.7) * 4 + Math.sin(t * 5.3) * 1.5, jy = Math.cos(t * 1.3) * 3 + Math.sin(t * 4.1) * 1.2;
  $('world').style.transformOrigin = ox + 'px ' + oy + 'px';
  $('world').style.transform = 'translate(' + jx + 'px,' + jy + 'px) scale(' + scale + ')';
}
// robot + plate + arm state
var ROBOT_Y = 300;
function robot(x, mood) {
  $('robot').style.left = x + 'px';
  $('eyes').textContent = mood === 'alert' ? '! !' : (mood === 'smile' ? '^ ^' : '• •');
  $('eyes').style.color = mood === 'alert' ? '#ff5252' : '#7fe3ff';
  $('screen').style.boxShadow = mood === 'alert' ? '0 0 30px 8px rgba(255,60,60,.8)' : 'none';
}
function plate(x, y) { $('plate').style.left = x + 'px'; $('plate').style.top = y + 'px'; }
var AL = 265, AA = 3;
function hand(len) { return [300 + len * Math.cos(AA * Math.PI / 180), 410 + len * Math.sin(AA * Math.PI / 180)]; }
function arm(len, ang) { $('arm').style.width = len + 'px'; $('arm').style.transform = 'rotate(' + ang + 'deg)'; }
function steam(t) {
  document.querySelectorAll('.puff').forEach(function (p, i) {
    var ph = (t * 0.5 + i * 0.37) % 1; p.style.opacity = Math.sin(ph * Math.PI) * 0.55;
    p.style.transform = 'translate(' + (Math.sin(ph * 6 + i) * 10) + 'px,' + (-ph * 90) + 'px) scale(' + (0.6 + ph) + ')';
  });
}
"""

STYLE = """<style>
.g{font-family:'Hiragino Sans','Helvetica Neue',sans-serif}
.tel{font-family:'Hiragino Sans',sans-serif;font-weight:900;color:#fff;-webkit-text-stroke:12px #111;paint-order:stroke fill;letter-spacing:.02em}
.tel.y{color:#ffe14d}
.tel.r{color:#fff;-webkit-text-stroke:12px #c4161c}
.puff{position:absolute;width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,.9);filter:blur(6px)}
.meat{background:repeating-linear-gradient(115deg,#d9435a 0 9px,#f6c9cf 9px 12px,#c9304a 12px 22px,#f3b8c0 22px 25px)}
</style>"""


def person(x, color, pid):
    return (f"<div id='{pid}' class='absolute' style='left:{x}px;top:300px;width:140px;height:200px'>"
            f"<div style='position:absolute;left:38px;top:0;width:64px;height:64px;border-radius:50%;background:#e8c4a0'></div>"
            f"<div style='position:absolute;left:38px;top:-4px;width:64px;height:30px;border-radius:32px 32px 6px 6px;background:#3b2a20'></div>"
            f"<div style='position:absolute;left:10px;top:70px;width:120px;height:140px;border-radius:40px 40px 10px 10px;background:{color}'></div>"
            "</div>")


def table(cx):
    return (f"<div class='absolute' style='left:{cx - 170}px;top:470px;width:340px;height:20px;background:#6b4226;border-radius:4px;box-shadow:0 6px 0 #4a2d19'></div>"
            f"<div class='absolute' style='left:{cx - 150}px;top:490px;width:16px;height:80px;background:#4a2d19'></div>"
            f"<div class='absolute' style='left:{cx + 134}px;top:490px;width:16px;height:80px;background:#4a2d19'></div>"
            f"<div class='absolute' style='left:{cx - 55}px;top:430px;width:110px;height:42px;border-radius:0 0 50px 50px;background:linear-gradient(#9aa3ab,#5d656c)'></div>"
            + "".join(f"<div class='puff' style='left:{cx - 30 + k * 18}px;top:400px'></div>" for k in range(4)))


ROBOT = """
<div id='robot' class='absolute' style='left:-260px;top:300px;width:170px;height:340px'>
  <div style='position:absolute;left:18px;top:-18px;width:0;height:0;border-left:22px solid transparent;border-right:22px solid transparent;border-bottom:34px solid #f2f2f2'></div>
  <div style='position:absolute;right:18px;top:-18px;width:0;height:0;border-left:22px solid transparent;border-right:22px solid transparent;border-bottom:34px solid #f2f2f2'></div>
  <div style='position:absolute;left:0;top:6px;width:170px;height:104px;border-radius:44px;background:#f2f2f2;box-shadow:inset -8px -8px 0 #d6d6d6'>
    <div id='screen' style='position:absolute;left:18px;top:16px;width:134px;height:70px;border-radius:30px;background:#1d2228;display:flex;align-items:center;justify-content:center'>
      <div id='eyes' class='g' style='font-size:40px;font-weight:900;color:#7fe3ff;letter-spacing:.15em'>^ ^</div></div></div>
  <div style='position:absolute;left:72px;top:110px;width:26px;height:200px;background:#cfcfcf'></div>
  <div style='position:absolute;left:0;top:140px;width:170px;height:14px;border-radius:7px;background:#e6e6e6'></div>
  <div style='position:absolute;left:0;top:210px;width:170px;height:14px;border-radius:7px;background:#e6e6e6'></div>
  <div style='position:absolute;left:0;top:280px;width:170px;height:14px;border-radius:7px;background:#e6e6e6'></div>
  <div style='position:absolute;left:10px;top:300px;width:150px;height:40px;border-radius:20px;background:#3a3f45'></div>
</div>"""

PLATE = "<div id='plate' class='absolute' style='left:-200px;top:0;width:120px;height:26px;border-radius:50%;background:#f7f3ea;box-shadow:0 3px 0 #bbb'><div class='meat' style='position:absolute;left:14px;top:-10px;width:92px;height:22px;border-radius:40%'></div></div>"
ARM = "<div id='arm' class='absolute' style='left:300px;top:395px;height:30px;width:0;border-radius:15px;background:#2f4a6d;transform-origin:0 50%'><div style='position:absolute;right:-16px;top:-3px;width:36px;height:36px;border-radius:50%;background:#e8c4a0'></div></div>"


def scene(overlay="", label="※再現VTR"):
    world = ("<div id='world' class='absolute inset-0' style='filter:var(--f,saturate(.72) contrast(1.06) sepia(.18))'>"
             "<div class='absolute inset-0' style='background:linear-gradient(#5a3b28,#8a5a3a 55%,#3a2619 56%,#2a1b12)'></div>"
             "<div class='absolute' style='left:0;right:0;top:60px;height:200px;background:repeating-linear-gradient(90deg,#6e4a32 0 120px,#5e3e2a 120px 124px)'></div>"
             "<div class='absolute' style='left:520px;top:90px;width:240px;height:150px;background:#f0d9a8;box-shadow:inset 0 0 40px #b07a3a;opacity:.8'></div>"
             + person(260, "#4b5d7a", "pA") + table(330) + person(930, "#7a4b4b", "pB") + table(1000)
             + ARM + ROBOT + PLATE +
             "<div id='qm' class='tel absolute' style='left:1010px;top:200px;font-size:90px;opacity:0'>？</div>"
             "<div id='ring' class='absolute' style='opacity:0'></div>"
             "</div>")
    return (STYLE + "<div class='relative overflow-hidden' style='width:1280px;height:720px;background:#111'>"
            + world +
            "<canvas id='grain' width='320' height='180' class='absolute inset-0' style='width:1280px;height:720px;mix-blend-mode:overlay'></canvas>"
            "<div class='absolute inset-0' style='background:radial-gradient(ellipse at center,transparent 55%,rgba(0,0,0,.6))'></div>"
            + overlay +
            f"<div class='tel absolute' style='right:28px;top:20px;font-size:26px;-webkit-text-stroke:6px #111'>{label}</div>"
            "</div>")


def beat(bid, text, overlay, script, label="※再現VTR"):
    return {"id": bid, "text": text,
            "image": {"type": "html_tailwind", "html": scene(overlay, label), "script": HELPERS + script, "animation": {"fps": 30}}}


# 1. establishing shot
b1 = beat("open", "2026年9月。とある、しゃぶしゃぶ店。",
          "<div id='date' class='tel absolute' style='left:60px;top:70px;font-size:44px;opacity:0'>2026年9月</div>"
          "<div id='place' class='tel absolute' style='left:60px;top:130px;font-size:56px;opacity:0'>とある しゃぶしゃぶ店</div>", """
function render(frame, total, fps) {
  var t = frame / fps; grain(frame); steam(t);
  cam(t, 1.3 * (1 + 0.06 * P(t, 0, total / fps)), 640, 560);
  robot(-260, 'smile'); plate(-200, 0); arm(0, 0);
  var a = P(t, 0.4, 0.9), b = P(t, 1.0, 1.5);
  $('date').style.opacity = a; $('date').style.transform = 'translateX(' + (-40 * (1 - eout(a))) + 'px)';
  $('place').style.opacity = b; $('place').style.transform = 'translateX(' + (-40 * (1 - eout(b))) + 'px)';
}""")

# 2. robot approaches with premium meat
b2 = beat("approach", "高級コースの肉を、ネコ型ロボットが運んでくる。……はずだった。",
          "<div id='t1' class='tel y absolute' style='left:0;right:0;bottom:60px;text-align:center;font-size:64px;opacity:0'>高価格帯コースの肉を運ぶ配膳ロボ</div>"
          "<div id='t2' class='tel r absolute' style='left:0;right:0;bottom:60px;text-align:center;font-size:72px;opacity:0'>……はずだった</div>", """
function render(frame, total, fps) {
  var t = frame / fps, D = total / fps; grain(frame); steam(t);
  cam(t, 1.3, 640, 560);
  var x = -260 + 740 * einout(P(t, 0.2, D - 1.6));
  robot(x, 'smile'); plate(x + 25, ROBOT_Y + 114); arm(0, 0);
  $('pB').style.transform = 'translateY(' + (Math.abs(Math.sin(t * 4)) * -6) + 'px)';
  $('t1').style.opacity = P(t, 0.5, 0.9) * (1 - P(t, D - 1.7, D - 1.5));
  var s = P(t, D - 1.5, D - 1.2); $('t2').style.opacity = s; $('t2').style.transform = 'scale(' + (1.4 - 0.4 * eout(s)) + ')';
}""")

# 3. the grab, then freeze-frame
b3 = beat("grab", "その途中、隣の客の手が伸び、肉はそのまま別の席へ。",
          "<svg class='absolute inset-0' width='1280' height='720'><ellipse id='circ' cx='640' cy='380' rx='170' ry='110' fill='none' stroke='#e11' stroke-width='10' stroke-dasharray='1200' stroke-dashoffset='1200' opacity='0'/></svg>"
          "<div id='eh' class='tel y absolute' style='left:0;right:0;bottom:50px;text-align:center;font-size:110px;opacity:0'>えっ……!?</div>", """
var PX = 505, PY = 414, F = 1.8;                  // freeze while the hand is carrying the plate away
function grabAt(t) {
  var reach = P(t, 0.3, 1.0), back = P(t, 1.3, 2.4);
  var len = AL * eout(reach) * (1 - 0.75 * eout(back)), h = hand(len);
  var pl = t < 1.0 ? [PX, PY] : [h[0] - 60, h[1] - 8 + 40 * eout(back)];
  return { len: len, h: h, pl: pl };
}
var FZ = grabAt(F);
$('circ').setAttribute('cx', FZ.h[0]); $('circ').setAttribute('cy', FZ.h[1]);
function render(frame, total, fps) {
  var t = frame / fps; grain(frame);
  var tt = Math.min(t, F), g = grabAt(tt);
  steam(tt); arm(g.len, AA); plate(g.pl[0], g.pl[1]); robot(480, 'smile');
  var f = P(t, F, F + 0.5);
  $('world').style.setProperty('--f', t >= F ? 'grayscale(1) contrast(1.15)' : 'saturate(.72) contrast(1.06) sepia(.18)');
  cam(tt, 1.3 + 0.6 * eout(f), FZ.h[0], FZ.h[1]);
  var c = P(t, F + 0.2, F + 0.8); $('circ').setAttribute('opacity', c > 0 ? 1 : 0); $('circ').setAttribute('stroke-dashoffset', 1200 * (1 - eout(c)));
  var e = P(t, F + 0.5, F + 0.8); $('eh').style.opacity = e; $('eh').style.transform = 'scale(' + (1.5 - 0.5 * eback(e)) + ')';
}""")

# 4. social media reaction (abstract cards, no real posts)
b4 = beat("sns", "SNSには同様の投稿が相次ぎ、意図的な横取りを指摘する声も。",
          "<div id='dim' class='absolute inset-0' style='background:rgba(10,10,14,.65);opacity:0'></div>"
          "<div id='cards' class='absolute inset-0'></div>"
          "<div id='tz' class='tel r absolute' style='left:0;right:0;bottom:60px;text-align:center;font-size:80px;opacity:0'>“横取り”の指摘も</div>", """
var POS = [[90,90,-4],[420,60,3],[760,100,-2],[200,300,2],[560,280,-3],[900,320,4],[60,470,-2],[980,520,-4]];
var cards = POS.map(function (p) {
  var d = document.createElement('div'); d.className = 'absolute';
  d.style.cssText = 'left:' + p[0] + 'px;top:' + p[1] + 'px;width:300px;height:120px;border-radius:16px;background:#fff;box-shadow:0 12px 30px rgba(0,0,0,.4);padding:16px;display:flex;gap:14px';
  d.innerHTML = "<div style='width:46px;height:46px;border-radius:50%;background:#c9ced6;flex:none'></div><div style='flex:1'><div style='height:12px;width:40%;background:#9aa1ab;border-radius:6px'></div><div style='height:12px;margin-top:14px;background:#d5d9df;border-radius:6px'></div><div style='height:12px;margin-top:10px;width:80%;background:#d5d9df;border-radius:6px'></div></div>";
  $('cards').appendChild(d); return d;
});
function render(frame, total, fps) {
  var t = frame / fps; grain(frame); steam(t);
  cam(t, 1.3, 640, 560); robot(480, 'smile'); plate(306, 452); arm(66, AA);
  $('dim').style.opacity = P(t, 0, 0.4);
  cards.forEach(function (d, i) { var p = P(t, 0.3 + i * 0.28, 0.6 + i * 0.28); d.style.opacity = p; d.style.transform = 'rotate(' + POS[i][2] + 'deg) scale(' + eback(p) + ')'; });
  var z = P(t, 2.8, 3.1); $('tz').style.opacity = z; $('tz').style.transform = 'scale(' + (1.4 - 0.4 * eout(z)) + ')';
}""", label="※イメージ")

# 5. company response: voice alert, rollout to all stores
b5 = beat("response", "運営元は謝罪。ほかの客の段の商品を取ろうとすると、ロボットが音声で知らせる機能を、全店に導入するとしています。",
          "<div id='bub' class='g absolute' style='left:640px;top:170px;padding:18px 26px;border-radius:24px;background:#fff;border:5px solid #c4161c;font-size:40px;font-weight:900;color:#c4161c;opacity:0'>ピピッ！ 音声でお知らせ</div>"
          "<div id='panel' class='g absolute' style='right:40px;top:300px;width:470px;padding:22px 26px;border-radius:18px;background:rgba(255,255,255,.95);opacity:0'>"
          "<div style='font-size:24px;font-weight:900;color:#c4161c'>運営元（すかいらーくHD）の対策</div>"
          "<div class='it' style='font-size:26px;font-weight:700;margin-top:10px;opacity:0'>・利用手順の説明を充実</div>"
          "<div class='it' style='font-size:26px;font-weight:700;margin-top:6px;opacity:0'>・英語・中国語のイラスト掲示</div>"
          "<div class='it' style='font-size:26px;font-weight:700;margin-top:6px;opacity:0'>・誤った段に手 → 音声通知</div>"
          "<div id='all' style='margin-top:14px;font-size:34px;font-weight:900;color:#fff;background:#c4161c;text-align:center;border-radius:10px;padding:6px 0;opacity:0'>全店に導入へ</div></div>"
          "<div class='g absolute' style='left:24px;bottom:16px;font-size:16px;color:#fff;opacity:.8'>出典: J-CASTニュース（2026年10月2日）</div>", """
function render(frame, total, fps) {
  var t = frame / fps; grain(frame); steam(t);
  cam(t, 1.3, 640, 560);
  var reach = P(t, 0.3, 1.0), back = P(t, 1.6, 2.1), alert = t > 1.0 && t < 2.8;
  var len = AL * 0.8 * eout(reach) * (1 - eout(back)); arm(len, AA);
  robot(480, alert ? 'alert' : 'smile'); plate(505, 414);
  var b = P(t, 1.0, 1.25) * (1 - P(t, 2.8, 3.1)); $('bub').style.opacity = b; $('bub').style.transform = 'scale(' + (0.6 + 0.4 * eback(P(t, 1.0, 1.3))) + ')';
  var p = P(t, 3.0, 3.4); $('panel').style.opacity = p; $('panel').style.transform = 'translateX(' + (60 * (1 - eout(p))) + 'px)';
  document.querySelectorAll('.it').forEach(function (d, i) { d.style.opacity = P(t, 3.5 + i * 0.5, 3.8 + i * 0.5); });
  var a = P(t, 5.3, 5.6); $('all').style.opacity = a; $('all').style.transform = 'scale(' + (1.3 - 0.3 * eback(a)) + ')';
}""", label="※イメージ")

deck = {
    "$mulmocast": {"version": "1.1"},
    "canvasSize": {"width": 1280, "height": 720},
    "title": "配膳ロボの「横取り」",
    "description": "J-CASTニュース（2026-10-02）の記事を再現VTR風に30秒で紹介するテスト。映像は html_tailwind のみ。",
    "lang": "ja",
    "speechParams": {"speakers": {"Narrator": {
        "voiceId": "Charon", "isDefault": True, "provider": "gemini", "model": "gemini-3.1-flash-tts-preview",
        "speechOptions": {"instruction": "テレビの再現VTRのナレーター風に、低めの声でドラマチックに、テンポよく読む。"}}}},
    "audioParams": {"bgm": {"kind": "path", "path": str(BGM)}, "bgmVolume": 0.22, "audioVolume": 1.0,
                    "padding": 0.3, "introPadding": 0.5, "closingPadding": 0.6, "outroPadding": 0.8},
    "beats": [b1, b2, b3, b4, b5],
}
if not BGM.exists():
    del deck["audioParams"]["bgm"]
    print("note: no BGM yet", file=sys.stderr)
(HERE / "robot-vtr.json").write_text(json.dumps(deck, ensure_ascii=False, indent=1))
print("wrote", HERE / "robot-vtr.json")
