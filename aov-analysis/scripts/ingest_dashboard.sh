#!/bin/bash
# usage: ingest_dashboard.sh <saved_tool_result>...  ; labels week by order dates, page by pagination.currentPage
for f in "$@"; do
python3 -I - "$f" <<'PY'
import json,sys,subprocess,os
f=sys.argv[1]; d=json.load(open(f)); sc=d['data']['structuredContent']
pg=sc['pagination']['currentPage']; dates=[o['date']['date'][:10] for o in sc['data']]
wk='w45' if min(dates)>='2026-11-02' else 'w44'
env=dict(os.environ, ORDERS_DIR='orders_dashboard')
subprocess.run([sys.executable,'-I','scripts/extract_orders_page.py',f,wk,str(pg)],env=env,check=True)
PY
done
