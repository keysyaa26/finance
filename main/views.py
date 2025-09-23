from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'hero.html')

def calculate(request):
    return render(request, 'calculate.html')

def calculate(request):
    context = {}
    if request.method == "POST":
        gaji = int(request.POST.get("salary", 0))
        file = request.FILES.get("excel")