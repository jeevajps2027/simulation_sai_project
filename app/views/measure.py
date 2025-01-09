from django.shortcuts import render


def measure(request):
    return render(request, 'app/measure.html')