from django.db import models


class Details(models.Model):
    type = models.CharField(max_length=20,default='',null=False)
    name = models.CharField(max_length=20,default='',null=False)
  
class probecalibration(models.Model):
    probe_id = models.CharField(max_length=50, unique=True)
    low_ref = models.JSONField(default=list)  # Storing a_values as a JSON array
    low_count = models.JSONField(default=list)  # Storing a1_values as a JSON array
    high_ref = models.JSONField(default=list)  # Storing b_values as a JSON array
    high_count = models.JSONField(default=list)  # Storing b1_values as a JSON array
    coefficent = models.JSONField(default=list)  # Storing e_values as a JSON array

