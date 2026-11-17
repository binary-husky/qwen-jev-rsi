"""Draw bilingual, editable SVG timing diagrams; ideal timing, not a benchmark."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent

def draw(lang):
    zh = lang == 'zh'
    def tr(a,b): return a if zh else b
    a=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 850" role="img" aria-labelledby="title desc">',
       '<title id="title">'+tr('错峰推理与独立执行','Staggered inference and independent execution')+'</title>',
       '<desc id="desc">'+tr('三个推理线程错峰读取最新画面，结果依次交给决策与动作线程。理想结果间隔为 L/3，单次推理耗时仍为 L。','Three inference workers read fresh frames at staggered starts. Results feed one decision worker and one action worker. Ideal result spacing is L/3; each inference still takes L.')+'</desc>',
       '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#718096" stroke-width="1.2"/></marker></defs>',
       '<rect width="1400" height="850" fill="white"/><g font-family="Arial,Noto Sans CJK SC,Microsoft YaHei,sans-serif" fill="#344153">']
    def text(x,y,s,size=20,fill='#344153',anchor='start'):
        a.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')
    def line(x1,y1,x2,y2,color='#dce2e8',dash=False,arrow=False):
        a.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="1.6"'+(' stroke-dasharray="5 5"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def rect(x,y,w,h,fill,stroke='none',r=5):a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
    text(34,42,tr('错峰推理与独立执行','Staggered inference and independent execution'),28)
    text(34,76,tr('n = 3 的理想时序示意；L 为一次完整推理周期','Idealized timing with n = 3; L is one complete inference cycle'),19,'#697582')
    x0=230; unit=405
    def x(t):return x0+unit*t
    labels=[tr('画面采集','Frame capture'),tr('推理线程 0','Inference worker 0'),tr('推理线程 1','Inference worker 1'),tr('推理线程 2','Inference worker 2'),tr('策略决策','Policy decision'),tr('动作执行','Action execution')]
    ys=[166,246,326,406,486,566]
    for i,(label,y) in enumerate(zip(labels,ys)):
        rect(24,y-28,1348,62,'#f5f7fa' if i%2==0 else '#fafbfc',r=0)
        text(42,y+8,label,20)
    for t,label in [(0,'0'),(1/3,'L/3'),(2/3,'2L/3'),(1,'L'),(4/3,'4L/3'),(5/3,'5L/3'),(2,'2L'),(8/3,'8L/3')]:
        line(x(t),115,x(t),601,dash=True)
        text(x(t),108,label,17,'#697582','middle')
    text(1370,132,tr('时间','Time'),17,'#697582','end')
    for k in range(33):rect(x(k/12),153,9,25,'#a8b5c3',r=2)
    text(x(1.9),141,tr('持续更新共享画面','Shared frames keep updating'),17,'#697582')
    colors=['#4c6982','#409b98','#8056b3']
    # Show two cycles per worker; the second cycle is muted for visual hierarchy.
    for i in range(3):
        y=ys[i+1];start=i/3
        for cycle in range(2):
            st=start+cycle
            rect(x(st),y-16,unit-7,33,colors[i] if cycle==0 else '#e2e7ed')
            text(x(st)+unit/2-4,y+7,tr('推理','Inference')+('  ·  L' if cycle==0 else ''),18,'white' if cycle==0 else '#697582','middle')
        line(x(start),184,x(start),y-19,'#718096',dash=True,arrow=True)
        a.append(f'<circle cx="{x(start)}" cy="{y-17}" r="4" fill="{colors[i]}"/>')
        end=x(start+1)
        line(end,y+18,end,467,colors[i],arrow=True)
        rect(end,472,26,28,colors[i])
        line(end+26,502,end+26,548,colors[i],arrow=True)
        rect(end+26,552,61,28,colors[i])
    # Actual execution completion is fed back to the decision worker.
    a.append(f'<path d="M{x(1)+87},582 L{x(1)+106},582 L{x(1)+106},508" fill="none" stroke="#718096" stroke-width="1.6" stroke-dasharray="5 5" marker-end="url(#arrow)"/>')
    text(x(1)+112,536,tr('回执','Receipt'),16,'#697582')
    line(x(1),619,x(4/3),619,'#718096')
    line(x(1),612,x(1),626,'#718096');line(x(4/3),612,x(4/3),626,'#718096')
    text((x(1)+x(4/3))/2,647,tr('结果间隔 ≈ L/3','Result spacing ≈ L/3'),19,'#344153','middle')
    text(34,640,tr('启动时读取最新画面与历史帧','Read fresh frames at each start'),19)
    cards=[
        (tr('限制积压','Bound the backlog'),tr('新调度覆盖旧调度；错过时刻则跳过。','Replace pending schedules; skip missed starts.'),tr('动作队列满时丢弃最早等待的动作。','Drop the oldest queued action when full.')),
        (tr('按到达顺序决策','Decide on arrival'),tr('结果允许乱序返回，无需等待早期请求。','Results may finish out of order.'),tr('决策与动作各由一个线程串行处理。','Decisions and actions each use one worker.')),
        (tr('分别测量延迟','Measure distinct timings'),tr('推理周期、决策间隔、观测至动作完成。','Inference, decision spacing, observation-to-action.'),tr('主推理线程超出延迟预算时停止运行。','Stop on a lead-worker latency-budget breach.'))]
    for i,(title,l1,l2) in enumerate(cards):
        xx=24+i*456;rect(xx,687,440,130,'#f5f7fa')
        text(xx+17,719,title,21);text(xx+17,753,l1,16);text(xx+17,783,l2,16)
    a.append('</g></svg>')
    (OUT/f'latency_swimlanes_{lang}.svg').write_text('\n'.join(a))

if __name__=='__main__':
    for lang in ['zh','en']:draw(lang)
