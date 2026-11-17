"""Standalone scientific teaching figure; no experimental detector claim."""
from pathlib import Path
from dataclasses import replace
import os
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from validation.gosia_points import cases
from coulex import CoupledChannels
from coulex.lab_gamma import orbit_to_lab,emitter_beta,inverse_photon_boost,angular_density,angular_kernel


def main():
    reaction=replace(list(cases())[1],excitation='projectile')
    theta=np.pi/2;rho=CoupledChannels(reaction).solve(90.).density_matrices[1]
    rho/=np.trace(rho);kernel=angular_kernel(rho,2,0,2)
    polar=np.linspace(0,np.pi,361);lab=np.column_stack([np.sin(polar),np.zeros(len(polar)),np.cos(polar)])
    curves=[]
    for boost in (False,True):
        value=np.zeros(len(polar))
        for phi in (np.arange(32)+.5)*2*np.pi/32:
            rest,doppler=inverse_photon_boost(lab,emitter_beta(reaction,theta,.3,phi) if boost else np.zeros(3))
            value+=angular_density(kernel,2,rest@orbit_to_lab(theta,phi,'projectile'))*doppler**2/32
        curves.append(value)
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for y,label in zip(curves,['Lab axes, no photon boost','Lab axes, with photon boost']): axes[0].plot(np.rad2deg(polar),4*np.pi*y,label=label)
    axes[0].axhline(1,color='grey',ls=':',label='Isotropic reference')
    axes[0].set(xlabel='Photon angle from beam (deg)',ylabel='4π × normalized photon density (sr⁻¹)',title='Aligned E2 decay; particle azimuth averaged')
    axes[0].legend(fontsize=8)
    for phi,label in [(0.,'Particle azimuth 0°'),(np.pi,'Particle azimuth 180°')]:
        _,doppler=inverse_photon_boost(lab,emitter_beta(reaction,theta,.3,phi))
        axes[1].plot(np.rad2deg(polar),300*doppler,label=label)
    axes[1].axhline(300,color='grey',ls=':')
    axes[1].set(xlabel='Photon angle from beam (deg)',ylabel='Laboratory photon energy (keV)',title='A 300 keV rest-frame line')
    axes[1].legend(fontsize=8)
    for ax in axes: ax.grid(alpha=.25)
    fig.suptitle('Synthetic ¹⁶O + ⁵⁸Ni, 30 MeV; projectile excitation; θCM = 90°')
    out=ROOT/'docs'
    fig.savefig(out/'lab_gamma_response.png',dpi=180)
    fig.savefig(out/'lab_gamma_response.svg')
    svg=out/'lab_gamma_response.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()).rstrip()+'\n')
    plt.close(fig)


if __name__=='__main__':main()
