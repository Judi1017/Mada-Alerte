import json,time,os,datetime as D,urllib.request as U,urllib.parse as P_,numpy as np,pandas as pd
from rich.progress import Progress,SpinnerColumn,TextColumn,BarColumn,MofNCompleteColumn,TimeElapsedColumn
from src.b import C,I
V=[('Antananarivo',-18.910,47.525),('Toamasina',-18.155,49.410),('Mahajanga',-15.717,46.317),('Toliara',-23.350,43.667),('Antsiranana',-12.279,49.292),('Fianarantsoa',-21.454,47.086),('Antsirabe',-19.867,47.033),('Morondava',-20.283,44.283),('Sambava',-14.264,50.168),('Taolagnaro',-25.032,46.990),('Maroantsetra',-15.433,49.744),('Manakara',-22.145,48.017)]
K='temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max,wind_gusts_10m_max,shortwave_radiation_sum'
N=dict(temperature_2m_max='tmax',temperature_2m_min='tmin',temperature_2m_mean='tmoy',precipitation_sum='pluie',wind_speed_10m_max='vent',wind_gusts_10m_max='raf',shortwave_radiation_sum='ray')
H1=os.environ.get('MADA_ARCH','https://archive-api.open-meteo.com/v1/archive');H2=os.environ.get('MADA_PREV','https://api.open-meteo.com/v1/forecast')
def q(u,p,r=5):
 for i in range(r):
  try:
   with U.urlopen(u+'?'+P_.urlencode(p),timeout=90) as x:return json.load(x)
  except Exception as e:
   if i==r-1:raise
   time.sleep(65 if getattr(e,'code',0)==429 else 3*(i+1))
def j(o,v):
 d=pd.DataFrame(o['daily']).rename(columns={'time':'date'}).rename(columns=N);d['date']=pd.to_datetime(d['date']);d['ville']=v[0];d['lat']=v[1];d['lon']=v[2];d['alt']=o.get('elevation',np.nan);return d
def g(R_,a='2012-01-01'):
 e=(D.date.today()-D.timedelta(days=10)).isoformat();(R_/'data/raw').mkdir(parents=True,exist_ok=True);L=[]
 with Progress(SpinnerColumn('line',style='cyan'),TextColumn('[bold]{task.description:<24}'),BarColumn(bar_width=32,complete_style='cyan',finished_style='green'),MofNCompleteColumn(),TimeElapsedColumn(),console=C) as P:
  t=P.add_task('',total=len(V))
  for v in V:
   f=R_/'data/raw'/f'{v[0].lower()}.csv';P.update(t,description=f'{I["rn"]} {v[0]}')
   if f.exists():d=pd.read_csv(f,parse_dates=['date'])
   else:d=j(q(H1,dict(latitude=v[1],longitude=v[2],start_date=a,end_date=e,daily=K,timezone='auto')),v);d.to_csv(f,index=False);time.sleep(1)
   L.append(d);P.advance(t)
  P.update(t,description=f'{I["ok"]} terminé')
 return pd.concat(L,ignore_index=True)
def w(v,fin=None):
 if fin:e=pd.Timestamp(fin);o=q(H1,dict(latitude=v[1],longitude=v[2],start_date=(e-pd.Timedelta(days=40)).strftime('%Y-%m-%d'),end_date=(e+pd.Timedelta(days=1)).strftime('%Y-%m-%d'),daily=K,timezone='auto'))
 else:o=q(H2,dict(latitude=v[1],longitude=v[2],past_days=40,forecast_days=1,daily=K,timezone='auto'))
 return j(o,v)
def n(d):
 k=len(d);d=d.drop_duplicates(['ville','date']).copy();c=['tmax','tmin','tmoy','vent','raf','ray']
 for x in c+['pluie']:d[x]=pd.to_numeric(d[x],errors='coerce')
 d=d.sort_values(['ville','date']);d.loc[d.pluie<0,'pluie']=0;d=d[d.pluie.notna()].copy()
 for x in c:d[x]=d.groupby('ville')[x].transform(lambda s:s.interpolate(limit=3,limit_direction='both'))
 d=d.dropna(subset=c);d=d[d.tmin<=d.tmax];return d.reset_index(drop=True),k-len(d)
