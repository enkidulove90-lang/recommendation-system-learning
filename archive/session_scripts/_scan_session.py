# -*- coding: utf-8 -*-
import json, io, os
p = r"C:/Users/xu.yan1/.workbuddy/projects/c-Users-xu.yan1-papers-recommendation-system-learning/e5a041fe-b710-4c95-b524-1670acb9fbe9.jsonl"
n=0
kinds={}
with io.open(p, encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        n+=1
        try: o=json.loads(line)
        except Exception as e:
            kinds['PARSE_FAIL']=kinds.get('PARSE_FAIL',0)+1; continue
        t=o.get('type')
        kinds[t]=kinds.get(t,0)+1
        if n<=3:
            print('LINE',n,'keys',list(o.keys()))
            c=o.get('message',{}).get('content') if isinstance(o.get('message'),dict) else o.get('content')
            print(' content type', type(c).__name__)
            if isinstance(c,list):
                for b in c:
                    if isinstance(b,dict): print('   block', b.get('type'), list(b.keys()))
print('total lines', n)
print(kinds)
