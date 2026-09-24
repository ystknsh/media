import json, sys, urllib.request, os
key = next(l.split('=',1)[1].strip().strip('"') for l in open('.env') if l.startswith('ELEVENLABS_API_KEY='))
body = json.load(open(sys.argv[1]))
req = urllib.request.Request('https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        open(sys.argv[2], 'wb').write(r.read()); print('ok', r.status)
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read()[:800].decode(errors='replace'))
