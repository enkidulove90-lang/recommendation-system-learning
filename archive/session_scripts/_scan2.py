# -*- coding: utf-8 -*-
import json, io
p = r"C:/Users/xu.yan1/.workbuddy/projects/c-Users-xu.yan1-papers-recommendation-system-learning/e5a041fe-b710-4c95-b524-1670acb9fbe9.jsonl"
cnt=0
with io.open(p, encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        o=json.loads(line)
        if o.get('type')=='function_call':
            print('KEYS', list(o.keys()))
            print(json.dumps(o, ensure_ascii=False)[:1200])
            cnt+=1
            if cnt>=2: break
