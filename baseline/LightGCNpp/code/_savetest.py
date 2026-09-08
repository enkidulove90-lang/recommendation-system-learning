import os, json, time
out = os.path.abspath('results_idea2.json')
tmp = out + '.tmptest'
data = {"_test": True}
with open(tmp, 'w') as f:
    json.dump(data, f)
try:
    os.replace(tmp, out)
    print("os.replace: OK")
    os_replace_works = True
except Exception as e:
    print("os.replace FAILED:", repr(e))
    os_replace_works = False
# try direct write
try:
    with open(out, 'w') as f:
        json.dump(data, f)
    print("direct write('w'): OK")
    direct_works = True
except Exception as e:
    print("direct write FAILED:", repr(e))
    direct_works = False
# cleanup
try:
    with open(out, 'r') as f:
        d = json.load(f)
    d.pop('_test', None)
    with open(out, 'w') as f:
        json.dump(d, f)
    print("cleanup OK")
except Exception as e:
    print("cleanup note:", repr(e))
print("RESULT os_replace_works=", os_replace_works, "direct_works=", direct_works)
