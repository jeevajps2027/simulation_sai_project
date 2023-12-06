from django.db import models


class Details(models.Model):
    type = models.CharField(max_length=20,default='',null=False)
    name = models.CharField(max_length=20,default='',null=False)
  
