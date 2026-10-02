import argparse as A_,time,joblib,pandas as pd
from pathlib import Path as P
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from src.b import C,I,A,E,B,K,W,T
from src.d import V,w,n
from src.p import f,y
R=P(__file__).resolve().parent;p=A_.ArgumentParser();p.add_argument('--ville',default='Toamasina');p.add_argument('--date',default=None);a=p.parse_args();B()
v=next((x for x in V if x[0].lower()==a.ville.strip().lower()),None);v or exit('Villes possibles : '+', '.join(x[0] for x in V))
M=joblib.load(R/'models/mada_alerte.joblib')
try:d=W(f'récupération météo réelle · {v[0]} {"("+a.date+")" if a.date else "(en direct)"}…',lambda:y(f(n(w(v,a.date))[0])))
except Exception as x:exit(K('Connexion Open-Meteo impossible : '+str(x)[:90]))
r=d[d.date==pd.Timestamp(a.date)] if a.date else d.iloc[[-1]]
(r.empty or r[M['fx']].isna().any(axis=None)) and exit(K('Pas assez de données pour cette date (essayez une date plus ancienne).'))
q=float(M['m'].predict_proba(r[M['fx']])[0,1]);th=M['th'];c='green' if q<th*.6 else 'yellow' if q<th else 'red';nv='FAIBLE' if c=='green' else 'MODÉRÉ' if c=='yellow' else 'ÉLEVÉ';z=r.iloc[0];N_=28
with Live(console=C,refresh_per_second=40) as lv:
 for i in range(int(q*N_)+1):lv.update(Text.assemble((f'  {I["rn"]} Risque J+1 ≥ {M["seuil"]:.0f} mm  ','bold white'),('█'*i,c),('░'*(N_-i),'grey37'),(f'  {i/N_:.0%}',f'bold {c}')));time.sleep(.025)
 lv.update(Text.assemble((f'  {I["rn"]} Risque J+1 ≥ {M["seuil"]:.0f} mm  ','bold white'),('█'*int(q*N_),c),('░'*(N_-int(q*N_)),'grey37'),(f'  {q:.1%}',f'bold {c}')))
t=Table(box=box.ROUNDED,header_style='bold magenta',title=f'{I["sn"]} Conditions · {v[0]} · {z.date:%d/%m/%Y}');[t.add_column(k,justify='right') for k in['Jour','Σ 3 j','Σ 7 j','Σ 30 j','T° moy','Vent','Rafales']];t.add_row(f'{z.pluie:.1f} mm',f'{z.c3:.0f} mm',f'{z.c7:.0f} mm',f'{z.c30:.0f} mm',f'{z.tmoy:.1f} °C',f'{z.vent:.0f} km/h',f'{z.raf:.0f} km/h');C.print();C.print(t)
ic=I['al'] if c=='red' else I['rn'] if c=='yellow' else I['ok'];act=''
if a.date:
 k=d.loc[d.date==pd.Timestamp(a.date)+pd.Timedelta(days=1),'pluie']
 act=f'\n[white]Réalité le lendemain :[/] [bold]{k.iloc[0]:.1f} mm[/] ' + (f'[green]{I["ok"]} alerte justifiée[/]' if k.iloc[0]>=M['seuil'] and q>=th else f'[green]{I["ok"]} cohérent[/]' if (k.iloc[0]>=M['seuil'])==(q>=th) else f'[red]{I["ko"]} le modèle s\'est trompé[/]') if len(k) else '\n[dim]Réalité du lendemain pas encore disponible.[/]'
C.print(Panel(f'[bold {c}]{ic}  NIVEAU {nv}[/]   [white]· seuil d\'alerte du modèle : {th:.0%}[/]'+act+f'\n\n[dim]{I["st"]} Projet réalisé par {A} · {E}[/]',box=box.DOUBLE,border_style=c,padding=(1,3),width=78))
