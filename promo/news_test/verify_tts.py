"""Transcribe each beat's TTS clip and compare it with the script text. Exits 1 if any beat drifts.

usage: python3 verify_tts.py <studio.json>
Gemini 3.1 Flash TTS was seen adding sentences, repeating lines and reading the instruction aloud.
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

BIN = Path.home() / "mulmoclaude/.claude/skills/podcast-transcribe/bin/transcribe"
KANA_NUM = str.maketrans("０１２３４５６７８９", "0123456789")


def norm(s):
    s = re.sub(r"\[[^\]]*\]", "", s)  # ElevenLabs v4 inline delivery tags are not spoken
    s = s.translate(KANA_NUM)
    s = s.replace("二十", "2")  # the recogniser writes 22 as 二十 2
    return re.sub(r"[\s、。「」『』…・,.!?！？“”]", "", s)


studio = json.load(open(sys.argv[1]))
bad = checked = 0
for b, sb in zip(studio["beats"], studio["script"]["beats"]):
    text = sb.get("text", "")
    if not text:
        continue
    heard = subprocess.run([str(BIN), b["audioFile"], "ja-JP"], capture_output=True, text=True).stdout.strip().splitlines()[-1]
    a, h = norm(text), norm(heard)
    ratio = difflib.SequenceMatcher(None, a, h).ratio()
    extra = len(h) / max(len(a), 1)
    ok = ratio >= 0.8 and extra <= 1.2
    bad += not ok
    checked += 1
    print(f"{'OK ' if ok else 'NG '} ratio={ratio:.2f} len={extra:.2f} | {heard}")
if checked == 0:
    sys.exit("no narrated beats found")
sys.exit(1 if bad else 0)
