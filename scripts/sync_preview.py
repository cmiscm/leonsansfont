"""Keep the self-contained local specimen and webfont tied to the release binary."""
from pathlib import Path
from fontTools.ttLib import TTFont
import base64,hashlib,io,json,re,unicodedata

ROOT=Path(__file__).resolve().parents[1]
font_path=ROOT/'fonts/variable/LeonSans[wght].ttf'
font=TTFont(font_path);font.flavor='woff2';buf=io.BytesIO();font.save(buf);woff=buf.getvalue()
web=ROOT/'fonts/webfonts';web.mkdir(exist_ok=True)
(web/'LeonSans[wght].woff2').write_bytes(woff)
(web/'leonsans.css').write_text("@font-face { font-family: 'Leon Sans'; src: url('LeonSans[wght].woff2') format('woff2'); font-style: normal; font-weight: 100 900; font-display: swap; }\n")
preview=ROOT/'Preview.html'
if not preview.exists():
 print('Webfont refreshed; optional Preview.html is absent.');raise SystemExit(0)
text=preview.read_text();old_info=json.loads(re.search(r'const BUILD_INFO = (.*);',text).group(1))
glyphs=json.loads(re.search(r'const GLYPHS = (.*);',text).group(1));cmap=font.getBestCmap();order=font.getGlyphOrder();byname={g['name']:g for g in glyphs}
if 'uni0331' not in byname:
 glyphs.append({'id':order.index('uni0331'),'name':'uni0331','cp':0x331,'cps':['U+0331'],'code':'U+0331','uname':unicodedata.name(chr(0x331)),'group':'combining','display':'◌'+chr(0x331)})
for weight in [100,400,900]:
 gs=font.getGlyphSet(location={'wght':weight})
 for glyph in glyphs:
  glyph['id']=order.index(glyph['name']);glyph['w'+str(weight)]=round(gs[glyph['name']].width)
info=dict(old_info,family='Leon Sans',version=font['name'].getDebugName(5).replace('Version ',''),glyphs=len(order),visible_characters=len(glyphs),ttf_sha256=hashlib.sha256(font_path.read_bytes()).hexdigest(),woff2_sha256=hashlib.sha256(woff).hexdigest())
info.pop('updated_at',None)
text=re.sub(r'data:font/woff2;base64,[A-Za-z0-9+/=]+','data:font/woff2;base64,'+base64.b64encode(woff).decode(),text)
text=re.sub(r'const BUILD_INFO = .*;',lambda _: 'const BUILD_INFO = '+json.dumps(info,ensure_ascii=False)+';',text)
text=re.sub(r'const SUPPORTED = new Set\(.*\);',lambda _: 'const SUPPORTED = new Set('+json.dumps(sorted(cmap))+');',text)
text=re.sub(r'const GLYPHS = .*;',lambda _: 'const GLYPHS = '+json.dumps(glyphs,ensure_ascii=False)+';',text)
# Update human-readable counts and build hash badge without touching binary data or glyph metrics.
text=text.replace('U+0300–U+0328','U+0300–U+0331').replace('478-Glyph','479-Glyph').replace('478 GLYPHS','479 GLYPHS').replace('478 Total','479 Total').replace('461 Visible','462 Visible').replace('461 VISIBLE','462 VISIBLE').replace('461 CHARS','462 CHARS').replace('461-Character','462-Character').replace('MATRIX (461)','MATRIX (462)').replace('461 / 461','462 / 462').replace('DESC -564','DESC -800')
text=re.sub(r'id="buildBadge">#[0-9a-fA-F]+<',f'id="buildBadge">#{info["ttf_sha256"][:8]}<',text)
preview.write_text(text)
print('Synchronized preview:',info['version'],info['glyphs'],info['ttf_sha256'])
