from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def monitor_1(request):
    return HttpResponse("Monitor 1 good")

def monitor_2(request):
    return HttpResponse("Monitor 2 good")
