#!/usr/bin/env python3
"""Fallback when a page came back inline: pass a JSON file whose content is the tool's
structuredContent object (or the full tool result). Usage same as extract_orders_page.py."""
import json, sys, subprocess, os
src, day, page = sys.argv[1:4]
d = json.load(open(src))
if 'data' in d and isinstance(d['data'], list):  # bare structuredContent
    d = {'data': {'structuredContent': d}}
tmp = src + '.wrapped.json'
json.dump(d, open(tmp, 'w'), ensure_ascii=False)
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, '-I', os.path.join(here, 'extract_orders_page.py'), tmp, day, page], check=True)
