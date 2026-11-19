"""Regression checks for normalization, soft dots and accented fi/fl sequences."""
import argparse,hashlib,json,unicodedata
from pathlib import Path
from fontTools.ttLib import TTFont
import uharfbuzz as hb

ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--font',type=Path,default=ROOT/'fonts/variable/LeonSans[wght].ttf');parser.add_argument('--output',type=Path)
    args=parser.parse_args();raw=args.font.read_bytes();font=TTFont(args.font);shaper=hb.Font(hb.Face(raw));cmap=font.getBestCmap();errors=[];cases=0
    marks=[chr(c) for c in cmap if unicodedata.category(chr(c))=='Mn']
    pairs=[(chr(c),unicodedata.normalize('NFD',chr(c))) for c in cmap]
    pairs=[(a,b) for a,b in pairs if a!=b and all(ord(c) in cmap for c in b)]
    def shape(text,features=None):
        b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(shaper,b,features)
        return [(font.getGlyphName(g.codepoint),p.x_advance,p.x_offset,p.y_offset) for g,p in zip(b.glyph_infos,b.glyph_positions)]
    def check(ok,context):
        nonlocal cases
        cases+=1
        if not ok:errors.append(context)
    for weight in range(100,901,10):
        shaper.set_variations({'wght':weight})
        for a,b in pairs:check(shape(a)==shape(b),[weight,'NFC/NFD',a])
        for encoded,plain in [('ﬁ','fi'),('ﬂ','fl')]:
            check(shape(encoded)==shape(plain),[weight,'unmarked presentation form',plain])
            check(shape(plain)[0][0]==plain,[weight,'ordinary ligature',plain])
            for mark in marks:
                text=plain+mark;actual=shape(text);without=shape(text,{'liga':False})
                check(actual==without,[weight,'marked ligature must retain base attachment',text])
                check(shape(encoded+mark)==actual,[weight,'encoded ligature with mark',text])
                check(all(g[0]!='.notdef' for g in actual),[weight,'missing glyph',text])
        for base in ['i','j']:
            check(shape(base+'\u0331')[0][0]==base,[weight,'dot must remain with below mark',base])
            check(shape(base+'\u0331\u030b')[0][0] in ['i.dotless','uni0237'],[weight,'dot must disappear with above mark',base])
    report={'sha256':hashlib.sha256(raw).hexdigest(),'weights':81,'normalization_pairs':len(pairs),'combining_marks':len(marks),'assertions':cases,'errors':errors}
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({**report,"errors":errors[:10],"error_count":len(errors)},ensure_ascii=False));raise SystemExit(bool(errors))
if __name__=='__main__':main()
