"""Check an isolated, complete submission package; never suppress checks."""
import argparse, json, shutil, subprocess, tempfile
from pathlib import Path
from datetime import datetime, timezone
from check_release import digest, package_hashes

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--fontspector',default='fontspector')
parser.add_argument('--output',type=Path,default=ROOT/'output/qa')
parser.add_argument('--offline',action='store_true')
args=parser.parse_args();args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=True)
exe=shutil.which(args.fontspector) or str(Path(args.fontspector).resolve())
with tempfile.TemporaryDirectory(prefix='leonsans-qa-') as directory:
    package=Path(directory)/'leonsans';shutil.copytree(ROOT/'ofl/leonsans',package)
    inputs=[str(p) for p in sorted(package.rglob('*')) if p.is_file()]
    cmd=[exe,'--profile','googlefonts','--full-lists','--timeout','30','--json',str(args.output/'fontspector.json'),'--html',str(args.output/'fontspector.html')]
    if args.offline:cmd.append('--skip-network')
    for name in ['fontspector.json','fontspector.html','provenance.json']:
        (args.output/name).unlink(missing_ok=True)
    result=subprocess.run(cmd+inputs)
    report=args.output/'fontspector.json'
    provenance={'profile':'googlefonts','offline':args.offline,'excluded_checks':[],
                'checked_at_utc':datetime.now(timezone.utc).isoformat(),'returncode':result.returncode,
                'checker_sha256':digest(Path(exe)),'package_files':package_hashes(package),
                'report_sha256':digest(report) if report.is_file() else None}
    (args.output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    raise SystemExit(result.returncode)
