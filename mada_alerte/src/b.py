import os,sys,time
from rich.console import Console,Group
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.live import Live
from rich import box
A='Judicaël';E='...49@gmail.com'
try:sys.stdout.reconfigure(encoding='utf-8')
except Exception:pass
C=Console(highlight=False)
I=dict(ok='[OK]',ko='[X]',go='>',st='*',al='!',rn='~',sn='o',pc='#',ma='@') if os.environ.get('MADA_PLAIN') else dict(ok='✔',ko='✖',go='►',st='★',al='⚡',rn='☂',sn='☀',pc='◆',ma='✉')
def G(s,a=(0,210,255),b=(255,90,200),w='bold'):
 t=Text();n=max(len(s)-1,1)
 for i,x in enumerate(s):t.append(x,style='%s rgb(%d,%d,%d)'%((w,)+tuple(int(p+(q-p)*i/n) for p,q in zip(a,b))))
 return t
def B():
 L=[G(f'{I["rn"]}  M A D A - A L E R T E  {I["al"]}'),Text("Alerte précoce des fortes pluies · Madagascar",style='italic white'),Text(''),Text.assemble((f'{I["st"]} Projet réalisé par ',''),(A,'bold yellow')),Text.assemble((f'{I["ma"]}  Email : ',''),(E,'underline cyan'))]
 with Live(console=C,refresh_per_second=30) as v:
  for k in range(1,len(L)+1):v.update(Panel(Align.center(Group(*L[:k])),box=box.DOUBLE,border_style='cyan',padding=(1,4),width=64));time.sleep(.3)
 C.print()
def S(i,n,t):C.print();C.rule(f'[bold cyan]{I["go"]} ÉTAPE {i}/{n}[/]  [white]{t}[/]',style='cyan')
def O(t):C.print(f'  [bold green]{I["ok"]}[/] {t}')
def K(t):C.print(f'  [bold red]{I["ko"]}[/] {t}')
def W(t,f,*a,**k):
 with C.status('[cyan]'+t,spinner='bouncingBar'):return f(*a,**k)
def T(s,c='cyan',d=.015):
 for i in range(len(s)+1):C.print(Text(s[:i],style=c),end='\r');time.sleep(d)
 C.print(Text(s,style=c))
