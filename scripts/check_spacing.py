"""Regression and expanded spacing checks; manual optical review remains necessary."""
from pathlib import Path
import json,string,itertools,unicodedata,hashlib,argparse
import uharfbuzz as hb
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen

parser=argparse.ArgumentParser(description='Screen shaped letter pairs for outline overlap.')
parser.add_argument('--font',type=Path,default=Path(__file__).resolve().parents[1]/'fonts/variable/LeonSans[wght].ttf')
parser.add_argument('--full',action='store_true',help='All encoded letters below U+2000 at four representative weights.')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
p=args.font;f=TTFont(p);hf=hb.Font(hb.Face(p.read_bytes()));order=f.getGlyphOrder()
letters=''.join(chr(cp) for cp in f.getBestCmap() if unicodedata.category(chr(cp)).startswith('L') and cp<0x2000)
pairs=list(itertools.product(letters,repeat=2)) if args.full else [('f','º'),('f','ˋ')]
weights=[100,400,700,900] if args.full else list(range(100,901,10))

issues=[];tested=0
for w in weights:
 gs=f.getGlyphSet(location={'wght':w});hf.set_variations({'wght':w});cache={}
 for a,b in pairs:
  buf=hb.Buffer();buf.add_str(a+b);buf.guess_segment_properties();hb.shape(hf,buf)
  paths=[];x=0
  for inf,pos in zip(buf.glyph_infos,buf.glyph_positions):
   n=order[inf.codepoint]
   if n not in cache:
    rec=DecomposingRecordingPen(gs);gs[n].draw(rec);cache[n]=rec
   path=pathops.Path();pen=TransformPen(path.getPen(),(1,0,0,1,x+pos.x_offset,pos.y_offset));cache[n].replay(pen);paths.append(path);x+=pos.x_advance
  if len(paths)==2:
   intersection=pathops.op(paths[0],paths[1],pathops.PathOp.INTERSECTION)
   if intersection.area>1:issues.append({'weight':w,'pair':a+b,'area':round(intersection.area,3)})
  tested+=1
out={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'weights':weights,'characters':letters if args.full else 'fºˋ','pairs_tested':tested,'overlaps_over_1_square_unit':issues,'note':'Geometric pair overlap screen after default HarfBuzz shaping; intentional joins require manual review. Not full spacing/kerning quality certification.'}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('tested',tested,'flags',len(issues));print(issues[:50])

raise SystemExit(bool(issues))
