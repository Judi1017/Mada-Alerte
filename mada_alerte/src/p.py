import json,joblib,numpy as np,pandas as pd,matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as L
from rich.table import Table
from rich.panel import Panel
from rich import box
from sklearn.pipeline import Pipeline as Q
from sklearn.impute import SimpleImputer as IM
from sklearn.preprocessing import StandardScaler as SS
from sklearn.linear_model import LogisticRegression as LR
from sklearn.ensemble import HistGradientBoostingClassifier as HG
from sklearn.inspection import permutation_importance as XI
from sklearn.metrics import average_precision_score as ap,roc_auc_score as ra,precision_recall_curve as pc,precision_score as ps,recall_score as rs,f1_score as fs,confusion_matrix as cm,ConfusionMatrixDisplay as CD
from src.b import C,I,A,E,B,S,O,K,W,T
from src.d import g,n
FX=['pluie','p1','p2','p3','c3','c7','c30','tmax','tmin','tmoy','dt','amp','vent','raf','rv','ray','ds','dc','lat','lon','alt']
SE=30.
def f(d):
 d=d.sort_values(['ville','date']).reset_index(drop=True);h=d.groupby('ville').pluie
 for k in(1,2,3):d[f'p{k}']=h.shift(k)
 for k in(3,7,30):d[f'c{k}']=h.transform(lambda s,k=k:s.rolling(k).sum())
 d['dt']=d.tmoy-d.groupby('ville').tmoy.transform(lambda s:s.rolling(7).mean());d['amp']=d.tmax-d.tmin;a=2*np.pi*d.date.dt.dayofyear/365.25;d['ds']=np.sin(a);d['dc']=np.cos(a);d['rv']=d.raf/(d.vent+1);return d
def y(d):
 h=d.groupby('ville');x=h.pluie.shift(-1);k=(h.date.shift(-1)-d.date).dt.days==1;d=d.copy();d['pn']=x.where(k);d['y']=(x>=SE).astype(float).where(k);return d
MD=dict(LR=lambda:Q([('i',IM(strategy='median')),('s',SS()),('m',LR(max_iter=800,class_weight='balanced'))]),HG=lambda:HG(max_iter=300,learning_rate=.06,max_depth=6,l2_regularization=1.,class_weight='balanced',random_state=7))
NM=dict(LR='Régression logistique',HG='HistGradientBoosting')
def m(R_):
 B();o=R_/'outputs';o.mkdir(exist_ok=True);(R_/'models').mkdir(exist_ok=True);(R_/'data/clean').mkdir(parents=True,exist_ok=True)
 S(1,6,'Collecte des données météo RÉELLES (Open-Meteo · ERA5)');r=g(R_);O(f'{len(r):,} lignes brutes · {r.ville.nunique()} villes · {r.date.min():%Y-%m-%d} → {r.date.max():%Y-%m-%d}')
 S(2,6,'Nettoyage');d,x=W('contrôle qualité…',n,r);O(f'{len(d):,} lignes propres · {x} rejetées (doublons, valeurs manquantes, incohérences)')
 S(3,6,'Préparation : variables météo glissantes');d=W('création des variables…',lambda:y(f(d)));e=d.dropna(subset=FX+['y']).reset_index(drop=True);e.to_csv(R_/'data/clean/meteo_mada_propre.csv',index=False);O(f'{len(e):,} exemples · {len(FX)} variables · alerte = pluie ≥ {SE:.0f} mm demain · taux {e.y.mean():.2%}')
 S(4,6,'Analyse exploratoire');q=e.groupby('ville').agg(jours=('y','size'),al=('y','sum'),tx=('y','mean'),mx=('pluie','max'),an=('pluie',lambda s:s.sum()/(len(s)/365.25))).sort_values('tx',ascending=False)
 t=Table(title=f'{I["rn"]} Jours d\'alerte par ville',box=box.ROUNDED,header_style='bold magenta')
 [t.add_column(c,justify='left' if i==0 else 'right') for i,c in enumerate(['Ville','Jours','Alertes','Taux','Pluie max (mm)','Pluie / an (mm)'])]
 for v,z in q.iterrows():t.add_row(v,f'{int(z.jours):,}',f'{int(z.al):,}',f'{z.tx:.1%}',f'{z.mx:.0f}',f'{z.an:.0f}')
 C.print(t)
 S(5,6,'Entraînement & évaluation (découpage temporel)');a=e[e.date<'2022-01-01'];v=e[(e.date>='2022-01-01')&(e.date<'2024-01-01')];t_=e[e.date>='2024-01-01'];O(f'train {len(a):,} (2012–2021) · validation {len(v):,} (2022–2023) · test {len(t_):,} (≥ 2024)');Z={};MO={}
 for k,fn in MD.items():
  with C.status(f'[cyan]entraînement {NM[k]}…',spinner='bouncingBar'):
   mo=fn().fit(a[FX],a.y);pv=mo.predict_proba(v[FX])[:,1];P1,R1,TH=pc(v.y,pv);th=float(TH[np.argmax((2*P1*R1/(P1+R1+1e-9))[:-1])]);pt=mo.predict_proba(t_[FX])[:,1]
  MO[k]=mo;Z[k]=dict(th=th,pt=pd.Series(pt,index=t_.index),roc=ra(t_.y,pt),ap=ap(t_.y,pt),p=ps(t_.y,pt>=th,zero_division=0),r=rs(t_.y,pt>=th),f=fs(t_.y,pt>=th));O(f'{NM[k]} entraîné · seuil d\'alerte {th:.2f}')
 bp=t_.pluie>=SE;bf=max(Z,key=lambda k:Z[k]['f']);tb=Table(title=f'{I["pc"]} Résultats sur le TEST (données jamais vues)',box=box.ROUNDED,header_style='bold magenta')
 [tb.add_column(c,justify='left' if i==0 else 'right') for i,c in enumerate(['Modèle','ROC-AUC','PR-AUC','Précision','Rappel','F1'])]
 tb.add_row('Hasard (taux d\'événement)','0.500',f'{t_.y.mean():.3f}','-','-','-');tb.add_row('Persistance (pluie ≥ 30 mm aujourd\'hui)','-','-',f'{ps(t_.y,bp,zero_division=0):.3f}',f'{rs(t_.y,bp):.3f}',f'{fs(t_.y,bp):.3f}')
 for k,z in Z.items():tb.add_row(NM[k],f'{z["roc"]:.3f}',f'{z["ap"]:.3f}',f'{z["p"]:.3f}',f'{z["r"]:.3f}',f'[bold green]{z["f"]:.3f}[/]' if k==bf else f'{z["f"]:.3f}')
 C.print(tb)
 S(6,6,'Graphiques & sauvegarde')
 def pl():
  fg,ax=L.subplots(2,3,figsize=(19,10));ax=ax.ravel();mm=e.assign(mo=e.date.dt.month).groupby('mo').y.sum();ax[0].bar(mm.index,mm.values,color='#2471a3');ax[0].set_xticks(range(1,13));ax[0].set_title('Jours d\'alerte par mois (saison cyclonique)')
  ax[1].barh(q.index[::-1],q.tx.values[::-1]*100,color='#c0392b');ax[1].set_title('Taux de jours d\'alerte par ville (%)')
  for k,z in Z.items():P2,R2,_=pc(t_.y,z['pt']);ax[2].plot(R2,P2,label=f'{NM[k]} (PR-AUC {z["ap"]:.2f})')
  ax[2].axhline(t_.y.mean(),ls='--',c='k',label='Hasard');ax[2].set_xlabel('Rappel');ax[2].set_ylabel('Précision');ax[2].legend(fontsize=8);ax[2].set_title('Courbe précision–rappel (test)')
  CD(cm(t_.y,Z[bf]['pt']>=Z[bf]['th']),display_labels=['Calme','Alerte']).plot(ax=ax[3],colorbar=False);ax[3].set_title(f'Matrice de confusion – {NM[bf]}')
  s=t_.sample(min(4000,len(t_)),random_state=7);pi=XI(MO[bf],s[FX],s.y,n_repeats=3,scoring='average_precision',random_state=7,n_jobs=-1);kk=pd.Series(pi.importances_mean,index=FX).sort_values().tail(10);ax[4].barh(kk.index,kk.values,color='#27ae60');ax[4].set_title('Variables les plus utiles (permutation)')
  cv=t_.groupby('ville').y.sum().idxmax();kt=t_[t_.ville==cv].sort_values('date');ax[5].plot(kt.date,Z[bf]['pt'][kt.index],lw=.8,c='#2471a3',label='Risque prédit');ax[5].vlines(kt.date[kt.y==1],0,1,color='r',alpha=.35,label='Alerte réelle (J+1)');ax[5].axhline(Z[bf]['th'],ls='--',c='k');ax[5].legend(fontsize=8);ax[5].set_title(f'{cv} – risque prédit vs réalité (test)')
  fg.suptitle('MADA-ALERTE · fortes pluies J+1 · Madagascar (Open-Meteo / ERA5)',fontsize=15);fg.text(.5,.005,f'Projet réalisé par {A}  ·  {E}',ha='center',fontsize=10);L.tight_layout(rect=(0,.02,1,.96));fg.savefig(o/'analyse_et_resultats.png',dpi=110);L.close('all')
 W('dessin des graphiques…',pl);O('outputs/analyse_et_resultats.png')
 J=dict(auteur=A,email=E,seuil_mm=SE,n_exemples=len(e),n_villes=int(e.ville.nunique()),periode=[str(e.date.min().date()),str(e.date.max().date())],taux_alerte=round(float(e.y.mean()),4),test={k:dict(seuil=round(z['th'],3),roc_auc=round(float(z['roc']),4),pr_auc=round(float(z['ap']),4),precision=round(float(z['p']),4),rappel=round(float(z['r']),4),f1=round(float(z['f']),4)) for k,z in Z.items()},persistance=dict(precision=round(float(ps(t_.y,bp,zero_division=0)),4),rappel=round(float(rs(t_.y,bp)),4),f1=round(float(fs(t_.y,bp)),4)),hasard_pr_auc=round(float(t_.y.mean()),4))
 json.dump(J,open(o/'metrics.json','w'),indent=1,ensure_ascii=False);O('outputs/metrics.json')
 fm=W('modèle final (toutes les données)…',lambda:MD[bf]().fit(e[FX],e.y));joblib.dump(dict(m=fm,th=Z[bf]['th'],fx=FX,seuil=SE,nom=NM[bf]),R_/'models/mada_alerte.joblib');O('models/mada_alerte.joblib')
 C.print();C.print(Panel(f'[bold green]{I["ok"]} PIPELINE TERMINÉ[/]\n\n[white]Meilleur modèle :[/] [bold]{NM[bf]}[/]   [white]F1 test :[/] [bold yellow]{Z[bf]["f"]:.3f}[/]   [white]PR-AUC :[/] [bold yellow]{Z[bf]["ap"]:.3f}[/]\n\n{I["rn"]} Essayez : [cyan]python predict.py --ville Toamasina[/]\n{I["al"]} Ou rejouez un jour : [cyan]python predict.py --ville Toamasina --date 2025-02-10[/]\n\n[dim]{I["st"]} Projet réalisé par {A} · {E}[/]',box=box.DOUBLE,border_style='green',padding=(1,3),width=78))
