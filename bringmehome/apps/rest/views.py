import re
import json
import datetime
import functools
import urllib
import urllib2
from bringmehome import settings
from bs4 import BeautifulSoup
import foursquare

from bringmehome.apps.rest.models import UserProfile
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404

BVG_ROOT = 'http://mobil.bvg.de'
BVG_URL = 'http://mobil.bvg.de/Fahrinfo/bin/query.bin/dox'

EXCLUDE = {
	"English" : 0,
	"Fahrplanauskunft" : 0,
	"Mobil" : 0,
	"Klassisch" : 0,
	"Impressum" : 0,
	None : 0,
}

def jsonview(**jsonargs):
	'''
	Make any view return pure json from http://djangosnippets.org/snippets/2102/
	'''
	
	def outer(f):
		@functools.wraps(f)
		def inner_json(request, *args, **kwargs):
			result = f(request, *args, **kwargs)
			if result:
				indent = jsonargs.pop('indent', None)
				data = json.dumps(result, indent=indent, **jsonargs)
			else:
				data = "{}"
			callback = request.GET.get('callback')
			if callback:
				data = '%s(%s);' % (callback, data)

			r = HttpResponse(mimetype='application/json')
			r.write(data)
			return r
		return inner_json
	return outer

@jsonview()
def query_home_address(request, user_id, address_string):

	data = urllib.urlencode({
			'REQ0HafasInitialSelection':0,
			'queryDisplayed': True,
			'SID':'A=16@X=13411086@Y=52551357@O=Von hier starten', #Checkin location data
			'REQ0JourneyStopsZ0A':255,
			'REQ0JourneyStopsZ0G': address_string.encode('utf-8'),
			#REQ0JourneyStopsZ0ID: 0,
			'REQ0JourneyDate':'03.11.12', #now
			'REQ0JourneyTime':'15:10', #now
			'REQ0HafasSearchForw':1,
			'start':'Suchen',
		})
	request = urllib2.urlopen(BVG_URL, data)

	response_data = BeautifulSoup(request.read())

	links = response_data.find_all('a')

	return_data = []

	for link in links:
		try:
			exists = EXCLUDE[link.string]
		except KeyError:
			if 'co=C0' in link.get('href'):
				return [address_string]
			return_data.append(link.string)

	return return_data

@jsonview()
def register_address(request, user_id, address_string):
	try:
		user = UserProfile.objects.get(uuid=user_id)
		user.address = address_string.encode('utf-8')
		user.save()
		return [address_string]
	except Exception, e:
		return []

@csrf_exempt
#@jsonview()
def query_way_home(request):

	user_data = json.loads(request.POST['checkin'])
	checkin_id = user_data['id']

	client = foursquare.Foursquare(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, redirect_uri=settings.CALLBACK_URL)

	try:
		user = UserProfile.objects.get(foursquare_id=user_data['user']['id'])
	except Exception:
		raise Http404

	return_data = []

	match = re.compile('^(conL)|(conD)$')
	now = datetime.datetime.now() + datetime.timedelta(minutes=300) #now is for our servers!  not the user! set it to berlin
	journey_time = now + datetime.timedelta(minutes=60)

	data = urllib.urlencode({
			'REQ0HafasInitialSelection':0,
			'queryDisplayed': True,
			#'SID':'A=16@X=%s@Y=%s@O=Von hier starten' % (user_data['venue']['location']['lng'], user_data['venue']['location']['lat']), #Checkin location data
			'SID':'A=16@X=13411086@Y=52551357@O=Von hier starten',
			'REQ0JourneyStopsZ0A': 255,
			'REQ0JourneyStopsZ0G': user.address.encode('utf-8'),
			#REQ0JourneyStopsZ0ID: 0,
			'REQ0JourneyDate': journey_time.strftime("%d.%m.%y"),
			'REQ0JourneyTime': journey_time.strftime("%H:%M"),
			'REQ0HafasSearchForw':1,
			'start':'Suchen',
		})
	request = urllib2.urlopen(BVG_URL, data)
	response = request.read()
	
	response_data = BeautifulSoup(response)

	links = response_data.find_all('a')

	for link in links:
		if 'co=C0' in link.get('href'):
			l = []
			url = BVG_ROOT + link.get('href')
			link_request = urllib2.urlopen(url)
			link_data = BeautifulSoup(link_request.read())

			routes = link_data.find_all('p', {'class': match})
			for route in routes:
				#print "------------------------------------------------"
				#print route.renderContents()
				#print '------------------------------------------------'
				l.append(route.encode("utf-8"))
			return_data.append(l)
			#print "====================================================="
			#print "====================================================="
			#print "====================================================="
	#return return_data
	message = "hi there!"

	client.checkins.reply(checkin_id, {'text': message}) #add url later

	r = HttpResponse()
	r.status_code = 200
	return r




