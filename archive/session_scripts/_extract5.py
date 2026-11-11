# -*- coding: utf-8 -*-
import json, io, datetime, re
p = r"C:/Users/xu.yan1/.workbuddy/projects/c-Users-xu.yan1-papers-recommendation-system-learning/e5a041fe-b710-4c95-b524-1670acb9fbe9.jsonl"
rows=[json.loads(l) for l in io.open(p,encoding='utf-8') if l.strip()]

def uq(o):
    c=o.get('content') or []
    if not isinstance(c,list): return ''
    t=''.join(b.get('text','') for b in c if isinstance(b,dict))
    m=re.search(r'<user_query>(.*?)</user_query>', t, re.S)
    return m.group(1).strip() if m else ''

start=None
for i,o in enumerate(rows):
    if o.get('type')=='message' and o.get('role')=='user':
        q=uq(o)
        if 'Sequence-level Adaptive Gradient Evolution' in q or 'DiffGRM' in q:
            start=i; break
print('start idx', start)

out=[]
seq=0
for o in rows[start:]:
    if o.get('type')!='function_call': continue
    seq+=1
    name=o.get('name')
    args=o.get('arguments')
    if isinstance(args,str):
        try: args=json.loads(args)
        except Exception: args={'RAW':args}
    ts=datetime.datetime.fromtimestamp(o['timestamp']/1000).strftime('%m-%d %H:%M:%S')
    out.append({'n':seq,'ts':ts,'name':name,'args':args})

print('calls', len(out))
io.open('_calls.json','w',encoding='utf-8').write(json.dumps(out,ensure_ascii=False,indent=1))
from collections import Counter
print(Counter(c['name'] for c in out))
