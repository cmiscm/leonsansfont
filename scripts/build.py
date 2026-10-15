#!/usr/bin/env python3
"""Build Leon Sans from editable UFO masters using the pinned open-source toolchain."""
from pathlib import Path
import subprocess,sys,tempfile,os
ROOT=Path(__file__).resolve().parents[1]
env=dict(os.environ)
env.setdefault('SOURCE_DATE_EPOCH',str(1791676800))
env.setdefault('PYTHONDONTWRITEBYTECODE','1')
with tempfile.TemporaryDirectory(prefix='leonsans-build-') as tmp:
 raw=Path(tmp)/'LeonSans.ttf'
 subprocess.run([sys.executable,'-B','-m','fontmake','-m',str(ROOT/'sources/LeonSans.designspace'),'-o','variable','--output-path',str(raw),'--no-production-names','--keep-overlaps','--keep-direction'],check=True,cwd=ROOT,env=env)
 subprocess.run([sys.executable,'-B',str(ROOT/'scripts/finalize.py'),str(raw)],check=True,cwd=ROOT,env=env)

subprocess.run([sys.executable,'-B',str(ROOT/'scripts/prepare_metadata.py')],check=True,cwd=ROOT,env=env)
