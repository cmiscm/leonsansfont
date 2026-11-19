"""Require an online, unfiltered Google Fonts report for the exact package."""
import argparse,hashlib,json
from pathlib import Path

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def package_hashes(package):
    return {str(p.relative_to(package)):digest(p) for p in sorted(package.rglob('*')) if p.is_file()}
def release_errors(qa_directory,package):
    report_path=qa_directory/'fontspector.json';provenance_path=qa_directory/'provenance.json'
    if not report_path.is_file() or not provenance_path.is_file():return ['QA report or its provenance record is missing.']
    try:
        report=json.loads(report_path.read_text());provenance=json.loads(provenance_path.read_text())
    except (OSError,ValueError) as exc:return [f'Cannot read QA evidence: {exc}']
    errors=[]
    if provenance.get('report_sha256')!=digest(report_path):errors.append('Report hash does not match the recorded run.')
    if provenance.get('profile')!='googlefonts' or provenance.get('offline') is not False or provenance.get('excluded_checks')!=[]:errors.append('Require an online, unfiltered googlefonts profile run.')
    if provenance.get('package_files')!=package_hashes(package):errors.append('Submission files changed since QA.')
    if provenance.get('returncode')!=0:errors.append('Fontspector did not exit successfully.')
    if not report.get('summary',{}).get('PASS',0):errors.append('No passing checks recorded.')
    blocking={key:report.get('summary',{}).get(key,0) for key in ['FATAL','ERROR','FAIL','WARN']}
    if any(blocking.values()):errors.append('Unresolved results: '+', '.join(f'{k}={v}' for k,v in blocking.items() if v))
    return errors

def main():
    root=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser()
    parser.add_argument('--qa-directory',type=Path,default=root/'output/qa');parser.add_argument('--package',type=Path,default=root/'ofl/leonsans');args=parser.parse_args()
    errors=release_errors(args.qa_directory,args.package)
    print('\n'.join(errors) if errors else 'Strict technical QA gate passed. Design approval and release provenance remain separate requirements.')
    raise SystemExit(bool(errors))
if __name__=='__main__':main()
