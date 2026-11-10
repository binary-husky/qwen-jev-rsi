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
# Two aligned panels mirror the visual language of the main framework figure.
rect(35,35,650,805,'#F3F8FC','#B8D1E5',14,1.2,z=0)
rect(760,35,805,805,'#FCFAF6','#E4D3BA',14,1.2,z=0)
txt(65,70,'Policy',18,BLUE,'bold',ha='left')
txt(790,70,'Iterative JEV improvement',18,GOLD,'bold',ha='left')
# Preserve the actual reference artwork; a frame stack is already embedded in it.
im=Image.open(OUT/'reference-screen-0.png')
rect(215,105,290,214,'white','#A8BACB',9,1.3)
ax.imshow(im,extent=(225,495,309,115),zorder=5,aspect='auto')
txt(360,345,'Current screen + 4 history frames',14,weight='bold')
txt(360,370,'Visual input',10.5,MUTED)
arrow([(360,387),(360,421)],BLUE)
rect(90,421,540,125,'#E7F4F0',TEAL,10,1.5)
network(117,448,88,48)
txt(238,447,'JEV feature output',14,TEAL,'bold',ha='left')
txt(238,482,'Ticks until hit',13,ha='left')
txt(238,518,'Heavy-attack energy',13,ha='left')
arrow([(360,546),(360,594)],BLUE)
rect(90,594,540,171,'#EDF2F8','#B9CDDF',10,1.3)
txt(360,620,'Behavior tree',15,weight='bold')
# Branching icon followed by equal-sized action leaves.
line([(360,639),(360,662),(190,662),(190,689)],BLUE,1.6)
line([(360,662),(530,662),(530,689)],BLUE,1.6)
line([(360,662),(360,689)],BLUE,1.6)
for xx,label in [(110,'Dodge'),(280,'Attack'),(450,'Heavy attack')]:
    node(xx,690,160,48,label,color=BLUE,fill='white',size=12)
txt(360,802,'Visual perception → features → control actions',11,MUTED)
# Model lifecycle and experience flow, with separate init and update ports.
node(1040,112,250,76,'wk-rsi-base','Initialization',TEAL,'#E7F4F0',12)
node(1040,224,250,76,'wk-rsi-v{k}','Model at iteration k',TEAL,'#E7F4F0',12)
node(1000,343,330,76,'20 episodes','Collect interaction experience',BLUE,'#EDF4FA',15)
node(1000,462,330,76,'Hit-prediction labels','Supervision from collected experience',PURPLE,'#EEE5F7',15)
node(1040,581,250,76,'LoRA SFT','Supervised fine-tuning',GOLD,'#FFF2DF',15)
node(1040,700,250,76,'wk-rsi-v{k+1}','Model at iteration k + 1',TEAL,'#E7F4F0',12)
for y1,y2 in [(188,224),(300,343),(419,462),(538,581),(657,700)]:
    arrow([(1165,y1),(1165,y2)],TEAL if y1==188 else GOLD)
# Policy supplies the rollout; route in the gap between the two panels.
arrow([(630,653),(715,653),(715,381),(1000,381)],BLUE)
rect(788,359,170,38,'#FCFAF6',radius=4,z=3)
txt(873,377,'Apply policy',11,BLUE,'bold')
# Feedback is an explicit promotion of the new model, not a merge into Base JEV.
arrow([(1290,738),(1470,738),(1470,262),(1290,262)],TEAL,True,2)
rect(1365,557,169,71,'#FCFAF6',radius=4,z=3)
txt(1449,579,'Next iteration',12,TEAL,'bold')
txt(1449,607,'Update JEV',10.5,MUTED)
txt(1165,805,'Repeat experience collection and model refinement',10.5,MUTED)
txt(45,873,'Blue: policy / interaction    Purple: labels    Amber: training    Teal: JEV / model update',10,MUTED,ha='left')
txt(1550,873,'Game image retained from the supplied reference',9,MUTED,ha='right')
for ext in ('svg','pdf','png'):
    fig.savefig(OUT/f'jev_iteration.{ext}',dpi=220,facecolor='white')
plt.close(fig)
print('Rendered Figure 2: SVG / PDF / PNG')
