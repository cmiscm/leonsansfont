"""Package the family without falsely attributing a dirty build to HEAD."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
from fontTools.ttLib import TTFont
from check_release import release_errors
from gfmetadata.fonts_public_pb2 import FamilyProto
from google.protobuf.text_format import MessageToString

ROOT=Path(__file__).resolve().parents[1]
TRACKED_INPUTS=['Makefile','requirements.in','sources','scripts','fonts','documentation','README.md','requirements.txt','requirements-builder.txt','OFL.txt','AUTHORS.txt','CONTRIBUTORS.txt']

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--release',action='store_true',help='Require a clean, committed source tree.')
    parser.add_argument('--qa-directory',type=Path,default=ROOT/'output/qa',help='Online, unfiltered QA evidence for this exact package.')
    args=parser.parse_args()
    source_commit=None
    try:
        status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*TRACKED_INPUTS],cwd=ROOT,text=True)
        if not status:
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except (subprocess.CalledProcessError,FileNotFoundError):
        status='Source checkout has no Git provenance.'
    if args.release and not source_commit:
        raise SystemExit('Release packaging requires committed sources. Commit the reviewed release files, then rerun with --release.')
    binary=ROOT/'fonts/variable/LeonSans[wght].ttf';font=TTFont(binary)
    metadata=FamilyProto(name='Leon Sans',designer='Jongmin Kim',license='OFL',date_added='2026-10-11')
    metadata.category.append('SANS_SERIF')
    metadata.subsets.extend(['latin','latin-ext','menu'])
    entry=metadata.fonts.add(name='Leon Sans',style='normal',weight=400,filename=binary.name)
    entry.post_script_name=font['name'].getDebugName(6)
    entry.full_name=font['name'].getDebugName(4)
    entry.copyright=font['name'].getDebugName(0)
    metadata.axes.add(tag='wght',min_value=100,max_value=900)
    metadata.source.repository_url='https://github.com/cmiscm/leonsansfont'
    metadata.source.branch='master'
    metadata.source.config_yaml='sources/config.yaml'
    if source_commit:metadata.source.commit=source_commit
    mappings=[('OFL.txt','OFL.txt'),('fonts/variable/'+binary.name,binary.name),('documentation/article/ARTICLE.en_us.html','article/ARTICLE.en_us.html'),('documentation/article/specimen.png','article/specimen.png')]
    package=ROOT/'ofl/leonsans';package.mkdir(parents=True,exist_ok=True)
    # Google Fonts uses article OR legacy DESCRIPTION, never both.
    (package/'DESCRIPTION.en_us.html').unlink(missing_ok=True)
    for source,destination in mappings:
        metadata.source.files.add(source_file=source,dest_file=destination)
        out=package/destination;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/source,out)
    (package/'METADATA.pb').write_text(MessageToString(metadata))
    qa_errors=release_errors(args.qa_directory,package) if args.release else []
    manifest={'release_ready':bool(args.release and source_commit and not qa_errors),'source_commit_verified':bool(source_commit),'source_commit':source_commit,'font_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'files':{}}
    for item in TRACKED_INPUTS:
        entry=ROOT/item
        paths=sorted(entry.rglob('*')) if entry.is_dir() else [entry]
        for path in paths:
            if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc' and path.name not in {'build.ninja','.ninja_log','.ninja_deps'}:
                manifest['files'][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT/'ofl/build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if qa_errors:raise SystemExit('Release QA blocked: '+'; '.join(qa_errors))
    if not source_commit:print('Development package: source.commit intentionally omitted until reviewed changes are committed.')

if __name__=='__main__':main()
