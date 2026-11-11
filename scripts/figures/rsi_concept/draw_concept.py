"""Editable vector concept diagram: human learning above language-model RSI.
All icons, labels and connectors are native SVG; no embedded raster images.
"""
from pathlib import Path
from html import escape
ROOT = Path(__file__).parent
INDIGO='#4d5886'; GOLD='#bc8b32'; TEAL='#248f86'; INK='#263447'

def brain():
    return '<path d="M0-43 C-18-59-40-48-43-31 C-63-30-72-12-65 3 C-80 19-63 44-43 42 C-40 61-15 63 0 47 C16 64 43 59 47 41 C68 43 80 21 67 5 C77-13 61-31 45-31 C42-50 16-61 0-43Z"/><path d="M0-43V47 M-43-31Q-25-30-28-13 M-61 3Q-39-8-28 8 M-43 42Q-47 23-24 25 M-13-25Q-27-10-13 0 M-9 39Q-26 39-24 25 M45-31Q24-30 29-13 M64 5Q41-7 28 9 M47 41Q46 22 25 26 M13-26Q29-12 13 0 M9 40Q27 40 25 26"/>'

def book():
    return '<path d="M0-42Q-27-55-64-43V49Q-28 37 0 50Q28 37 64 49V-43Q27-55 0-42V50 M-64-34L-73-30V59Q-30 47 0 60Q30 47 73 59V-30L64-34"/><path d="M-51-22H-16 M-51-9H-16 M-51 4H-24 M16-22H51 M16-9H51 M16 4H43 M-51 20H-16 M16 20H51" stroke-width="3"/>'

def swimmer():
    return '<circle cx="42" cy="-20" r="12"/><path d="M-53 9L-22-13L8-8L23 5 M-22-13L-3-43L26-59 M8-8L-6 14 M-53 9L-74 3" stroke-width="6"/><path d="M-78 31Q-65 20-52 31T-26 31T0 31T26 31T52 31T78 31 M-78 52Q-65 41-52 52T-26 52T0 52T26 52T52 52T78 52" stroke-width="3"/>'


def head():
    return '<path d="M-48 62L-36 31C-61 5-59-39-31-56C-6-72 30-56 35-29L40-12L51 3L38 8V25Q35 37 14 34L13 62 M-36 31Q-14 45 13 34"/><path d="M9-12Q18-7 26-12 M29 20H38"/><circle cx="56" cy="-48" r="7"/><circle cx="76" cy="-70" r="12"/>'

def practice():
    return '<g transform="translate(-10 3) scale(.9)">'+swimmer()+'</g><circle cx="65" cy="-54" r="22" fill="white"/><path d="M54-54L62-46L77-63"/>'

def memory():
    return brain()+'<path d="M-43-13H43 M-39 24H38" stroke="white" stroke-width="13"/><path d="M-43-13H43 M-39 24H38"/><g fill="white"><circle cx="-43" cy="-13" r="8"/><circle cy="-13" r="8"/><circle cx="43" cy="-13" r="8"/><circle cx="-39" cy="24" r="8"/><circle cx="8" cy="24" r="8"/><circle cx="38" cy="24" r="8"/></g>'

def document():
    return '<path d="M-45-61H20L49-31V61H-45Z M20-61V-31H49"/><circle cx="-19" cy="-28" r="11"/><path d="M-29 4Q-20-7-9 4T11 4 M-29 23Q-18 12-5 23T27 23 M-29 42Q-17 32-3 42T27 42 M15-4L25-22L36-4"/>'

def rsi():
    s='<path d="M-63-43C-26-79 37-77 66-39 M-66 40C-34 77 29 78 64 43"/><path d="M66-56V-39H49 M-66 56V40H-49"/>'
    for x in [-58,0,58]:
        s+=f'<g transform="translate({x} 0)"><rect x="-23" y="-23" width="46" height="46" rx="4" fill="white"/><path d="M-17 14L-3-8L5 3L12-5L19 14Z" stroke-width="2.8"/><circle cx="-12" cy="-12" r="3" fill="currentColor" stroke="none"/></g>'
    return s+'<path d="M-35 0H-23 M23 0H35"/>'

def network():
    s=''
    for xa,xb,ya,yb in [(-60,0,[-36,0,36],[-54,-18,18,54]),(0,60,[-54,-18,18,54],[-36,0,36])]:
        for a in ya:
            for b in yb:s+=f'<path d="M{xa} {a}L{xb} {b}" stroke-width="1.7" opacity=".65"/>'
    for x,ys in [(-60,[-36,0,36]),(0,[-54,-18,18,54]),(60,[-36,0,36])]:
        for y in ys:s+=f'<circle cx="{x}" cy="{y}" r="11" fill="white"/>'
    return s

def realtime():
    return '<path d="M-28-54C-86-30-78 40-30 57 M28 54C86 30 78-40 30-57 M-30 42V57H-46 M30-42V-57H46"/><rect x="-22" y="-70" width="44" height="38" rx="6"/><circle cy="-51" r="10"/><circle cy="48" r="21"/><path d="M0 17V27 M0 69V79 M-31 48H-21 M21 48H31 M-22 26L-15 33 M15 63L22 70 M22 26L15 33 M-15 63L-22 70" stroke-width="7"/><path d="M-16 1H-5L1-13L8 13L14 1H24"/>'

LABELS={
'zh':[['深度思考','理论概念理解','有针对性地练习','肌肉记忆','学会某项运动技能'],['推理模型','模糊描述的先验知识','System One RSI','JEV 模型','完成高频实时任务']],
'en':[['Deep thinking','Conceptual understanding','Targeted practice','Muscle memory','Acquire a motor skill'],['Reasoning model','Loosely described prior knowledge','System One RSI','JEV model','High-frequency real-time tasks']]}
for lang,labels in LABELS.items():
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1760" height="650" viewBox="0 0 1760 650" role="img" aria-labelledby="title desc">',
       '<title id="title">Human learning and System One RSI</title><desc id="desc">Human: deep thinking, conceptual understanding, targeted practice, muscle memory, motor skills. Language Model: reasoning, prior knowledge, few-sample RSI, JEV, real-time tasks.</desc>',
       '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L8 5L1 9" fill="none" stroke="#788695" stroke-width="1.6" stroke-linejoin="round"/></marker></defs>',
       '<rect width="1760" height="650" fill="white"/><g font-family="Inter, Arial, Noto Sans CJK SC, Microsoft YaHei, sans-serif">']
    xs=[340,640,940,1240,1540]
    for x in xs:p.append(f'<path d="M{x} 275V348" stroke="#c9d1d9" stroke-width="2" stroke-dasharray="3 7" stroke-linecap="round"/>')
    icons=[[head,book,practice,memory,swimmer],[brain,document,rsi,network,realtime]]
    for row,(y,label) in enumerate([(155,'Human'),(465,'Language Model')]):
        p.append(f'<rect x="18" y="{y-26}" width="176" height="52" rx="9" fill="#f0f3f6"/><text x="106" y="{y+7}" text-anchor="middle" fill="{INK}" font-size="21" font-weight="600">{label}</text>')
        for i,x in enumerate(xs):
            col=[INDIGO,INDIGO,GOLD,TEAL,TEAL][i]
            p.append(f'<g transform="translate({x} {y})" fill="none" stroke="{col}" color="{col}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">{icons[row][i]()}</g>')
            text=labels[row][i]
            lines=[text]
            if lang=='en' and i==1:lines=['Conceptual','understanding'] if row==0 else ['Loosely described','prior knowledge']
            if lang=='en' and i==4:lines=['Acquire a motor skill'] if row==0 else ['High-frequency','real-time tasks']
            for j,line in enumerate(lines):p.append(f'<text x="{x}" y="{y+107+j*29}" text-anchor="middle" font-size="{24 if lang=="zh" else 22}" font-weight="500" fill="{INK}">{escape(line)}</text>')
            if row==1 and i==2:p.append(f'<text x="{x}" y="{y+140}" text-anchor="middle" font-size="21" fill="{GOLD}">{"（极少样本）" if lang=="zh" else "Very few samples"}</text>')
            if i<4:p.append(f'<path d="M{x+108} {y}H{x+190}" stroke="#788695" stroke-width="2.7" marker-end="url(#arrow)"/>')
    p.append('</g></svg>')
    (ROOT/f'concept_{lang}.svg').write_text(''.join(p))
