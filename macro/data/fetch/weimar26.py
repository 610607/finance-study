"""Check the fixed source hashes and reproducible transcriptions for Chapter 26.

python data/fetch/weimar26.py [--offline]
No downloaded program is executed. Only source documents are fetched to WEB_CACHE.
Tables are factual subsets, manually transcribed and stored with their exact location.
The checks independently parse source table rows and verify the stored observations.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from verify_web_quotes import fetch
import json
ROOT=HERE.parents[1]
meta=json.loads((ROOT/'data/snapshots/weimar_facts.json').read_text())
for key,source in meta['sources'].items():
    path,note=fetch(key,source,'--offline' in sys.argv)
    if not path or note:
        raise SystemExit(f'{key}: {note}')
    print('ok',key,source['sha256'])
import subprocess
subprocess.run([sys.executable,str(ROOT/'checks/check_ch26.py')],check=True)
