#!/bin/sh
# Splice the two ElevenLabs takes into bgm.mp3 (30.5 s), cut to the beats in build.py:
#   0.0-11.5   2025 part (bgm-2025.json), skipping its ~0.95 s silent head; hard stop as the CRT switches off
#   11.5-12.4  silence (the "cut" beat)
#   12.4-30.5  2026 part (bgm-2026.json), its own fade-out lands on the closing title
# mulmocast plays audioParams.bgm from 0 s with no offset option, so the silent head has to be cut here.
# usage: sh splice.sh <2025 take.mp3> <2026 take.mp3> <out.mp3>
set -e
ffmpeg -v error -y -i "$1" -i "$2" -filter_complex "\
[0:a]atrim=start=0.95:duration=11.5,asetpts=PTS-STARTPTS,afade=t=out:st=11.35:d=0.15[a];\
aevalsrc=0:c=stereo:s=44100:d=0.9[s];\
[1:a]atrim=start=0:duration=18.1,asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st=17.4:d=0.7[b];\
[a][s][b]concat=n=3:v=0:a=1[out]" -map "[out]" -ar 44100 -ac 2 -b:a 192k "$3"
