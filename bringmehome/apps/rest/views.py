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
BVG_MATCH = re.compile('^(conL)|(conD)$')
GEO_MATCH = re.compile('([0-9]{2})\.([0-9]{6}).*') #from BVG website

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
#@jsonview() #testing
def query_way_home(request):

	user_data = json.loads(request.POST['checkin'])
	checkin_id = user_data['id']

	client = foursquare.Foursquare(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, redirect_uri=settings.CALLBACK_URL)

	try:
		user = UserProfile.objects.get(foursquare_id=user_data['user']['id'])
	except Exception:
		raise Http404

	# Apply the returned access token to the client
	client.set_access_token(user.oauth_token)

	return_data = []

	now = datetime.datetime.now() #locale should be set to berlin
	journey_time = now + datetime.timedelta(minutes=60)

	lng = str(user_data['venue']['location']['lng'])
	lat = str(user_data['venue']['location']['lat'])

	lng_match = re.match(GEO_MATCH, lng)
	lat_match = re.match(GEO_MATCH, lat)

	data = urllib.urlencode({
			'REQ0HafasInitialSelection':0,
			'queryDisplayed': True,
			'SID':'A=16@X=%s%s@Y=%s%s@O=Von hier starten' % (lng_match.group(1), lng_match.group(2), lat_match.group(1), lat_match.group(2)), #Checkin location data translated to BVG specs
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

	message = 'Bring me home!'

	for link in links:
		if 'co=C0' in link.get('href'):
			url = BVG_ROOT + link.get('href')
			route_request = urllib2.urlopen(url)
			route_data = BeautifulSoup(route_request.read())

			stages = route_data.find_all('p', {'class': BVG_MATCH})
			for stage in stages:
				fragment = stage.text
				cleaned = fragment.replace('\n', ' ')
				message += cleaned

			break #usually 3 routes, we'll hack it to just query the first route

	#return [message.encode("utf-8")] #testing

	client.checkins.reply(checkin_id, {'text': message.encode("utf-8")}) #add url parameter later

	r = HttpResponse()
	r.status_code = 200
	return r




