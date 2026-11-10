"""Editable vector artwork: semantic miniatures instead of text-only boxes."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Ellipse, PathPatch
from matplotlib.path import Path as MplPath

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans', 'svg.fonttype':'none', 'pdf.fonttype':42})
fig, ax = plt.subplots(figsize=(16,9))
fig.subplots_adjust(0,0,1,1)
ax.set(xlim=(0,1600),ylim=(900,0)); ax.axis('off')
INK='#243449'; MUTED='#6A7787'; BLUE='#3978B7'; TEAL='#07878A'; GOLD='#BD7B2F'; PURPLE='#8B6CB0'

def txt(x,y,s,size=13,color=INK,weight='normal',ha='center',**kw):
    ax.text(x,y,s,fontsize=size,color=color,fontweight=weight,ha=ha,va='center',zorder=8,**kw)

def rect(x,y,w,h,fill='white',stroke='none',radius=10,lw=1.3,dash=False,z=3):
    p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={radius}',
        facecolor=fill,edgecolor=stroke,linewidth=lw,linestyle=(0,(4,3)) if dash else '-',zorder=z)
    ax.add_patch(p); return p

def line(points,color=BLUE,lw=1.8,dash=False,z=4):
    ax.plot(*zip(*points),color=color,lw=lw,linestyle=(0,(4,3)) if dash else '-',
            solid_capstyle='round',zorder=z)

def arrow(points,color=BLUE,dash=False,lw=1.8):
    if len(points)>2: line(points[:-1],color,lw,dash,z=2)
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=14,
       linewidth=lw,color=color,linestyle=(0,(4,3)) if dash else '-',shrinkA=0,shrinkB=2,zorder=2))

def dot(x,y,r,color,edge='none',z=5):
    ax.add_patch(Circle((x,y),r,facecolor=color,edgecolor=edge,linewidth=1.3,zorder=z))

def scene(x,y,w,h):
    # Snake-style illustration; no claim that this is a captured game frame.
    rect(x,y,w,h,'#F0F6EC',radius=4,z=5)
    cell=min(w/12,h/8)
    gx=x+(w-12*cell)/2; gy=y+(h-8*cell)/2
    for k in range(13): line([(gx+k*cell,gy),(gx+k*cell,gy+8*cell)],'#DCE7D6',.45,z=5)
    for k in range(9): line([(gx,gy+k*cell),(gx+12*cell,gy+k*cell)],'#DCE7D6',.45,z=5)
    body=[(2,6),(3,6),(4,6),(4,5),(4,4),(5,4),(6,4),(7,4)]
    for i,(cx,cy) in enumerate(body):
        rect(gx+cx*cell+.5,gy+cy*cell+.5,cell-1,cell-1,
             '#226F45' if i==len(body)-1 else '#62A862',radius=cell*.16,z=6)
    for ey in (.28,.72):
        dot(gx+7.73*cell,gy+(4+ey)*cell,cell*.10,'#FFFFFF',z=7)
        dot(gx+7.77*cell,gy+(4+ey)*cell,cell*.045,'#193B2A',z=8)
    dot(gx+10.4*cell,gy+4.5*cell,cell*.35,'#E56751',z=7)
    line([(gx+10.4*cell,gy+4.2*cell),(gx+10.55*cell,gy+3.95*cell)],'#417848',1.2,z=7)

def monitor(x,y,w,h):
    rect(x,y,w,h,'#FFFFFF','#8FA8BE',7,1.6)
    scene(x+7,y+7,w-14,h-18)
    line([(x+w/2,y+h),(x+w/2,y+h+10)],'#8FA8BE',2.5)
    line([(x+w*.34,y+h+11),(x+w*.66,y+h+11)],'#8FA8BE',2.5)

def network(x,y,w=125,h=58,color=TEAL):
    cols=[[y+8,y+h/2,y+h-8],[y,y+h/3,y+2*h/3,y+h],[y+10,y+h-10]]
    xs=[x,x+w/2,x+w]
    for i in range(2):
        for a in cols[i]:
            for b in cols[i+1]: line([(xs[i],a),(xs[i+1],b)],'#ACD8D5',1,z=5)
    for xx,ys in zip(xs,cols):
        for yy in ys: dot(xx,yy,5.5,'#FFFFFF',color,z=6)

def film(x,y,w=145,h=83):
    for off in (16,8,0):
        rect(x+off,y-off,w,h,'#FFFFFF','#A8BACB',5,z=4)
        scene(x+off+6,y-off+6,w-12,h-12)

def database(x,y,w=130,h=83):
    ax.add_patch(Rectangle((x,y+12),w,h-24,facecolor='#F7E7CD',edgecolor=GOLD,lw=1.3,zorder=5))
    for yy in (y+h-12,y+h*.56,y+12):
        ax.add_patch(Ellipse((x+w/2,yy),w,25,facecolor='#FFF5E5',edgecolor=GOLD,lw=1.3,zorder=6))
    txt(x+w/2,y+44,'v1  v2  …',11,GOLD)

def document(x,y,w=80,h=78,color=GOLD):
    rect(x,y,w,h,'#FFFFFF',color,6,z=5)
    for i,ww in enumerate((.6,.45,.6)):
        line([(x+15,y+18+i*18),(x+15+w*ww,y+18+i*18)],color,2,z=6)

def node(x,y,w,h,title,sub='',color=BLUE,fill='white',size=14):
    rect(x,y,w,h,fill,color,10,1.5)
    txt(x+w/2,y+h/2-(11 if sub else 0),title,size,color,'bold')
    if sub: txt(x+w/2,y+h/2+17,sub,10,MUTED)

from PIL import Image
rect(35,35,650,805,'#F3F8FC','#B8D1E5',14,1.2,z=0)
rect(760,35,805,805,'#FCFAF6','#E4D3BA',14,1.2,z=0)
txt(65,70,'Policy',18,BLUE,'bold',ha='left')
txt(790,70,'Iterative JEV improvement',18,GOLD,'bold',ha='left')
im=Image.open(OUT/'reference-screen.jpg')
rect(190,103,340,200,'white','#A8BACB',9,1.3)
ax.imshow(im,extent=(200,520,293,113),zorder=5,aspect='auto')
txt(360,327,'Main screen',14,weight='bold')
txt(360,351,'Visual input',10.5,MUTED)
arrow([(360,370),(360,397)],BLUE)
rect(90,397,540,172,'#E7F4F0',TEAL,10,1.5)
network(117,451,78,55)
txt(225,423,'JEV feature output',14,TEAL,'bold',ha='left')
for y,label in [(456,'Combat state'),(485,'Skill and ultimate state'),(514,'Current player'),(543,'Attack prediction')]:
    dot(229,y,3.1,TEAL);txt(245,y,label,12.5,ha='left')
arrow([(360,569),(360,603)],BLUE)
rect(90,603,540,183,'#EDF2F8','#B9CDDF',10,1.3)
txt(360,627,'Behavior tree',15,weight='bold')
line([(360,645),(360,658),(190,658),(190,673)],BLUE,1.6)
line([(360,658),(530,658),(530,673)],BLUE,1.6)
line([(360,658),(360,673)],BLUE,1.6)
for xx,labels in [(110,('Special','Ultimate')),(280,('Movement','Dodge')),(450,('Switch player','Normal attack'))]:
    for yy,label in zip((674,731),labels):
        node(xx,yy,160,42,label,color=BLUE,fill='white',size=10.5)
txt(530,704,'(Counter)',7.8,MUTED)
txt(360,812,'Visual perception → features → control actions',11,MUTED)
node(1040,112,250,76,'zzz-rsi-base','Initialization',TEAL,'#E7F4F0',12)
node(1040,224,250,76,'zzz-rsi-v{k}','Model at iteration k',TEAL,'#E7F4F0',12)
node(1000,343,330,76,'5 episodes','Collect interaction experience',BLUE,'#EDF4FA',15)
node(1000,462,330,76,'Attack-prediction labels','Supervision from collected experience',PURPLE,'#EEE5F7',14)
node(1040,581,250,76,'LoRA SFT','Supervised fine-tuning',GOLD,'#FFF2DF',15)
node(1040,700,250,76,'zzz-rsi-v{k+1}','Model at iteration k + 1',TEAL,'#E7F4F0',12)
for y1,y2 in [(188,224),(300,343),(419,462),(538,581),(657,700)]:
    arrow([(1165,y1),(1165,y2)],TEAL if y1==188 else GOLD)
arrow([(630,645),(715,645),(715,381),(1000,381)],BLUE)
rect(788,359,170,38,'#FCFAF6',radius=4,z=3)
txt(873,377,'Apply policy',11,BLUE,'bold')
arrow([(1290,738),(1470,738),(1470,262),(1290,262)],TEAL,True,2)
rect(1365,550,169,85,'#FCFAF6',radius=4,z=3)
txt(1449,575,'Iteration ×2',12,TEAL,'bold')
txt(1449,605,'Update JEV',10.5,MUTED)
txt(1165,805,'Repeat experience collection and model refinement',10.5,MUTED)
txt(45,873,'Blue: policy / interaction    Purple: labels    Amber: training    Teal: JEV / model update',10,MUTED,ha='left')
txt(1550,873,'Game image retained from the supplied reference',9,MUTED,ha='right')
for ext in ('svg','pdf','png'):
    fig.savefig(OUT/f'zzz_iteration.{ext}',dpi=220,facecolor='white')
plt.close(fig)
print('Rendered ZZZ iteration: SVG / PDF / PNG')
