"""Readable scientific plots shared by subject and combination reports."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

COLORS={2023:'#276b9a',2025:'#d27720'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
    'axes.labelsize':11,'xtick.labelsize':10,'ytick.labelsize':11,
    'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white'})

def safe_name(s):return s.replace(':','_').replace('|','_').replace('/','_')

def density_curve(values,maximum=10):
    """Fine-bin Gaussian KDE, all observations, reflected physical boundaries."""
    x=np.asarray(values,dtype=float);x=x[np.isfinite(x)]
    if not len(x):raise ValueError('No observations for density')
    bandwidth=.20 if maximum==10 else .35
    bins=np.linspace(0,maximum,501 if maximum==10 else 601)
    counts,edges=np.histogram(x,bins=bins);dx=edges[1]-edges[0]
    smooth=gaussian_filter1d(counts.astype(float)/(len(x)*dx),bandwidth/dx,mode='reflect')
    centers=(edges[:-1]+edges[1:])/2;grid=np.linspace(0,maximum,601)
    curve=np.interp(grid,centers,smooth)
    curve/=np.trapezoid(curve,grid)
    return grid,curve

def distribution_plot(arrays,title,path:Path,maximum=10):
    fig,axes=plt.subplots(1,2,figsize=(13,4.9));counts=[]
    for year,x in sorted(arrays.items()):
        x=np.asarray(x,dtype=float);x=x[np.isfinite(x)]
        if not len(x):continue
        support,freq=np.unique(x,return_counts=True)
        grid,curve=density_curve(x,maximum)
        axes[0].plot(grid,curve,color=COLORS[year],lw=2.1,linestyle='--' if year==2023 else '-',label=f'{year}: n={len(x):,}')
        axes[1].step(np.r_[0,support],np.r_[0,100*np.cumsum(freq)/len(x)],where='post',
            color=COLORS[year],lw=1.8,label=str(year))
    for ax in axes:ax.set_xlim(0,maximum);ax.set_xlabel(f'Điểm (thang 0–{maximum})');ax.grid(alpha=.16)
    axes[0].set_ylabel('Mật độ ước lượng');axes[0].set_title('Phổ điểm mượt (KDE)');axes[0].legend(fontsize=10)
    axes[1].set_ylabel('% có điểm không vượt ngưỡng');axes[1].set_ylim(0,101);axes[1].set_title('Phân phối tích lũy (ECDF)');axes[1].legend()
    fig.suptitle(title,fontsize=16,fontweight='bold');fig.tight_layout(rect=[0,0,1,.94]);path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=150);plt.close(fig)

def effect_overview(table,path:Path,title):
    t=table.loc[table.cohen_d.notna()].copy().sort_values('cohen_d');n=len(t)
    fig,axes=plt.subplots(1,3,figsize=(17,max(5,.45*n+1.8)),sharey=True);y=np.arange(n)
    for i,r in enumerate(t.itertuples()):
        axes[0].plot([r.mean_2023,r.mean_2025],[i,i],color='#bbc3cb',lw=2)
    axes[0].scatter(t.mean_2023,y,label='2023',color=COLORS[2023]);axes[0].scatter(t.mean_2025,y,label='2025',color=COLORS[2025],marker='D')
    axes[0].set_yticks(y,t.label);axes[0].set_title('Trung bình');axes[0].legend(fontsize=10)
    for ax,col,lo,hi,caption in [(axes[1],'delta_mean','delta_ci_low','delta_ci_high','Chênh trung bình và CI 95%'),(axes[2],'cohen_d','d_ci_low','d_ci_high','Cohen’s d và CI bootstrap 95%')]:
        ax.errorbar(t[col],y,xerr=np.array([t[col]-t[lo],t[hi]-t[col]]),fmt='o',capsize=3,color='#3b687c');ax.axvline(0,color='gray',lw=1);ax.set_title(caption)
    axes[1].set_xlabel('2025 − 2023 (điểm)');axes[2].set_xlabel('2025 − 2023 (SD gộp)')
    for ax in axes:ax.grid(axis='x',alpha=.16)
    fig.suptitle(title,fontsize=16,fontweight='bold');fig.tight_layout(rect=[0,0,1,.95]);path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=145);plt.close(fig)
