"""Save manual cookies to xhs-cli format.

Usage:
    python save_cookies.py --a1 "your_a1_value" --web-session "your_web_session_value"
    or set env vars: REDBOOK_A1, REDBOOK_WEB_SESSION
"""
import argparse
import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / '.xhs-cli'
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description='Save Xiaohongshu cookies')
    parser.add_argument('--a1', default=os.environ.get('REDBOOK_A1', ''),
                        help='a1 cookie value (or set REDBOOK_A1 env var)')
    parser.add_argument('--web-session', default=os.environ.get('REDBOOK_WEB_SESSION', ''),
                        help='web_session cookie value (or set REDBOOK_WEB_SESSION env var)')
    args = parser.parse_args()

    a1 = args.a1
    web_session = args.web_session

    if not a1 or not web_session:
        print('ERROR: a1 and web_session are required.')
        print('Usage: python save_cookies.py --a1 "..." --web-session "..."')
        print('  or set env vars: REDBOOK_A1, REDBOOK_WEB_SESSION')
        return

    data = {'cookies': {'a1': a1, 'web_session': web_session}}
    cookies_file = CONFIG_DIR / 'cookies.json'
    cookies_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f'Cookies saved to: {cookies_file}')


if __name__ == '__main__':
    main()
