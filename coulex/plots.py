"""Interactive teaching figures. Every physical axis carries its units."""
import numpy as np
import plotly.graph_objects as go
from .solver import collision_functions
from .i18n import t

COLORS = ['#087f8c','#d66b32','#6360a8','#3b936b','#bd527a','#7c8945','#3e79b4','#885b43','#7c7987','#bd9648','#329eaa']


def style(fig, x, y, title=''):
    fig.update_layout(template='plotly_white', title=title, xaxis_title=x, yaxis_title=y,
                      margin=dict(l=30,r=20,t=45,b=40), height=390,
                      font=dict(family='Arial',size=13,color='#192d45'),
                      legend=dict(orientation='h',y=-.24), hovermode='x unified')
    return fig


def label(index, level):
    return f'{index+1}: J={level.spin:g}{"+" if level.parity>0 else "−"}, {level.energy:g} MeV'


def curves(reaction, x, values, xlabel, ylabel, selected=None, log=False):
    fig = go.Figure()
    for i in range(len(reaction.levels)) if selected is None else selected:
        fig.add_scatter(x=x, y=values[:,i], mode='lines+markers', name=label(i,reaction.levels[i]),
                        line=dict(color=COLORS[i%len(COLORS)]),marker=dict(size=4))
    style(fig,xlabel,ylabel)
    if log:
        fig.update_yaxes(type='log')
    return fig


def levels(reaction):
    fig = go.Figure()
    for me in reaction.elements:
        if me.initial==me.final or me.value==0:
            continue
        a,b=reaction.levels[me.initial],reaction.levels[me.final]
        fig.add_scatter(x=[a.spin,b.spin],y=[a.energy,b.energy],mode='lines',
                        line=dict(color='#a6b9c8',width=1+min(abs(me.value),3)),showlegend=False,
                        hovertemplate=f'E{me.multipolarity}: {me.value:g} e b^({me.multipolarity}/2)<extra></extra>')
    for i,level in enumerate(reaction.levels):
        fig.add_scatter(x=[level.spin-.35,level.spin+.35],y=[level.energy]*2,mode='lines',
                        line=dict(color=COLORS[i%len(COLORS)],width=5),name=label(i,level),
                        hovertemplate=label(i,level)+'<extra></extra>')
    return style(fig,t('Spin J (ℏ)'),t('Excitation energy (MeV)'),t('Levels and electromagnetic connections'))


def orbit(reaction, angle):
    epsilon=1/np.sin(np.deg2rad(angle)/2)
    w=np.linspace(-2.4,2.4,400)
    a=reaction.head_on_distance/2
    z=a*(np.cosh(w)+epsilon)
    y=a*np.sqrt(max(0,epsilon**2-1))*np.sinh(w)
    fig=go.Figure()
    fig.add_scatter(x=z,y=y,name=t('Relative Rutherford orbit'),mode='lines',line=dict(color=COLORS[0]))
    fig.add_scatter(x=[0],y=[0],name=t('Partner nucleus'),mode='markers',marker=dict(size=16,color=COLORS[1]))
    fig.add_scatter(x=[a*(1+epsilon)],y=[0],name=t('Closest approach'),mode='markers',marker=dict(size=8,color=COLORS[2]))
    fig.update_yaxes(scaleanchor='x',scaleratio=1)
    return style(fig,'z (fm)','y (fm)',t('Relative trajectory at θcm = {angle}°',angle=f'{angle:g}'))


def collision_plot(reaction, angle, lam=2):
    epsilon=1/np.sin(np.deg2rad(angle)/2)
    w=np.linspace(-5,5,401)
    q=np.array([collision_functions(lam,epsilon,x,reaction.polarization) for x in w])
    fig=go.Figure()
    for mu in range(lam+1):
        fig.add_scatter(x=w,y=q[:,mu].imag if mu%2 else q[:,mu].real,
                        name=f'μ={mu}, '+(t('imaginary part') if mu%2 else t('real part')),line=dict(color=COLORS[mu]))
    return style(fig,t('Orbit parameter ω (0 = closest approach)'),t('Collision function Q (dimensionless)'),t('E{lam} driving field',lam=lam))
