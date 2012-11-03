from django.db import models

class UserProfile(models.Model):
	foursquare_id = models.IntegerField(primary_key=True)
	address = models.CharField(max_length=500)