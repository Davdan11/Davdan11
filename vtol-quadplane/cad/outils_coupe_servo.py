"""Dessine la coupe de l'aile au droit du servo d'aileron : python outils_coupe_servo.py image.png"""
import sys, math; sys.path.insert(0,'.')
import numpy as np, trimesh, pieces as P, build as B
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Rectangle
from params import *
i=P.segments_aileron()[0]; yc=P.Y_GUIGNOL_AILERON
def coupe(wp, y):
    m=B.vers_trimesh(wp,0.05); s=m.section([0,1,0],[0,y,0])
    return [] if s is None else [e for e in s.discrete]
a=math.radians(CALAGE_AILE)
def R(x,z): return x*math.cos(a)+z*math.sin(a), -x*math.sin(a)+z*math.cos(a)
fig,ax=plt.subplots(figsize=(13,5.5))
for wp,col,lab in [(P.segment_aile(i),'#9a9a90','aile (segment avec baie de servo)'),(P.aileron(i),'#5577aa','aileron'),(P.guignol_aileron(),'#e07020','guignol PETG')]:
    from shapely.geometry import Polygon as SP
    geom=None
    for e in coupe(wp,yc+0.3 if 'guignol' in lab else yc+3):
        p=SP(np.c_[e[:,0],e[:,2]]).buffer(0)
        geom=p if geom is None else geom.symmetric_difference(p)
    polys=[geom] if geom.geom_type=='Polygon' else list(geom.geoms)
    for k,pg in enumerate(polys):
        from matplotlib.path import Path; from matplotlib.patches import PathPatch
        verts=[];codes=[]
        for ring in [pg.exterior,*pg.interiors]:
            xy=np.asarray(ring.coords); verts+=list(xy); codes+=[Path.MOVETO]+[Path.LINETO]*(len(xy)-2)+[Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts,codes),fc=col,ec='k',lw=0.5,alpha=0.9,label=lab if k==0 else None))
# servo couché (23 x 12) dans la poche, palonnier vers le bas
xs=0.545*CORDE; zs=naca_cambrure=None
c=[R(xs-11.5,-2.5),R(xs+11.5,-2.5),R(xs+11.5,9.5),R(xs-11.5,9.5)]
ax.add_patch(MP(c,closed=True,fc='#2a9a50',ec='k',alpha=0.9,label='servo 9-12 g (couché)'))
p0=R(xs+6,-2.5); p1=R(xs+6,-12)
ax.plot([p0[0],p1[0]],[p0[1],p1[1]],color='#c03030',lw=4,label='palonnier du servo')
x0g,_=P._x_guignol(CORDE,AILERON_X+AILERON_JEU/2/CORDE)
zl=min(P.naca_surfaces(PROFIL_AILE,CORDE,x0g/CORDE))
g=R(x0g+3, zl-0.85*GUIGNOL_HAUT*CORDE)
ax.plot([p1[0],g[0]],[p1[1],g[1]],color='k',lw=1.8,ls='--',label='tringle 1,5 mm')
ax.autoscale_view(); ax.set_aspect('equal'); ax.grid(alpha=.25); ax.legend(loc='upper right',fontsize=9)
ax.set_title(f"Coupe à travers l'aile à l'endroit du servo d'aileron (Y = {yc:.0f} mm) — {VERSION.upper()}")
ax.set_xlabel('mm (bord d\'attaque à gauche)'); plt.tight_layout(); plt.savefig(sys.argv[1],dpi=110)
