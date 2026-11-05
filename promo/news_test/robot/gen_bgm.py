"""Generate the reenactment-VTR bed with ElevenLabs Music. Reads ELEVENLABS_API_KEY from the repo .env without printing it."""
import json
import pathlib
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[4] / "mulmo-presentations"
key = next(l.split("=", 1)[1].strip().strip('"') for l in (REPO / ".env").read_text().splitlines()
           if l.startswith("ELEVENLABS_API_KEY="))
body = {
    "prompt": ("Instrumental background music for a Japanese TV variety-show reenactment segment (saigen VTR). "
               "Light comedic suspense: tiptoeing pizzicato strings, soft ticking percussion, a low bass pulse, "
               "a sudden dramatic stinger hit around 12 seconds, then curious, slightly tense mood, "
               "and a calmer, resolved news-like ending. No vocals. Sits under a narrator."),
    "music_length_ms": 42000,
    "model_id": "music_v1",
    "force_instrumental": True,
}
req = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",
                             data=json.dumps(body).encode(), method="POST",
                             headers={"xi-api-key": key, "Content-Type": "application/json"})
out = pathlib.Path(__file__).parent / "assets" / "vtr-bed-raw.mp3"
out.parent.mkdir(exist_ok=True)
with urllib.request.urlopen(req, timeout=300) as r:
    out.write_bytes(r.read())
print("wrote", out, out.stat().st_size, "bytes")
