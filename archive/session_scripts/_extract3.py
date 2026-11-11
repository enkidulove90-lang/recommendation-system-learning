# -*- coding: utf-8 -*-
import json, io
p = r"C:/Users/xu.yan1/.workbuddy/projects/c-Users-xu.yan1-papers-recommendation-system-learning/e5a041fe-b710-4c95-b524-1670acb9fbe9.jsonl"
rows=[json.loads(l) for l in io.open(p,encoding='utf-8') if l.strip()]
n=0
for o in rows:
    if o.get('type')=='message' and o.get('role')=='user':
        c=o.get('content') or []
        if isinstance(c,list):
            kinds=[b.get('type') for b in c if isinstance(b,dict)]
            if n<6:
                print('---', kinds)
                print(json.dumps(c, ensure_ascii=False)[:500])
            n+=1
print('user msgs', n)
