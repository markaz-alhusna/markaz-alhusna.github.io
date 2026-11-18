#!/usr/bin/env bash
cd voice/ustaza/stt
for f in bukvy razdel-6 razdel-15; do
  curl -sS -X POST https://api.elevenlabs.io/v1/speech-to-text -H "xi-api-key: $ELEVENLABS_API_KEY" -F model_id=scribe_v1 -F language_code=ara -F "file=@$f.mp3" -F timestamps_granularity=word > $f.json
  echo "$f: $(python3 -c "import json;d=json.load(open('$f.json'));print(d.get('text') or d)" )"
done
