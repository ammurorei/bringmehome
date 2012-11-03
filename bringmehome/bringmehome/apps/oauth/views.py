import re
import json
import datetime
import functools
import urllib
import urllib2
from bs4 import BeautifulSoup

from django.shortcuts import render,redirect
from django.template import RequestContext
from django.http import HttpResponse

from bringmehome import settings

from bringmehome.apps.rest.models import UserProfile

import foursquare
def callback(request):
	code = request.REQUEST.get('code')
	# Construct the client object
	client = foursquare.Foursquare(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, redirect_uri=settings.CALLBACK_URL)

	# Interrogate foursquare's servers to get the user's access_token
	access_token = client.oauth.get_token(code)
	
	# Apply the returned access token to the client
	client.set_access_token(access_token)

	# Get the user's data
	fsq_user = client.users()

	u, created = UserProfile.objects.get_or_create(foursquare_id=fsq_user.get('user').get('id'), oauth_token=access_token)
	u.save()
	print "created user ", u
	print "created new user? ", created
	return redirect('home', {'user_id': u.uuid})