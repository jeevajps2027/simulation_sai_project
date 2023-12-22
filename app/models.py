from django.db import models


  
class probecalibration(models.Model):
    probe_id = models.CharField(max_length=50, unique=True)
    low_ref = models.JSONField(default=list)  # Storing a_values as a JSON array
    low_count = models.JSONField(default=list)  # Storing a1_values as a JSON array
    high_ref = models.JSONField(default=list)  # Storing b_values as a JSON array
    high_count = models.JSONField(default=list)  # Storing b1_values as a JSON array
    coefficent = models.JSONField(default=list)  # Storing e_values as a JSON array

class partTable(models.Model):
    part_name = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    part_model = models.CharField(max_length=100)
    part_no = models.CharField(max_length=100)    

class batchTable(models.Model):
    batch_no = models.CharField(max_length=100)

class machineTable(models.Model):
    machine_no = models.CharField(max_length=100)
    machine_name = models.CharField(max_length=100)

class operatorTable(models.Model):
    operator_no = models.CharField(max_length=100)
    operator_name = models.CharField(max_length=100)

class vTable(models.Model):
    vendor_code = models.CharField(max_length=100)
    email = models.EmailField()

