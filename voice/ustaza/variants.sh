#!/usr/bin/env bash
# Пробы настроек: voice/ustaza/variants.json — список {name,file,model,stability,similarity,style}
set -uo pipefail
cd voice/ustaza; mkdir -p out/var
VID=gMB389pj77Qe5nErWNjd
python3 -c "import json;[print(v['name'],v['file'],v['model'],v['stability'],v['similarity'],v.get('style',0)) for v in json.load(open('variants.json'))]" | while read n f mo st si sy; do
  code=$(curl -sS -w '%{http_code}' -o "out/var/$n.mp3" -X POST "https://api.elevenlabs.io/v1/speech-to-speech/$VID?output_format=mp3_44100_192" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" -F "audio=@in/$f" -F model_id=$mo \
    -F "voice_settings={\"stability\":$st,\"similarity_boost\":$si,\"style\":$sy,\"use_speaker_boost\":false}" -F remove_background_noise=false)
  echo "$n -> $code"; [ "$code" = 200 ] || { cat "out/var/$n.mp3"; rm -f "out/var/$n.mp3"; }
done
curl -sS https://api.elevenlabs.io/v1/user/subscription -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -c "import json,sys;d=json.load(sys.stdin);print('кредиты:',d.get('character_count'),'/',d.get('character_limit'))" || true
