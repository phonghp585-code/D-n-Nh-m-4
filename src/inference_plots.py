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

def relation_matrix(table,ids,metric):
    matrix=np.full((len(ids),len(ids)),np.nan);positions={s:i for i,s in enumerate(ids)}
    for row in table.itertuples():
        if row.subject_x in positions and row.subject_y in positions:
            i,j=positions[row.subject_x],positions[row.subject_y];matrix[i,j]=matrix[j,i]=getattr(row,metric)
    return matrix

def relation_heatmap(table,ids,metric,path,title):
    from src.analysis_catalog import label
    matrix=relation_matrix(table,ids,metric);counts=metric=='n_pair'
    display=np.log10(matrix+1) if counts else matrix
    cmap=plt.get_cmap('viridis' if counts else 'RdBu_r').copy();cmap.set_bad('#eeeeee')
    fig,ax=plt.subplots(figsize=(max(10,.65*len(ids)+3),max(9,.6*len(ids)+2)))
    im=ax.imshow(display,cmap=cmap,**({} if counts else dict(vmin=-1,vmax=1)))
    labels=[label(s).replace('Tiếng ','') for s in ids]
    ax.set_xticks(range(len(ids)),labels,rotation=55,ha='right',fontsize=10);ax.set_yticks(range(len(ids)),labels,fontsize=10)
    for i in range(len(ids)):
        for j in range(len(ids)):
            value=matrix[i,j]
            if np.isfinite(value):
                text=(f'{value/1000:.0f}k' if value>=1000 else str(int(value))) if counts else f'{value:.2f}'
                ax.text(j,i,text,ha='center',va='center',fontsize=10,color='white' if counts and value>500 or not counts and abs(value)>.55 else '#222222')
            elif i!=j:ax.text(j,i,'—',ha='center',va='center',fontsize=10,color='#777777')
    fig.colorbar(im,ax=ax,shrink=.8,label='log10(n+1); số trong ô là n' if counts else metric)
    ax.set_title(title+'\nÔ xám: không ước lượng; đường chéo bỏ qua',fontsize=14,pad=16)
    fig.tight_layout();path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=150);plt.close(fig)

def pair_examples(frames,high,folder):
    from src.analysis_catalog import subject_values,label
    targets=[('math','physics'),('literature','history'),('history','geography')]
    for x,y in targets:
        fig,axes=plt.subplots(1,2,figsize=(12,5),sharex=True,sharey=True)
        for ax,(year,frame) in zip(axes,sorted(frames.items())):
            a=subject_values(frame,x).to_numpy(float);b=subject_values(frame,y).to_numpy(float);mask=np.isfinite(a)&np.isfinite(b)
            im=ax.hexbin(a[mask],b[mask],gridsize=35,extent=(0,10,0,10),mincnt=1,bins='log',cmap='viridis')
            ax.set_title(f'{year}: n={int(mask.sum()):,}');ax.set_xlabel(label(x));ax.set_ylabel(label(y));ax.set_xlim(0,10);ax.set_ylim(0,10);fig.colorbar(im,ax=ax,label='Số người/ô (log)')
        fig.suptitle(f'{label(x)} – {label(y)}: phân bố cặp điểm',fontsize=15);fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(folder/f'hexbin_{x}_{y}.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(15,5),sharey=True)
    for ax,(x,y) in zip(axes,targets):
        select=high.loc[high.subject_x.eq(x)&high.subject_y.eq(y)&high.cutoff_mode.eq('P80')].sort_values('year')
        for i,row in enumerate(select.itertuples()):
            ax.bar(i-.17,100*row.p_y_high_baseline,width=.32,color='#b8c2cb',label='Mức nền' if i==0 else None)
            p=100*row.p_y_high_given_x_high;ax.bar(i+.17,p,width=.32,color=COLORS[row.year],label='Khi X cao' if i==0 else None)
            ax.errorbar(i+.17,p,yerr=[[p-100*row.conditional_ci_low],[100*row.conditional_ci_high-p]],color='black',capsize=3)
            ax.text(i+.17,p+2,f'{p:.1f}%',ha='center',fontsize=10)
        ax.set_xticks([0,1],['2023','2025']);ax.set_ylim(0,100);ax.set_title(f'{label(x)} cao → {label(y)} cao');ax.grid(axis='y',alpha=.15)
    axes[0].set_ylabel('Xác suất Y cao (%)');axes[0].legend(fontsize=10);fig.suptitle('Ngưỡng P80 trong đúng tập có cả hai điểm',fontsize=15);fig.tight_layout(rect=[0,0,1,.93]);fig.savefig(folder/'high_score_examples.png',dpi=150);plt.close(fig)

def pca_plot(summary,loadings,title,path):
    from src.analysis_catalog import label
    fig,axes=plt.subplots(1,3,figsize=(15,4.9),gridspec_kw={'width_ratios':[1.1,1,1]})
    for year in (2023,2025):
        s=summary.loc[summary.year.eq(year)].iloc[0];axes[0].plot([1,2,3],[s[f'pc{k}_explained_pct'] for k in (1,2,3)],marker='o',color=COLORS[year],linestyle='--' if year==2023 else '-',label=f'{year}: n={s.n_complete:,}')
    axes[0].set_xticks([1,2,3],['PC1','PC2','PC3']);axes[0].set_ylim(0,100);axes[0].set_ylabel('Phương sai giải thích (%)');axes[0].legend(fontsize=10);axes[0].grid(alpha=.16)
    for ax,year in zip(axes[1:],(2023,2025)):
        t=loadings.loc[loadings.year.eq(year)].sort_values('subject_id');a=t[[f'loading_pc{k}' for k in (1,2,3)]].to_numpy();im=ax.imshow(a,vmin=-1,vmax=1,cmap='RdBu_r');ax.set_xticks([0,1,2],['PC1','PC2','PC3']);ax.set_yticks(range(len(t)),[label(s) for s in t.subject_id]);ax.set_title(f'Loading {year}')
        for i in range(len(t)):
            for j in range(3):ax.text(j,i,f'{a[i,j]:.2f}',ha='center',va='center',color='white' if abs(a[i,j])>.55 else '#222222',fontsize=11)
        fig.colorbar(im,ax=ax,shrink=.75)
    fig.suptitle(title,fontsize=15,fontweight='bold');fig.tight_layout(rect=[0,0,1,.93]);path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=150);plt.close(fig)
