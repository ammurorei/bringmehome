import uuid
from django.db import models

class UserProfile(models.Model):
	foursquare_id = models.IntegerField(primary_key=True)
	uuid = models.CharField(default=str(uuid.uuid1().int), max_length=100)
	address = models.CharField(max_length=500)