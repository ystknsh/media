"""Derive the v3 decks from v2: same visuals, TTS switched to ElevenLabs eleven_v4."""
import json, pathlib
P = pathlib.Path(__file__).parent

def el(voice):
    return {"speakers": {"Narrator": {"provider": "elevenlabs", "model": "eleven_v4", "voiceId": voice, "isDefault": True}}}

# wagashi: news read, Hinata (calm young male, news / narration)
w = json.loads((P / "wagashi-tv/wagashi-tv.json").read_text())
w["title"] += "（ElevenLabs v4）"
w["speechParams"] = el("j210dv0vWm7fCknyQpbA")
w["audioParams"]["bgmVolume"] = 0.13
w["audioParams"]["audioVolume"] = 2.2  # Hinata comes out ~9 dB quieter than the Gemini voice; peaks leave ~8 dB
(P / "wagashi-tv/wagashi-v3.json").write_text(json.dumps(w, ensure_ascii=False, indent=1))

# robot: reenactment narrator, Otani (middle-aged male, narrative); a few v4 inline delivery tags
r = json.loads((P / "robot3d/robot-3d.json").read_text())
r["title"] += "（ElevenLabs v4）"
r["speechParams"] = el("3JDquces8E8bkmvbh6Bc")
tags = {
    "open": "[low, dramatic narrator voice] 2026年、9月。とある、しゃぶしゃぶ店。",
    "approach": "高級コースの肉を、ネコ型ロボットが運んでくる。[dramatic pause] ……はずだった。",
    "grab": "[tense] その途中、隣の客の手が伸び、肉はそのまま別の席へ。",
    "sns": "SNSには同様の投稿が相次ぎ、意図的な横取りを指摘する声も。",
    "response": "[calm, news anchor tone] 運営元は謝罪。ほかの客の段の商品を取ろうとすると、ロボットが音声で知らせる機能を、全店に導入するとしています。",
}
for b in r["beats"]:
    b["text"] = tags[b["id"]]
(P / "robot3d/robot-v3.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
print("ok")
