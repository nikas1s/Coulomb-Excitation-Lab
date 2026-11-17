"""Run from the repo: .venv/bin/python examples/research/run_study.py

Writes a standalone scientific figure; calculations use full coupled channels.
"""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from coulex.model import parse_input
from coulex.research import Parameter,sensitivity
from coulex.shapes import invariants
OUT=Path(__file__).resolve().parent
r=parse_input((OUT/'synthetic_rotor.txt').read_text())
angles=np.linspace(30,180,16)
base,jac,error=sensitivity(r,angles,[Parameter('element',0)],[.001])
fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
for level in (1,2):
    axes[0].plot(angles,base.cross_sections[:,level],label=f'Level {level+1}')
    axes[1].plot(angles,jac[:,level,0],label=f'Level {level+1}')
axes[0].set(ylabel='Cross section (barn/sr)',xlabel='CM angle (degrees)',title='Synthetic rotor excitation')
axes[1].set(ylabel='Derivative (barn/sr per eb)',xlabel='CM angle (degrees)',title='Sensitivity to ground-state E2 coupling')
for ax in axes: ax.legend(); ax.grid(alpha=.3)
fig.savefig(OUT/'sensitivity.png',dpi=180)
fig.savefig(OUT/'sensitivity.svg')
print(invariants(r))
