from django.shortcuts import render

def withoutsrno(request):
    return render(request, 'app/reports/consolidateWithoutSrNo.html')