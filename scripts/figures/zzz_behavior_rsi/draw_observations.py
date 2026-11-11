"""Regenerate the cross-opponent controller figure from audited display data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
root=Path(__file__).parent;data=json.loads((root/'observations.json').read_text());rows=data['rows']
fig,(ax,notes)=plt.subplots(1,2,figsize=(14,6.6),gridspec_kw={'width_ratios':[1.4,1]},layout='constrained')
for i,r in enumerate(rows):
 for key,off,color,lab in [('baseline_completed_s',-.12,'#657c96','Baseline controller (a6ad1ad)'),('revised_completed_s',.12,'#13877b','zzz-rsi-v3 controller (a3e7b6d)')]:
  vals=r[key]
  for k,value in enumerate(vals):ax.scatter(value,i+off+(k-(len(vals)-1)/2)*.032,s=40,color=color,label=lab if i==0 and k==0 else None,zorder=3)
 def status(vals,unfinished,invalid=0):
  if unfinished is None:return 'untested'
  parts=[f'{len(vals)} completed'] if vals else []
  if unfinished:parts.append(f'{unfinished} unfinished')
  if invalid:parts.append(f'{invalid} invalid')
  return ', '.join(parts)
 note=status(r['baseline_completed_s'],r['baseline_unfinished'])+' / '+status(r['revised_completed_s'],r['revised_unfinished'],r['revised_invalid'])
 notes.text(0,i,note,va='center',fontsize=9,color='#39424b')
ax.set(yticks=range(len(rows)),yticklabels=[r['opponent'] for r in rows],ylim=(8.6,-.7),xlim=(145,325),xlabel='In-game completion time (s); lower is shorter')
ax.grid(axis='x',alpha=.2);ax.spines[['top','right']].set_visible(False);ax.legend(loc='lower right',fontsize=8)
notes.set(ylim=(8.6,-.7),xlim=(0,1));notes.axis('off');notes.set_title('Outcomes (baseline / revised controller)',loc='left',fontsize=10)
fig.suptitle('Cross-opponent controller evaluation',fontsize=14)
fig.supxlabel('Each dot is a completed episode; unpaired observations. Non-completions have no numerical completion time.\nQuestion sets and behavior trees differ. Shared model weights have not been independently verified.',fontsize=9)
for ext in ['svg','png','pdf']:fig.savefig(root/('observations.'+ext),dpi=180)
