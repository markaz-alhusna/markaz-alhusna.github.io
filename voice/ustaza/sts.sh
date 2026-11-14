#!/usr/bin/env bash
# Перевод записей устазы в голос платформы (ElevenLabs Speech-to-Speech).
# Вход: voice/ustaza/in/*.mp3 (очищенные куски по 6 слогов, паузы — чистая тишина). Выход: voice/ustaza/out/.
set -euo pipefail
cd voice/ustaza
CFG=run.json
MODE=$(python3 -c "import json;print(json.load(open('$CFG'))['mode'])")
NAME=$(python3 -c "import json;print(json.load(open('$CFG'))['voice'])")
ST=$(python3 -c "import json;print(json.load(open('$CFG'))['stability'])")
SIM=$(python3 -c "import json;print(json.load(open('$CFG'))['similarity'])")
VIDCFG=$(python3 -c "import json;print(json.load(open('$CFG')).get('voice_id',''))")
for id in gMB389pj77Qe5nErWNjd GN4wbsbejSnGSa1AzjH5; do echo "config voice $id:"; curl -sS https://api.elevenlabs.io/v1/voices/$id -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -c "import json,sys;d=json.load(sys.stdin);print(' ',d.get('name'),d.get('category'),str(d.get('detail',''))[:200])"; done
curl -sS https://api.elevenlabs.io/v1/voices -H "xi-api-key: $ELEVENLABS_API_KEY" > /tmp/voices.json
python3 - "$NAME" "$VIDCFG" <<'PY' > /tmp/vid.txt
import json,sys
if sys.argv[2]: print(sys.argv[2]); sys.exit()
d=json.load(open('/tmp/voices.json'))
if 'voices' not in d: print('voices error:',str(d)[:300],file=sys.stderr); print(''); sys.exit()
v=d['voices']; name=sys.argv[1].lower()
for x in v: print('VOICE:',x['voice_id'],x['name'],x.get('category'),file=sys.stderr)
m=[x for x in v if x['name'].lower().startswith(name)] or [x for x in v if name in x['name'].lower()]
print(m[0]['voice_id'] if m else '')
PY
VID=$(cat /tmp/vid.txt); echo "voice id: $VID"; [ -n "$VID" ] || { echo "голос не найден"; exit 1; }
mkdir -p out
if [ "$MODE" = test ]; then FILES=$(python3 -c "import json;print(' '.join(json.load(open('$CFG'))['test_files']))"); else FILES=$(cd in && ls *.mp3); fi
for f in $FILES; do
  code=$(curl -sS -w '%{http_code}' -o "out/$f" -X POST "https://api.elevenlabs.io/v1/speech-to-speech/$VID?output_format=mp3_44100_192" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" -F "audio=@in/$f" -F model_id=eleven_multilingual_sts_v2 \
    -F "voice_settings={\"stability\":$ST,\"similarity_boost\":$SIM,\"style\":0,\"use_speaker_boost\":false}" -F remove_background_noise=false)
  echo "$f -> $code"; [ "$code" = 200 ] || { cat "out/$f"; rm -f "out/$f"; }
done
curl -sS https://api.elevenlabs.io/v1/user/subscription -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -c "import json,sys;d=json.load(sys.stdin);print('кредиты:',d.get('character_count'),'/',d.get('character_limit'))" || true
