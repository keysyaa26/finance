from django.shortcuts import render
from django.conf import settings
from pathlib import Path
import pandas as pd
import joblib
import os
from .utilys import preprocessingData, prepareData, hasilRekomendasi
import logging
from django.contrib import messages

logger = logging.getLogger('smartFinance')

MODEL_PATH = os.path.join(settings.BASE_DIR, "model", "kmeans_model.pkl")
SCALER_PATH = os.path.join(settings.BASE_DIR, "model", "scaler.pkl")

kmeans_model = joblib.load(MODEL_PATH)
scaler_model = joblib.load(SCALER_PATH)


# Create your views here.
def home(request):
    return render(request, 'hero.html')

def calculate(request):
    return render(request, 'calculate.html')

def predict(request):

    context = {}
    if request.method == "POST":
        gaji = int(request.POST.get("salary", 0))
        file = request.FILES.get("expenses")
        logger.info(f"Salary: {gaji}")
        
        if file:
            try:
                df = pd.read_excel(file)
            except Exception as e:
                messages.error(request, "❌ Error reading the Excel file. Please upload a valid .xlsx file.")
                return render(request, "calculate.html")
            
            try:
                data = preprocessingData(df)
                agg_data = prepareData(data)

                # scalling data
                features = agg_data[["TotalAmount", "AvgAmount", "TransCount"]]
                features_scaled = scaler_model.transform(features)

                # DEBUG SCALED DATA
                scaled_df = pd.DataFrame(
                    features_scaled,
                    columns=["TotalAmount", "AvgAmount", "TransCount"]
                )
                context["scaled_preview"] = scaled_df.head().to_html(classes="table table-sm")

                # clustering
                cluster = kmeans_model.predict(features_scaled)[0]
                context["cluster"] = cluster

                # DEBUG CLUSTERING DATA
                agg_data["Cluster"] = kmeans_model.predict(features_scaled)
                context["cluster_preview"] = agg_data.to_html(classes="table table-sm")

                hasil = hasilRekomendasi(gaji, cluster, agg_data)
                context.update(hasil)
            except Exception as e:
                logger.info(f"Error processing the Excel file: {e}")
                messages.error(request, "❌ Error processing the Excel file.")
                return render(request, "calculate.html")
        
    logger.info(hasil)

    return render(request, 'calculate.html', {"hasil": gaji})
