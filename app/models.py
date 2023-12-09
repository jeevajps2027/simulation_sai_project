from django.db import models


class Details(models.Model):
    type = models.CharField(max_length=20,default='',null=False)
    name = models.CharField(max_length=20,default='',null=False)
  
class getvalues(models.Model):
    probe_id = models.CharField(max_length=50, unique=True)
    a_values = models.JSONField(default=list)  # Storing a_values as a JSON array
    a1_values = models.JSONField(default=list)  # Storing a1_values as a JSON array
    b_values = models.JSONField(default=list)  # Storing b_values as a JSON array
    b1_values = models.JSONField(default=list)  # Storing b1_values as a JSON array
    e_values = models.JSONField(default=list)  # Storing e_values as a JSON array
