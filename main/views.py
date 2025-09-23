from django.shortcuts import render
from django.conf import settings
from pathlib import Path
import pandas as pd
import joblib
import os

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

    return render(request, 'calculate.html', {"hasil": gaji})