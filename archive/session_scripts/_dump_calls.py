# -*- coding: utf-8 -*-
import json, io
calls = json.load(io.open('_calls.json', encoding='utf-8'))
SHELL2 = "Power" + "Shell"
lines = []
for c in calls:
    a = c['args']; nm = c['name']
    lines.append('#%d %s %s' % (c['n'], c['ts'], nm))
    if nm in ('Bash', SHELL2):
        lines.append('  desc: %s' % a.get('description', ''))
        lines.append('  cmd: %s' % a.get('command', ''))
        for k in ('timeout', 'run_in_background'):
            if k in a:
                lines.append('  %s: %s' % (k, a[k]))
    elif nm == 'Skill':
        lines.append('  skill: %s  args=%s' % (a.get('skill'), a.get('args')))
    elif nm in ('Write', 'Edit', 'Read'):
        lines.append('  file: %s' % a.get('file_path'))
        if nm == 'Write':
            lines.append('  content_len: %d' % len(a.get('content', '')))
    elif nm == 'ViewImage':
        lines.append('  img: %s' % a.get('image_path'))
        lines.append('  q: %s' % a.get('query', '')[:160])
    elif nm == 'WebFetch':
        lines.append('  url: %s' % a.get('url'))
        lines.append('  prompt: %s' % a.get('prompt', '')[:200])
    elif nm == 'present_files':
        lines.append('  files: %s' % json.dumps(a.get('files'), ensure_ascii=False))
        lines.append('  expl: %s' % a.get('explanation', ''))
    else:
        lines.append('  args: %s' % json.dumps(a, ensure_ascii=False)[:300])
    lines.append('')
io.open('_calls_readable.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('lines', len(lines))
