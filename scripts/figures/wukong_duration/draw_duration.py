"""Bilingual survival duration chart, with mean bars and median marks."""
from pathlib import Path
from html import escape
ROWS=[('Stationary reference',23.6,None,6),('wk-rsi-v1',108.1,114.9,10),('wk-rsi-v2',160.0,170.1,10),('wk-rsi-v3',160.9,166.7,5),('wk-rsi-v4',260.5,212.2,5)]
ROOT=Path(__file__).parent
for lang in ['zh','en']:
 title='平均记录时长（s）' if lang=='zh' else 'Mean recorded episode duration (s)'
 note='条形表示均值，竖线表示中位数；灰色表示静止参考。' if lang=='zh' else 'Bars show means; vertical marks show medians; gray indicates the stationary reference.'
 p=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 350" role="img" aria-label="Recorded episode duration by model"><rect width="1000" height="350" fill="white"/><g font-family="Arial,Noto Sans CJK SC,sans-serif" fill="#344153">',f'<text x="205" y="25" font-size="17">{title}</text>']
 for value in (0,100,200,300):
  x=205+value*2;p.append(f'<path d="M{x} 40 V300" stroke="#e4e8ec"/><text x="{x}" y="325" text-anchor="middle" font-size="14">{value}</text>')
 for i,(label,mean,median,n) in enumerate(ROWS):
  if i==0 and lang=='zh':label='静止参考'
  y=70+48*i;color='#b3b9c1' if i==0 else '#4c6982'
  p.append(f'<text x="185" y="{y}" text-anchor="end" font-size="16">{escape(label)}</text><rect x="205" y="{y-17}" width="{mean*2}" height="24" fill="{color}"/><text x="{215+max(mean,median or 0)*2}" y="{y}" font-size="15">{mean:.1f} s</text><text x="905" y="{y}" font-size="14">n = {n}</text>')
  if median is not None:p.append(f'<path d="M{205+median*2} {y-22} v34" stroke="#344153" stroke-width="2"/>')
 p.append(f'<text x="205" y="347" font-size="13">{note}</text></g></svg>')
 (ROOT/f'wukong_duration_{lang}.svg').write_text(''.join(p))
