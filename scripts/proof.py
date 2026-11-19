"""Generate a portable specimen from the actual current variable font."""
import argparse,base64,hashlib,html,io
from pathlib import Path
from fontTools.ttLib import TTFont

ROWS=[('1 / figures','0 3 6 8 9'),('2 / curve of 5','5 6 9'),('3 / curve of 2','2 3 5'),('4 / bowls of 3','3 8 B'),('5 / omega','O Ω Ω'),('6 / ellipsis','P… ....'),('7 / cedilla','Ç ç Ş ş Ţ ţ'),('8 / dieresis','o ö u ü'),('9 / circumflex','u û ô'),('10 / dots and macron','ÿ Ā ā ī'),('11 / side caron','ď ľ ť Ľ'),('12 / bars','H Ħ h ħ'),('13 / ogonek','I Į i į'),('14 / diagonal bars','L Ł l ł'),('15 / eng','n ŋ h'),('16 / double acute','O Ő o ő Ű ű'),('17 / T bar','T Ŧ t ŧ'),('18 / U ogonek','U Ų u ų'),('19 / ezh','3 Ʒ ʒ Ǯ ǯ'),('20 / sharp S','B ß ẞ'),('Spacing regression','fº fˋ'),('Shaping regression','fi̱ fḻ ﬁ́ ﬂ́')]
def main():
    root=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('--font',type=Path,default=root/'fonts/variable/LeonSans[wght].ttf');parser.add_argument('--output',type=Path,default=root/'output/proof/index.html');args=parser.parse_args()
    raw=args.font.read_bytes();font=TTFont(io.BytesIO(raw));version=font['name'].getDebugName(5);font.flavor='woff2';buf=io.BytesIO();font.save(buf);encoded=base64.b64encode(buf.getvalue()).decode()
    css="""*{box-sizing:border-box}body{font:15px Arial,sans-serif;margin:28px;color:#141414}h1{font-size:24px}code{overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:170px repeat(4,minmax(320px,1fr));min-width:1450px}.cell{border-bottom:1px solid #ddd;padding:14px 10px;align-content:center}.sample{font-family:Leon;font-size:42px;line-height:1.6;white-space:nowrap}.small{font-family:Leon;line-height:1.65;margin:16px 0}.scroll{overflow:auto}small{color:#555}@media print{body{margin:12px}.grid{min-width:0;grid-template-columns:100px repeat(4,1fr)}.sample{font-size:24px}.cell{break-inside:avoid}}"""
    content=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Leon Sans proof</title><style>@font-face{{font-family:Leon;src:url(data:font/woff2;base64,{encoded}) format("woff2");font-weight:100 900}}{css}</style><h1>Leon Sans — {html.escape(version)}</h1><p>Original review items, spacing and shaping regressions. Generated from the current binary.</p><p><small>TTF SHA-256: <code>{hashlib.sha256(raw).hexdigest()}</code></small></p><div class="scroll"><div class="grid">'
    for label in ['Review item','Thin 100','Regular 400','Bold 700','Black 900']:content+=f'<div class="cell">{label}</div>'
    for label,text in ROWS:
        content+=f'<div class="cell">{html.escape(label)}</div>'
        for weight in [100,400,700,900]:content+=f'<div class="cell sample" style="font-weight:{weight}">{html.escape(text)}</div>'
    content+='</div></div><h2>All nine named weights</h2>'
    for weight in range(100,901,100):
        content+=f'<p><small>Weight {weight}</small></p><div class="small" style="font-weight:{weight};font-size:48px">3 8 Ω ß ẞ Ç ç Į į Ő ő Ų ų Ǯ ǯ</div>'
    content+='<h2>Text sizes</h2>'
    for weight in [100,400,700,900]:
        for size in [16,24,40]:content+=f'<p><small>Weight {weight} / {size}px</small></p><div class="small" style="font-weight:{weight};font-size:{size}px">Straße groß heißen Fuß — STRAẞE GROẞ<br>Noël déjà façade — Ą Ę Į Ų ą ę į ų<br>Příliš žluťoučký kůň — ď ľ ť Ő ő Ű ű<br>fº fˋ fi̱ fḻ ﬁ́ ﬂ́</div>'
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(content+'</html>');print(args.output)
if __name__=='__main__':main()
