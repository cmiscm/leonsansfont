from pathlib import Path
from fontTools.ttLib import TTFont,newTable
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.ttLib.tables.ttProgram import Program
from license_constants import PLACEHOLDER_LICENSING_TEXT,OFL_BODY_TEXT
import json
import sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'fonts/variable';OUT.mkdir(parents=True,exist_ok=True)
f=TTFont(sys.argv[1])
from fontTools.otlLib.builder import buildStatTable
names=['Thin','ExtraLight','Light','Regular','Medium','SemiBold','Bold','ExtraBold','Black']
buildStatTable(f,[{'tag':'wght','name':'Weight','values':[dict(value=100+i*100,name=n,**({'flags':2} if i==3 else {})) for i,n in enumerate(names)]}])
# Resolve IUP before rounding the default outline: coincident rounded points
# can otherwise infer different deltas in intermediate weights.
for glyph, variations in f['gvar'].variations.items():
 coords, controls=f['glyf']._getCoordinatesAndControls(glyph,f['hmtx'].metrics)
 for variation in variations:variation.calcInferredDeltas(coords,controls.endPts)
scale_upem(f,2000)
for glyph, variations in f['gvar'].variations.items():
 coords, controls=f['glyf']._getCoordinatesAndControls(glyph,f['hmtx'].metrics)
 pts=list(coords)[:-4];tol=0 if len(set(pts))<len(pts) else 0.5
 for variation in variations:
  variation.roundDeltas();variation.optimize(coords,controls.endPts,tolerance=tol,isComposite=f['glyf'][glyph].isComposite())
thinID=f['name'].addName('Thin')
for i in f['fvar'].instances:
 if i.subfamilyNameID==2:i.subfamilyNameID=thinID
for a in f['STAT'].table.AxisValueArray.AxisValue:
 if a.ValueNameID==2:a.ValueNameID=thinID
os=f['OS/2'];os.version=max(4,os.version);os.fsType=0;os.fsSelection=(os.fsSelection|64|128)&~(1|32);os.recalcCodePageRanges(f);os.recalcUnicodeRanges(f);os.recalcAvgCharWidth(f)
copyright='Copyright 2019 The Leon Sans Project Authors (https://github.com/cmiscm/leonsansfont)'
updates={0:copyright,1:'Leon Sans Thin',2:'Regular',3:'2.000;NONE;LeonSans-Thin',13:PLACEHOLDER_LICENSING_TEXT['OFL.txt'],14:'https://openfontlicense.org'}
for key,val in updates.items():
 for n in list(f['name'].names):
  if n.nameID==key:f['name'].setName(val,key,n.platformID,n.platEncID,n.langID)
 f['name'].setName(val,key,3,1,0x409)
os.achVendID='NONE'
f['prep']=newTable('prep');f['prep'].program=Program();f['prep'].program.fromBytecode(b'\xb8\x01\xff\x85\xb0\x04\x8d');f['maxp'].maxStackElements=max(f['maxp'].maxStackElements,1)
f['gasp']=newTable('gasp');f['gasp'].version=1;f['gasp'].gaspRange={65535:15}
f['meta']=newTable('meta');f['meta'].data={'dlng':'Latn','slng':'Latn'}
# Existing user-coordinate progression is intentionally unchanged.
f['avar']=newTable('avar');f['avar'].segments={'wght':{-1.0:-1.0,0.0:0.0,1.0:1.0}}
f.save(OUT/'LeonSans[wght].ttf')
(ROOT/'OFL.txt').write_text(copyright+'\n'+OFL_BODY_TEXT)
print('Saved',OUT/'LeonSans[wght].ttf')
