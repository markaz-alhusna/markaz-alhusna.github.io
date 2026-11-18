import json, os, base64, urllib.request, urllib.error
cfg = json.load(open('images/gen/run.json'))
key = os.environ.get('OPENROUTER_API_KEY', '')
print('ключ есть' if key else 'КЛЮЧА НЕТ')
os.makedirs('images/gen/out', exist_ok=True)
# баланс
try:
    r = urllib.request.urlopen(urllib.request.Request('https://openrouter.ai/api/v1/credits', headers={'Authorization': 'Bearer ' + key}), timeout=30)
    print('баланс:', r.read().decode()[:300])
except Exception as e:
    print('баланс: ошибка', e)
for job in cfg['jobs']:
    for model in job.get('models', [cfg.get('model')]):
        body = {'model': model, 'modalities': ['image', 'text'],
                'messages': [{'role': 'user', 'content': job['prompt']}]}
        req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                     headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        name = job['name'] + '__' + model.replace('/', '_')
        try:
            res = json.load(urllib.request.urlopen(req, timeout=240))
        except urllib.error.HTTPError as e:
            print(name, 'HTTP', e.code, e.read().decode()[:500]); continue
        except Exception as e:
            print(name, 'ошибка', e); continue
        msg = (res.get('choices') or [{}])[0].get('message', {})
        imgs = msg.get('images') or []
        print(name, 'картинок:', len(imgs), '| стоимость:', json.dumps(res.get('usage', {}))[:200], '| текст:', (msg.get('content') or '')[:150])
        for i, im in enumerate(imgs):
            url = im.get('image_url', {}).get('url', '')
            if url.startswith('data:'):
                ext = 'png' if 'png' in url[:30] else 'jpg'
                open(f'images/gen/out/{name}_{i+1}.{ext}', 'wb').write(base64.b64decode(url.split(',', 1)[1]))
