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

    # --- Tentukan proporsi sesuai cluster ---
    if cluster == 0:
        proporsi = {'Kebutuhan': 0.45, 'Keinginan': 0.20, 'Tabungan': 0.35}
        cluster_name = "Hemat"
    elif cluster == 1:
        proporsi = {'Kebutuhan': 0.50, 'Keinginan': 0.30, 'Tabungan': 0.20}
        cluster_name = "Normal"
    else:
        proporsi = {'Kebutuhan': 0.55, 'Keinginan': 0.25, 'Tabungan': 0.20}
        cluster_name = "Boros"

    # --- Hitung rekomendasi utama ---
    rekomendasi = {k: round(gaji * v, 2) for k, v in proporsi.items()}

    # --- Hitung rincian kebutuhan per kategori ---
    total_pengeluaran = user_agg['TotalAmount'].sum()
    detail = []
    for _, row in user_agg.iterrows():
        persen = row['TotalAmount'] / total_pengeluaran
        nominal = gaji * persen * proporsi['Kebutuhan']
        detail.append({
            "kategori": row['Kategori'],
            "nominal": round(nominal, 2),
            "persen": round(persen * 100, 1)
        })

    # --- Siapkan data chart untuk frontend ---
    kebutuhan_chart = {
        "labels": [d["kategori"] for d in detail],
        "values": [d["nominal"] for d in detail]
    }

    total_chart = {
        "labels": list(rekomendasi.keys()),
        "values": list(rekomendasi.values())
    }

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
