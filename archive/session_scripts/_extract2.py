# -*- coding: utf-8 -*-
import json, io, datetime
p = r"C:/Users/xu.yan1/.workbuddy/projects/c-Users-xu.yan1-papers-recommendation-system-learning/e5a041fe-b710-4c95-b524-1670acb9fbe9.jsonl"
rows=[json.loads(l) for l in io.open(p,encoding='utf-8') if l.strip()]
for o in rows:
    if o.get('type')=='message':
        c=o.get('content') or []
        if isinstance(c,list):
            for b in c:
                if isinstance(b,dict) and b.get('type')=='text':
                    t=b.get('text','').strip()
                    if t and not t.startswith('<'):
                        print(datetime.datetime.fromtimestamp(o['timestamp']/1000).strftime('%m-%d %H:%M'), '|', t[:80].replace('\n',' '))
