#!/bin/sh
# Fit the ElevenLabs take (bgm-request.json) to the film: skip its ~1.0 s silent head and keep 96.0 s.
# mulmocast plays audioParams.bgm from 0 s with no offset option, so the silent head has to be cut here.
# usage: sh fit.sh <take.mp3> <out.mp3>
set -e
ffmpeg -v error -y -i "$1" -af "atrim=start=1.0:duration=96.0,asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st=94.5:d=1.5" -ar 44100 -ac 2 -b:a 192k "$2"
