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

print('=== 真实 user_query 消息 ===')
marks=[]
for i,o in enumerate(rows):
    if o.get('type')=='message' and o.get('role')=='user':
        q=uq(o)
        if q:
            marks.append((i,o['timestamp'],q))
            print(len(marks), datetime.datetime.fromtimestamp(o['timestamp']/1000).strftime('%m-%d %H:%M'), '|', q[:70].replace('\n',' '))
