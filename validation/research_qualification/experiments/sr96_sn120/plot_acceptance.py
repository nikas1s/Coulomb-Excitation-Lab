"""Plot nominal two-body geometry, not a calibrated experimental response."""
from pathlib import Path
import os
import sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from coulex import Reaction,Level
from coulex.observables import lab_angle
from coulex.acceptance import recoil_lab_angle,particle_energy
r=Reaction('96Sr + 120Sn nominal acceptance',38,96,50,120,275.5,(Level(0,0),Level(2,.815)),(),dipole_strength=0.)
theta=np.linspace(.01,179.99,1800)
fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
axes[0].plot(theta,lab_angle(r,theta,.815),label='Scattered projectile')
axes[0].plot(theta,recoil_lab_angle(r,theta,.815),label='Recoiling target')
axes[0].axhspan(20,55,color='grey',alpha=.15,label='Nominal detector annulus')
axes[0].set(xlabel='Projectile CM angle (degrees)',ylabel='Particle lab angle (degrees)',ylim=(0,100),title='Inelastic two-body angular mapping')
for name in ('projectile','recoil'):
    axes[1].plot(theta,particle_energy(r,theta,.815,name),label=name.capitalize())
axes[1].axhline(1.,ls='--',color='grey',label='Illustrative 1 MeV threshold')
axes[1].set(xlabel='Projectile CM angle (degrees)',ylabel='Particle kinetic energy (MeV)',yscale='log',ylim=(1e-4,400),title='Why energy cuts matter')
for ax in axes:
    ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.suptitle('96Sr + 120Sn, 275.5 MeV, excitation 0.815 MeV: nominal geometry only')
out=Path(__file__).resolve().parent
fig.savefig(out/'acceptance.png',dpi=180);fig.savefig(out/'acceptance.svg')
p=out/'acceptance.svg';p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines()).rstrip()+'\n')
