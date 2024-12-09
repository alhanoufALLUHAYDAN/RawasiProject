from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
# Create your views here.

def home_view(request:HttpRequest):
    return render(request,'main/home.html')