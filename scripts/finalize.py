from pathlib import Path
from fontTools.ttLib import TTFont,newTable
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.ttLib.tables.ttProgram import Program
from license_constants import PLACEHOLDER_LICENSING_TEXT,OFL_BODY_TEXT
import json
import sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'fonts/variable';OUT.mkdir(parents=True,exist_ok=True)
OUTPUT=Path(sys.argv[2]) if len(sys.argv)>2 else OUT/'LeonSans[wght].ttf'
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
f=TTFont(sys.argv[1])
from fontTools.otlLib.builder import buildStatTable
names=['Thin','ExtraLight','Light','Regular','Medium','SemiBold','Bold','ExtraBold','Black']
buildStatTable(f,[{'tag':'wght','name':'Weight','values':[dict(value=100+i*100,name=n,**({'flags':2,'linkedValue':700} if i==3 else {})) for i,n in enumerate(names)]}])
# Resolve IUP before rounding the default outline: coincident rounded points
# can otherwise infer different deltas in intermediate weights.
for glyph, variations in f['gvar'].variations.items():
 coords, controls=f['glyf']._getCoordinatesAndControls(glyph,f['hmtx'].metrics)
 for variation in variations:variation.calcInferredDeltas(coords,controls.endPts)
scale_upem(f,2000)
for glyph, variations in f['gvar'].variations.items():
 coords, controls=f['glyf']._getCoordinatesAndControls(glyph,f['hmtx'].metrics)
 for variation in variations:
  variation.roundDeltas();variation.optimize(coords,controls.endPts,tolerance=0,isComposite=f['glyf'][glyph].isComposite())
from overlap_flags import set_overlap_flags
set_overlap_flags(f)
os=f['OS/2'];os.version=max(4,os.version);os.fsType=0;os.fsSelection=(os.fsSelection|64|128|256)&~(1|32);os.recalcCodePageRanges(f);os.recalcUnicodeRanges(f);nz=[w for w,_ in f['hmtx'].metrics.values() if w>0];os.xAvgCharWidth=sum(nz)//len(nz)
copyright='Copyright 2019 The Leon Sans Project Authors (https://github.com/cmiscm/leonsansfont)'
updates={0:copyright,1:'Leon Sans',2:'Regular',3:'2.006;NONE;LeonSans-Regular',5:'Version 2.006',4:'Leon Sans Regular',6:'LeonSans-Regular',13:PLACEHOLDER_LICENSING_TEXT['OFL.txt'],14:'https://openfontlicense.org'}
f['name'].removeNames(nameID=16);f['name'].removeNames(nameID=17)
f['name'].names=[n for n in f['name'].names if n.platformID!=1]
for key,val in updates.items():
 for n in list(f['name'].names):
  if n.nameID==key:f['name'].setName(val,key,n.platformID,n.platEncID,n.langID)
 f['name'].setName(val,key,3,1,0x409)
os.achVendID='NONE'
# The new below macron extends below descenders (e.g. j + U+0331 reaches
# -672 at Black). Reserve room consistently in Windows and typo metrics.
os.sTypoDescender=-800
os.usWinDescent=800
f['hhea'].descent=-800
f['prep']=newTable('prep');f['prep'].program=Program();f['prep'].program.fromBytecode(b'\xb8\x01\xff\x85\xb0\x04\x8d');f['maxp'].maxStackElements=max(f['maxp'].maxStackElements,1)
f['gasp']=newTable('gasp');f['gasp'].version=1;f['gasp'].gaspRange={65535:15}
f['meta']=newTable('meta');f['meta'].data={'dlng':'Latn','slng':'Latn'}
# Existing user-coordinate progression is intentionally unchanged.
f['avar']=newTable('avar');f['avar'].segments={'wght':{-1.0:-1.0,0.0:0.0,1.0:1.0}}
f['head'].fontRevision=2.006
f.save(OUTPUT)
(ROOT/'OFL.txt').write_text(copyright+'\n'+OFL_BODY_TEXT)
print('Saved',OUTPUT)
