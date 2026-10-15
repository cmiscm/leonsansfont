from fontTools.ttLib import TTFont
from fontbakery.fonts_public_pb2 import FamilyProto
from google.protobuf.text_format import MessageToString
from pathlib import Path
import shutil, subprocess
R=Path(__file__).resolve().parents[1];D=R/'fonts/variable';f=TTFont(D/'LeonSans[wght].ttf');m=FamilyProto();m.name='Leon Sans';m.designer='Jongmin Kim';m.license='OFL';m.category.append('SANS_SERIF');m.date_added='2026-10-11';m.subsets.extend(['latin','latin-ext','menu']);font=m.fonts.add();font.name='Leon Sans';font.style='normal';font.weight=400;font.filename='LeonSans[wght].ttf';font.post_script_name=f['name'].getDebugName(6);font.full_name=f['name'].getDebugName(4);font.copyright=f['name'].getDebugName(0);ax=m.axes.add();ax.tag='wght';ax.min_value=100;ax.max_value=900;m.source.repository_url='https://github.com/cmiscm/leonsansfont';m.source.branch='master';m.source.config_yaml='sources/config.yaml'
try:
 m.source.commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
except Exception:
 pass
for src_f, dst_f in [
 ('OFL.txt', 'OFL.txt'),
 ('fonts/variable/LeonSans[wght].ttf', 'LeonSans[wght].ttf'),
 ('documentation/article/ARTICLE.en_us.html', 'article/ARTICLE.en_us.html'),
 ('documentation/article/specimen.png', 'article/specimen.png'),
]:
 fm=m.source.files.add();fm.source_file=src_f;fm.dest_file=dst_f
T=R/'ofl/leonsans';T.mkdir(parents=True,exist_ok=True)
(T/'METADATA.pb').write_text(MessageToString(m))
shutil.copy(R/'OFL.txt',T/'OFL.txt')
shutil.copy(D/'LeonSans[wght].ttf',T/'LeonSans[wght].ttf')
if (R/'documentation/article').is_dir():
 shutil.copytree(R/'documentation/article',T/'article',dirs_exist_ok=True)

