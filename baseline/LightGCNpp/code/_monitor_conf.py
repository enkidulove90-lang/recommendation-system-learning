"""Tail a training log and surface conf_mean / Epoch / TEST lines for up to max_sec.

Usage: python _monitor_conf.py <log_path> [max_sec]
Used to verify the v3 gradient fix: conf_mean should recover from v2's
0.026 collapse back to the 0.3-0.7 band by ~epoch 5.
"""
import time, sys, os


def main():
    log = sys.argv[1]
    max_sec = int(sys.argv[2]) if len(sys.argv) > 2 else 540
    with open(log, 'r', errors='replace') as f:
        f.seek(0, os.SEEK_END)          # only watch new lines
        t0 = time.time()
        seen_conf = []
        epoch_marks = 0
        while time.time() - t0 < max_sec:
            line = f.readline()
            if not line:
                time.sleep(2)
                continue
            s = line.rstrip()
            low = s.lower()
            if 'conf_mean' in s:
                print(s)
                seen_conf.append(s)
            elif 'epoch' in low and ('test' in low or 'train' in low or low.startswith('epoch')):
                print('[EPOCH]', s)
                epoch_marks += 1
            elif 'test' in low or 'best' in low:
                print('[EVAL]', s)
        print('=== monitor window ended (%.0fs) ===' % (time.time() - t0))
        print('conf_mean lines seen:', len(seen_conf))
        if seen_conf:
            print('first:', seen_conf[0])
            print('last :', seen_conf[-1])


if __name__ == '__main__':
    main()
