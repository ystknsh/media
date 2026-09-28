#!/bin/sh
# Fit the ElevenLabs take (bgm-request.json) to the film: skip its silent head and keep the film's length.
# mulmocast plays audioParams.bgm from 0 s with no offset option, so the silent head has to be cut here.
# usage: sh fit.sh <take.mp3> <out.mp3> <head seconds> <film seconds>   (film seconds = build.py's total)
set -e
FADE=$(python3 -c "print($4 - 1.5)")
ffmpeg -v error -y -i "$1" -af "atrim=start=$3:duration=$4,asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st=$FADE:d=1.5" -ar 44100 -ac 2 -b:a 192k "$2"
# used: sh fit.sh take.mp3 bgm.mp3 1.45 109.6
