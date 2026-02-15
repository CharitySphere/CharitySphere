from django.shortcuts import render

def home1(request):
    return render(request, 'homepage1.html')

def home2(request):
    return render(request, 'homepage2.html')
