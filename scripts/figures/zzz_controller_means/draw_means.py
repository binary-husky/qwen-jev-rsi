"""Mean completion-time comparison; failed runs have no numerical bar."""
from pathlib import Path
import json
from html import escape
ROOT=Path(__file__).parent
DATA=json.loads((ROOT/'means.json').read_text())['rows']
for lang in ['zh','en']:
 title='平均完成用时（s，仅统计完成局）' if lang=='zh' else 'Mean completion time (s, completed episodes only)'
 fail='失败' if lang=='zh' else 'Failed'
 note='无完成记录时标注失败，不绘制数值柱。时间越短越好。' if lang=='zh' else 'No completion: marked Failed, without a numerical bar. Lower is better.'
 p=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 480" role="img" aria-labelledby="title desc">',f'<title id="title">{escape(title)}</title><desc id="desc">{escape(note)}</desc>','<rect width="1100" height="480" fill="white"/><g font-family="Arial, Noto Sans CJK SC, sans-serif" fill="#344153">',f'<text x="65" y="32" font-size="19">{escape(title)}</text>']
 colors=['#eb6834','#8056b3']
 for j,model in enumerate(['zzz-rsi-v2','zzz-rsi-v3']):
  x=760+j*160;p.append(f'<rect x="{x}" y="18" width="16" height="16" rx="2" fill="{colors[j]}"/><text x="{x+25}" y="31" font-size="16">{model}</text>')
 base=385;scale=.9
 for tick in range(0,351,50):
  y=base-tick*scale;p.append(f'<line x1="65" y1="{y}" x2="1070" y2="{y}" stroke="#e4e8ec"/><text x="52" y="{y+5}" text-anchor="end" font-size="14">{tick}</text>')
 for i,(boss,v2,v3) in enumerate(DATA):
  cx=138+i*143
  for j,val in enumerate([v2,v3]):
   x=cx-49+j*52
   if val is None:
    p.append(f'<text x="{x+21}" y="{base-12}" text-anchor="middle" font-size="15" fill="#697582">{fail}</text>')
   else:
    h=val*scale;y=base-h;p.append(f'<rect x="{x}" y="{y:.2f}" width="42" height="{h:.2f}" rx="2" fill="{colors[j]}"/><text x="{x+21}" y="{y-9:.2f}" text-anchor="middle" font-size="15">{val:.1f}</text>')
  p.append(f'<text x="{cx}" y="414" text-anchor="middle" font-size="16">{boss}</text>')
 p.append(f'<text x="65" y="459" font-size="14" fill="#697582">{escape(note)}</text></g></svg>')
 (ROOT/f'controller_means_{lang}.svg').write_text(''.join(p))
