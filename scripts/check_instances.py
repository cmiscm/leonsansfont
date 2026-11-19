"""Validate the variable font and every named instance with OpenType Sanitizer."""
import argparse,hashlib,json,tempfile
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import ots

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--font',type=Path,default=Path(__file__).resolve().parents[1]/'fonts/variable/LeonSans[wght].ttf')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();source=TTFont(args.font);results=[]
    locations=[dict(i.coordinates) for i in source['fvar'].instances]
    with tempfile.TemporaryDirectory(prefix='leonsans-instances-') as directory:
        folder=Path(directory);files=[('variable',args.font)]
        for index,location in enumerate(locations):
            font=instantiateVariableFont(TTFont(args.font),location,inplace=True,updateFontNames=True)
            path=folder/f'{index}.ttf';font.save(path);files.append((location,path))
        for index,(location,path) in enumerate(files):
            result=ots.sanitize(str(path),str(folder/f'sanitized-{index}.ttf'),capture_output=True)
            results.append({'location':location,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'exit_code':result.returncode,'stdout':result.stdout.decode(),'stderr':result.stderr.decode()})
    report={'source_sha256':hashlib.sha256(args.font.read_bytes()).hexdigest(),'results':results,'failures':sum(r['exit_code']!=0 for r in results),'scope':'OpenType Sanitizer structure validation; not Google Fonts acceptance.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(f"Checked {len(results)} binaries; {report['failures']} sanitizer failures")
    raise SystemExit(bool(report['failures']))
if __name__=='__main__':main()
