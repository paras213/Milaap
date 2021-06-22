from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
class Member(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
	name=models.CharField(max_length=70)
	mobilenumber=models.IntegerField()
	gender=models.CharField(max_length=10)
	address=models.CharField(max_length=100)
	zip1=models.IntegerField()
	image=models.ImageField(upload_to='profile_image',blank=False)
	trained=models.BooleanField(default=False)
	missing = JSONField(default=dict)
	def __str__(self):
		return self.name
#class lost(models.Model):
#	user = models.ForeignKey(esehi,on_delete=models.CASCADE,null=True)
#	name=models.CharField(max_length=70)
#	mobilenumber=models.IntegerField()
#	gender=models.CharField(max_length=10,default='male')
#	address=models.CharField(max_length=100,default='Made')
#	zip1=models.IntegerField()
#	image=models.ImageField(upload_to='profile_image',blank=False)
#	def __str__(self):
#		return self.name
