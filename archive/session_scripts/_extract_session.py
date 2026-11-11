# -*- coding: utf-8 -*-
import json, io, datetime

p = r"C:/Users/xu.yan1/.workbuddy/projects/c-Users-xu.yan1-papers-recommendation-system-learning/e5a041fe-b710-4c95-b524-1670acb9fbe9.jsonl"
rows = []
with io.open(p, encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        o = json.loads(line)
        rows.append(o)

# 1) 找用户消息，定位小红书相关会话起点
users = []
for o in rows:
    if o.get('type') == 'message':
        c = o.get('content') or []
        if isinstance(c, list):
            txt = ''.join(b.get('text','') for b in c if isinstance(b,dict) and b.get('type')=='input_text')
            if txt.strip():
                users.append((o.get('timestamp'), txt.strip()[:90].replace('\n',' ')))
print('=== USER MESSAGES (%d) ===' % len(users))
for ts, t in users:
    print(datetime.datetime.fromtimestamp(ts/1000).strftime('%H:%M:%S'), '|', t)
