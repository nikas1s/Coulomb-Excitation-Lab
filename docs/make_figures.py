"""Regenerate standalone teaching figures: .venv/bin/python docs/make_figures.py."""
from pathlib import Path
import os
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from coulex import parse_input,CoupledChannels
from coulex.workflow import calculate, results_frame

model=parse_input((ROOT/'examples/22Mg_104Pd_literature.txt').read_text())
scan=calculate(model,np.arange(1.,181.,2.))
data=results_frame(model,scan)
trajectory=CoupledChannels(model).solve(90,history_points=501)
colors=['#087f8c','#d66b32','#6360a8']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
for i,level in enumerate(model.levels):
    ax=axes[0,0]
    ax.plot([level.spin-.5,level.spin+.5],[level.energy]*2,lw=4,color=colors[i])
    ax.text(level.spin,level.energy+.15,f'{level.spin:g}⁺ · {level.energy:g} MeV',ha='center',fontsize=10)
    state=data[data.level==i+1]
    axes[0,1].plot(state.theta_cm_deg,state.probability,color=colors[i],label=f'Level {i+1}, J={level.spin:g}')
    if i:
        axes[1,0].semilogy(state.theta_cm_deg,state.dsigma_cm_barn_per_sr,color=colors[i],label=f'Level {i+1}')
    axes[1,1].plot(trajectory.omega,trajectory.history[i],color=colors[i],label=f'Level {i+1}')
for me in model.elements:
    if me.initial!=me.final:
        a,b=model.levels[me.initial],model.levels[me.final]
        axes[0,0].annotate('',xy=(b.spin,b.energy-.05),xytext=(a.spin,a.energy+.1),
                           arrowprops=dict(arrowstyle='->',color='#9cabbc',lw=1.5))
axes[0,0].set(xlabel='Spin J (ℏ)',ylabel='Energy (MeV)',title='1. Describe the nucleus',ylim=(-.3,4),xlim=(-1,5))
axes[0,1].set(xlabel='CM scattering angle (degrees)',ylabel='Final population probability',title='2. Couple all levels',ylim=(-.02,1.02))
axes[1,0].set(xlabel='CM scattering angle (degrees)',ylabel='dσ/dΩcm (barn/sr)',title='3. Convert populations to cross sections',ylim=(1e-9,1))
axes[1,1].set(xlabel='Orbit parameter ω',ylabel='Instantaneous population',title='4. Follow a collision at 90°',xlim=(-4,4))
axes[1,1].axvline(0,color='#999999',lw=1,ls='--')
for ax in [axes[0,1],axes[1,0],axes[1,1]]:
    ax.legend(frameon=False,fontsize=9)
    ax.grid(alpha=.15)
fig.suptitle(f'Coulomb Excitation Lab  |  ²²Mg + ¹⁰⁴Pd at {model.energy_lab:g} MeV',fontsize=17,color='#192d45')
fig.savefig(ROOT/'docs/teaching_overview.png',dpi=180)
fig.savefig(ROOT/'docs/teaching_overview.svg')
plt.close(fig)
