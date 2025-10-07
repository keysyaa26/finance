import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import io, base64

def preprocessingData(df):
    # konversi tanggal
    if "Tanggal" in df.columns:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    
    # konversi nominal ke numeric
    if "Nominal" in df.columns:
        df["Nominal"] = (
            df["Nominal"].astype(str)
            .str.replace(r"[^\d\.-]", "", regex=True)
        )
        # isi 0 jika konversi failed
        df["Nominal"] = pd.to_numeric(df["Nominal"], errors="coerce").fillna(0)
    
    # ubah kolom tipe ke bentuk kategori
    if "Kategori" in df.columns:
        df["Kategori"] = df["Kategori"].astype("category")

    df = df.drop_duplicates()

    return df

def prepareData(data):
    # proses agregasi data
    agg_data = (data.groupby("Kategori")["Nominal"]
        .agg(
            TotalAmount="sum",
            AvgAmount="mean",
            TransCount="count"
        )
        .reset_index()
    )
    return agg_data




def hasilRekomendasi(gaji, cluster, user_agg):
    today = datetime.today()
    next_month = today + relativedelta(months=1)
    bulan = next_month.strftime("%B %Y")  

    if cluster == 0:
        proporsi = {'Kebutuhan': 0.45, 'Keinginan': 0.20, 'Tabungan': 0.35}
        cluster_name = "Hemat"
    elif cluster == 1:
        proporsi = {'Kebutuhan': 0.50, 'Keinginan': 0.30, 'Tabungan': 0.20}
        cluster_name = "Normal"
    else:
        proporsi = {'Kebutuhan': 0.55, 'Keinginan': 0.25, 'Tabungan': 0.20}
        cluster_name = "Boros"

    rekomendasi = {k: round(gaji * v, 2) for k, v in proporsi.items()}

    total_pengeluaran = user_agg['TotalAmount'].sum()
    detail = []
    for _, row in user_agg.iterrows():
        persen = row['TotalAmount'] / total_pengeluaran
        nominal = gaji * persen * proporsi['Kebutuhan']
        detail.append((row['Kategori'], round(nominal, 2)))

    labels = [d[0] for d in detail]
    values = [d[1] for d in detail]
    fig1, ax1 = plt.subplots(figsize=(5,5))
    ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    ax1.set_title(f"Distribusi Kebutuhan ({bulan}, Cluster: {cluster_name})")

    buffer1 = io.BytesIO()
    plt.savefig(buffer1, format='png')
    buffer1.seek(0)
    kebutuhan_chart = base64.b64encode(buffer1.read()).decode('utf-8')
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(5,5))
    ax2.pie(proporsi.values(),
            labels=proporsi.keys(),
            autopct='%1.1f%%', startangle=140,
            colors=['#4CAF50','#FF9800','#2196F3'])
    ax2.set_title(f"Distribusi Total Alokasi Gaji ({bulan})")

    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    total_chart = base64.b64encode(buffer2.read()).decode('utf-8')
    plt.close(fig2)

    return {
        "bulan": bulan,
        "gaji": gaji,
        "cluster": cluster,
        "cluster_name": cluster_name,
        "rekomendasi": rekomendasi,
        "detail": detail,
        "charts": {
            "kebutuhan": kebutuhan_chart,
            "total": total_chart
        }
    }
