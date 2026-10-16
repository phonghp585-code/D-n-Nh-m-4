"""Descriptive and comparative analysis of 2023 vs 2025 Vietnamese THPT scores."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SUBJECT_ALIASES = {
 "Toán": ["mathematics", "math", "toan", "điểm toán", "toán"],
 "Ngữ văn": ["literature", "ngu van", "ngữ văn", "van", "điểm văn"],
 "Ngoại ngữ": ["foreign language", "foreign_language", "ngoai ngu", "ngoại ngữ", "english", "ma ngoai ngu"],
 "Vật lý": ["physics", "vat ly", "vật lý", "ly"],
 "Hóa học": ["chemistry", "hoa hoc", "hóa học", "hoa"],
 "Sinh học": ["biology", "sinh hoc", "sinh học", "sinh"],
 "Lịch sử": ["history", "lich su", "lịch sử", "su"],
 "Địa lý": ["geography", "dia ly", "địa lý", "dia"],
 "GDCD": ["civic education", "gdcd", "giao duc cong dan", "giáo dục công dân"],
 "GDKT&PL": ["economic and legal education", "gdkt&pl", "gdk tpl", "giáo dục kinh tế và pháp luật"]
}
def norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)
def read_dataset(path):
    p=Path(path)
    if not p.exists(): raise FileNotFoundError(f"Không tìm thấy dataset: {p}")
    if p.suffix.lower()==".parquet": return pd.read_parquet(p)
    if p.suffix.lower() in (".xlsx",".xls"): return pd.read_excel(p)
    return pd.read_csv(p, low_memory=False)
def map_subject_columns(df):
    cols={}
    normalized={norm(c):c for c in df.columns}
    for subject, aliases in SUBJECT_ALIASES.items():
        for alias in aliases:
            key=norm(alias)
            found=normalized.get(key)
            if found is not None:
                cols[subject]=found; break
        if subject not in cols:
            # Prefer exact normalized alias containment only for long labels.
            for key, original in normalized.items():
                if any(len(norm(a))>=6 and (norm(a) in key or key in norm(a)) for a in aliases):
                    cols[subject]=original; break
    return cols
def tidy_year(df, year):
    cols=map_subject_columns(df)
    if not cols: raise ValueError(f"Năm {year}: không nhận diện được cột môn. Các cột hiện có: {list(df.columns)}")
    out=pd.DataFrame({"year":year})
    for subject,col in cols.items():
        s=pd.to_numeric(df[col].replace({"":np.nan,"-":np.nan}),errors="coerce")
        s=s.where(s.between(0,10))
        out[subject]=s
    return out
def summarize(long):
    rows=[]
    for (year,subject),g in long.groupby(["year","subject"],dropna=False):
        s=g.score.dropna()
        if s.empty: continue
        rows.append({"year":int(year),"subject":subject,"n":int(s.size),"mean":s.mean(),"median":s.median(),
          "std":s.std(ddof=1),"skewness":s.skew(),"kurtosis_excess":s.kurt(),
          "min":s.min(),"q1":s.quantile(.25),"q3":s.quantile(.75),"max":s.max(),
          "pct_le_1":(s<=1).mean()*100,"pct_lt_5":(s<5).mean()*100,
          "pct_ge_8":(s>=8).mean()*100,"pct_ge_9":(s>=9).mean()*100})
    return pd.DataFrame(rows).sort_values(["subject","year"]).reset_index(drop=True)
def plot_subject(long, subject, outdir):
    sub=long[(long.subject==subject)&long.score.notna()]
    if sub.empty:return []
    paths=[]
    # Histograms on a shared scale
    fig,ax=plt.subplots(figsize=(9,5))
    for year,g in sub.groupby("year"):
        ax.hist(g.score,bins=np.arange(-.25,10.76,.25),density=True,alpha=.42,label=str(year))
    ax.set(title=f"Histogram phân phối điểm: {subject}",xlabel="Điểm",ylabel="Mật độ");ax.set_xlim(0,10);ax.legend();fig.tight_layout()
    p=outdir/f"{slug(subject)}_histogram.png";fig.savefig(p,dpi=160);plt.close(fig);paths.append(p)
    # KDE (Gaussian kernel, with a safe fallback if scipy is unavailable)
    fig,ax=plt.subplots(figsize=(9,5))
    for year,g in sub.groupby("year"):
        x=g.score.to_numpy()
        try:
            from scipy.stats import gaussian_kde
            grid=np.linspace(0,10,400); ax.plot(grid,gaussian_kde(x)(grid),label=str(year))
        except Exception:
            ax.hist(x,bins=np.arange(0,10.25,.25),density=True,histtype="step",label=str(year))
    ax.set(title=f"KDE / đường mật độ: {subject}",xlabel="Điểm",ylabel="Mật độ");ax.set_xlim(0,10);ax.legend();fig.tight_layout()
    p=outdir/f"{slug(subject)}_kde.png";fig.savefig(p,dpi=160);plt.close(fig);paths.append(p)
    fig,ax=plt.subplots(figsize=(8,5)); data=[sub.loc[sub.year==y,"score"].dropna() for y in sorted(sub.year.unique())]
    ax.boxplot(data,tick_labels=[str(y) for y in sorted(sub.year.unique())],showfliers=False)
    ax.set(title=f"Boxplot điểm: {subject}",xlabel="Năm",ylabel="Điểm");ax.set_ylim(0,10);fig.tight_layout()
    p=outdir/f"{slug(subject)}_boxplot.png";fig.savefig(p,dpi=160);plt.close(fig);paths.append(p)
    fig,ax=plt.subplots(figsize=(8,5))
    years=sorted(sub.year.unique()); vals=[sub.loc[sub.year==y,"score"].dropna().to_numpy() for y in years]
    ax.violinplot(vals,showmedians=True,showextrema=True);ax.set_xticks(range(1,len(years)+1),[str(y) for y in years])
    ax.set(title=f"Violin plot điểm: {subject}",xlabel="Năm",ylabel="Điểm");ax.set_ylim(0,10);fig.tight_layout()
    p=outdir/f"{slug(subject)}_violin.png";fig.savefig(p,dpi=160);plt.close(fig);paths.append(p)
    return paths
def slug(s): return re.sub(r"[^a-z0-9]+","_",norm(s)).strip("_")
def write_docx(stats, figs, outpath, nrows):
    from docx import Document
    from docx.shared import Inches
    doc=Document();doc.add_heading("BÁO CÁO PHÂN TÍCH PHỔ ĐIỂM THI THPT 2023 VÀ 2025",0)
    doc.add_paragraph("Chủ đề 1: Phân tích mô tả và so sánh phân phối điểm")
    doc.add_heading("1. Mục tiêu và phương pháp",level=1)
    doc.add_paragraph("So sánh điểm theo môn giữa hai năm bằng trung bình, trung vị, độ lệch chuẩn, skewness, excess kurtosis và tỷ lệ điểm liệt (≤1), dưới trung bình (<5), từ 8 và từ 9. Histogram, KDE, boxplot và violin plot được tạo trên cùng thang điểm 0–10. Điểm thiếu không được tự động điền; điểm ngoài [0,10] được xem là không hợp lệ và bỏ khỏi thống kê môn.")
    doc.add_paragraph(f"Số dòng quan sát sau khi chuẩn hóa dữ liệu dài: {nrows:,}. Kết quả phụ thuộc các tệp dữ liệu cục bộ được truyền vào lệnh chạy.")
    doc.add_heading("2. Bảng thống kê mô tả",level=1)
    table=doc.add_table(rows=1, cols=8);table.style="Light Shading Accent 1"
    headers=["Năm","Môn","N","Trung bình","Trung vị","Độ lệch chuẩn","Skewness","Kurtosis (excess)"]
    for c,h in zip(table.rows[0].cells,headers):c.text=h
    for _,r in stats.iterrows():
        cells=table.add_row().cells
        vals=[int(r.year),r.subject,int(r.n),f'{r["mean"]:.3f}',f'{r["median"]:.3f}',f'{r["std"]:.3f}',f'{r["skewness"]:.3f}',f'{r["kurtosis_excess"]:.3f}']
        for c,v in zip(cells,vals):c.text=str(v)
    doc.add_heading("3. Tỷ lệ theo ngưỡng điểm",level=1)
    t=doc.add_table(rows=1,cols=6);t.style="Light Shading Accent 1"
    for c,h in zip(t.rows[0].cells,["Năm","Môn","≤1 (%)","<5 (%)","≥8 (%)","≥9 (%)"]):c.text=h
    for _,r in stats.iterrows():
        cells=t.add_row().cells
        for c,v in zip(cells,[int(r.year),r.subject,f'{r.pct_le_1:.2f}',f'{r.pct_lt_5:.2f}',f'{r.pct_ge_8:.2f}',f'{r.pct_ge_9:.2f}']):c.text=str(v)
    doc.add_heading("4. Trực quan hóa và diễn giải",level=1)
    doc.add_paragraph("Đọc histogram/KDE để nhận diện dịch chuyển vị trí, độ phân tán và hình dạng phân phối; boxplot/violin plot để so sánh trung vị, khoảng tứ phân vị và mật độ. So sánh chỉ nên thực hiện trên cùng môn và cần lưu ý thay đổi cấu trúc đề thi, cách tổ chức kỳ thi và nhóm thí sinh giữa các năm.")
    for subject, paths in figs.items():
        doc.add_heading(subject,level=2)
        for p in paths:
            doc.add_picture(str(p),width=Inches(5.8))
            doc.add_paragraph(p.name)
    doc.add_heading("5. Giới hạn",level=1)
    doc.add_paragraph("Đây là so sánh mô tả, không chứng minh nguyên nhân. Tỷ lệ được tính trên số điểm hợp lệ của từng môn, không phải toàn bộ số thí sinh nếu có dữ liệu thiếu. Chương trình không suy đoán điểm thiếu và không gộp môn có tên không được nhận diện.")
    doc.save(outpath)
def run(file23,file25,outdir):
    outdir=Path(outdir); figsdir=outdir/"figures";outdir.mkdir(parents=True,exist_ok=True);figsdir.mkdir(parents=True,exist_ok=True)
    d23=tidy_year(read_dataset(file23),2023);d25=tidy_year(read_dataset(file25),2025)
    subjects=sorted(set(d23.columns[1:]) & set(d25.columns[1:]))
    if not subjects: raise ValueError("Không có môn chung giữa hai dataset sau khi ánh xạ tên cột.")
    wide=pd.concat([d23[["year"]+subjects],d25[["year"]+subjects]],ignore_index=True)
    long=wide.melt(id_vars="year",var_name="subject",value_name="score")
    long=long[long.score.notna()].copy()
    stats=summarize(long)
    stats.to_csv(outdir/"thong_ke_mo_ta_2023_2025.csv",index=False,encoding="utf-8-sig")
    long.to_csv(outdir/"diem_long_2023_2025.csv",index=False,encoding="utf-8-sig")
    figs={}
    for s in subjects: figs[s]=plot_subject(long,s,figsdir)
    write_docx(stats,figs,outdir/"bao_cao_phan_tich_pho_diem_2023_2025.docx",len(long))
    (outdir/"run_metadata.json").write_text(json.dumps({"years":[2023,2025],"subjects":subjects,"valid_score_rows":len(long),"source_2023":str(file23),"source_2025":str(file25)},ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Hoàn tất: {outdir.resolve()} | {len(subjects)} môn | {len(long):,} điểm hợp lệ")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--2023",dest="file23",default="data/processed/week3/exam_2023.parquet")
    ap.add_argument("--2025",dest="file25",default="data/dataset_diem_thi_thpt_2025.csv")
    ap.add_argument("--out",default="outputs/score_distribution")
    a=ap.parse_args();run(a.file23,a.file25,a.out)
if __name__=="__main__":main()
