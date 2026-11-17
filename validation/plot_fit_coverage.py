"""Plot scoped coverage and pulls from the saved, actual multilevel ODE fits."""
from pathlib import Path
import json
import os
import sys
import numpy as np
from scipy.stats import norm
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    report=json.loads((ROOT/'validation/research_qualification/multilevel-coverage.json').read_text(encoding='utf-8'))
    labels=['Transition E2 element','Diagonal E2 element','Log normalization']
    fig,axes=plt.subplots(1,2,figsize=(11,4.3),constrained_layout=True)
    colors=['tab:blue','tab:orange','tab:green']
    for j,(label,color) in enumerate(zip(labels,colors)):
        for nominal,offset in [('0.68',-.12),('0.95',.12)]:
            entry=report['intervals'][nominal][j];y=entry['observed'];lo,hi=entry['binomial_99_interval']
            axes[0].errorbar(j+offset,y,yerr=[[y-lo],[hi-y]],color=color,
                marker='o' if nominal=='0.68' else 's',capsize=4,
                label=f'{int(float(nominal)*100)}% nominal' if j==0 else None)
    axes[0].axhline(.68,color='grey',ls=':');axes[0].axhline(.95,color='grey',ls='--')
    axes[0].set_xticks(range(3),['Transition E2','Diagonal E2','Log scale'])
    axes[0].set(ylabel='Observed coverage (99% binomial interval)',ylim=(.35,1.01),
        title=f'{report["trials"]} trials; {report["failed"]} failed; {report["boundary_fits"]} on bounds')
    axes[0].legend(fontsize=8)
    pulls=np.array([row['pulls'] for row in report['records'] if row.get('pulls') is not None])
    grid=np.linspace(-4,4,200)
    axes[1].plot(grid,norm.pdf(grid),color='black',ls='--',label='Standard normal reference')
    bins=np.linspace(-4,4,17)
    for j,(label,color) in enumerate(zip(labels,colors)):
        axes[1].hist(pulls[:,j],bins=bins,weights=np.ones(len(pulls))/(report['trials']*(bins[1]-bins[0])),
            histtype='step',lw=1.7,color=color,label=label)
    axes[1].set(xlabel='(Estimate − truth) /\nfitted standard error',ylabel='Density',title='Local-covariance parameter pulls')
    axes[1].legend(fontsize=8)
    for ax in axes: ax.grid(alpha=.2)
    fig.suptitle('Synthetic nondegenerate E2 network + Q and normalization calibration')
    for extension in ('png','svg'): fig.savefig(ROOT/f'docs/multilevel_coverage.{extension}',dpi=180)
    svg=ROOT/'docs/multilevel_coverage.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()).rstrip()+'\n', encoding='utf-8', newline='\n')
    plt.close(fig)


if __name__=='__main__':main()
