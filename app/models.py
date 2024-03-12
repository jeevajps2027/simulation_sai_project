from django.db import models


  
class readings(models.Model):
    probe_id = models.CharField(max_length=50, unique=True)
    low_ref = models.JSONField(default=list)  # Storing a_values as a JSON array
    low_count = models.JSONField(default=list)  # Storing a1_values as a JSON array
    high_ref = models.JSONField(default=list)  # Storing b_values as a JSON array
    high_count = models.JSONField(default=list)  # Storing b1_values as a JSON array
    coefficent = models.JSONField(default=list)  # Storing e_values as a JSON array

class find(models.Model):
    probe_id = models.CharField(max_length=50, unique=True)
    low_ref = models.JSONField(default=list)  # Storing a_values as a JSON array
    low_count = models.JSONField(default=list)  # Storing a1_values as a JSON array
    high_ref = models.JSONField(default=list)  # Storing b_values as a JSON array
    high_count = models.JSONField(default=list)  # Storing b1_values as a JSON array
    coefficent = models.JSONField(default=list)  # Storing e_values as a JSON array

class TableOneData(models.Model):
    part_name = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    part_model = models.CharField(max_length=100)
    part_no = models.CharField(max_length=100)
    hide = models.BooleanField(default=False)    

def __str__(self):
        return self.model_name







class TableTwoData(models.Model):
    batch_no = models.CharField(max_length=100)

class TableThreeData(models.Model):
    machine_no = models.CharField(max_length=100)
    machine_name = models.CharField(max_length=100)

class TableFourData(models.Model):
    operator_no = models.CharField(max_length=100)
    operator_name = models.CharField(max_length=100)

class TableFiveData(models.Model):
    vendor_code = models.CharField(max_length=100)
    email = models.EmailField()

class viewvalues(models.Model):
    model_id = models.CharField(max_length=255)
    parameter_name = models.CharField(max_length=255)



class parameterValue(models.Model):
    model_id = models.CharField(max_length=255)
    parameter_name = models.CharField(max_length=255)
    single_radio = models.BooleanField(default=False)
    analog_zero = models.FloatField(blank=True, null=True)
    reference_value = models.FloatField(blank=True, null=True)
    double_radio = models.BooleanField(default=False)
    high_mv = models.FloatField(blank=True, null=True)
    low_mv = models.FloatField(blank=True, null=True)    
    probe_no = models.FloatField()
    measurement_mode = models.CharField(max_length=50)
    nominal = models.FloatField()
    usl = models.FloatField()
    lsl = models.FloatField()
    mastering = models.FloatField()
    step_no = models.FloatField()
    hide_checkbox = models.BooleanField(default=False)


def __str__(self):
        return f'{self.model_id} - {self.parameter_name}'

class captValue(models.Model):
    model_id = models.CharField(max_length=255)
    parameter_name = models.CharField(max_length=255)
    sr_no = models.IntegerField()
    single_radio = models.BooleanField(default=False)
    analog_zero = models.FloatField(blank=True, null=True)
    reference_value = models.FloatField(blank=True, null=True)
    double_radio = models.BooleanField(default=False)
    high_mv = models.FloatField(blank=True, null=True)
    low_mv = models.FloatField(blank=True, null=True)    
    probe_no = models.FloatField()
    measurement_mode = models.CharField(max_length=50)
    nominal = models.FloatField()
    usl = models.FloatField()
    lsl = models.FloatField()
    mastering = models.FloatField()
    step_no = models.FloatField()
    hide_checkbox = models.BooleanField(default=False)


def __str__(self):
        return f'{self.model_id} - {self.parameter_name}'




class MasterData(models.Model):
    probe_no = models.CharField(max_length=100)
    a = models.FloatField()
    b = models.FloatField()
    parameter_name = models.CharField(max_length=100)
    selected_value = models.CharField(max_length=100)
    selected_mastering = models.CharField(max_length=100)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"Probe No: {self.probe_no}, Parameter Name: {self.parameter_name}, DateTime: {self.date_time}"
