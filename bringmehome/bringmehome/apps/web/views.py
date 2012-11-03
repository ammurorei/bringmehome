from django.shortcuts import render


#todo
def landing(request):
	return render(request, 'landing.html')

def home(request, user_id):
	ctx = {
		'user_id' : user_id,
	}
	return render(request, 'home.html', ctx)

def privacy(request):
	return render(request, 'privacy.html')	