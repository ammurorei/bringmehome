from django.shortcuts import render
from django.template import RequestContext

def home(request):
	return render(request, 'home.html')

def privacy(request):
	return render(request, 'privacy.html')	