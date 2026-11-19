"""Regression check for base/above-mark and stacked-mark collisions."""
from pathlib import Path
import json,hashlib,argparse
import uharfbuzz as hb,pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
parser=argparse.ArgumentParser(description='Check modified above marks and their stacked combinations for geometric collisions.')
parser.add_argument('--font',type=Path,default=Path(__file__).resolve().parents[1]/'fonts/variable/LeonSans[wght].ttf')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
p=args.font;f=TTFont(p);hf=hb.Font(hb.Face(p.read_bytes()));issues=[];cases=0
for w in range(100,901,10):
 hf.set_variations({'wght':w});gs=f.getGlyphSet(location={'wght':w});cache={}
 for base in 'aAoOuUyYiIjJ':
  for first in ['\u0307','\u0308','\u030b','\u0301','\u0300']:
   for second in ['\u0300','\u0301','\u0304','\u0308','\u030b']:
    s=base+first+second;b=hb.Buffer();b.add_str(s);b.guess_segment_properties();hb.shape(hf,b);paths=[];x=0
    for info,pos in zip(b.glyph_infos,b.glyph_positions):
     n=f.getGlyphName(info.codepoint)
     if n not in cache:
      rec=DecomposingRecordingPen(gs);gs[n].draw(rec);cache[n]=rec
     q=pathops.Path();cache[n].replay(TransformPen(q.getPen(),(1,0,0,1,x+pos.x_offset,pos.y_offset)));paths.append(q);x+=pos.x_advance
    for i in range(len(paths)):
     for j in range(i+1,len(paths)):
      area=pathops.op(paths[i],paths[j],pathops.PathOp.INTERSECTION).area
      if area>1:issues.append([w,s,i,j,area])
    cases+=1
r={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cases':cases,'overlaps_over_1_square_unit':issues,'scope':'Base + modified dot/acute/grave/dieresis/double acute + above mark, 81 weights. Geometric overlap, not optical certification.'}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2));print(cases,len(issues));raise SystemExit(bool(issues))
