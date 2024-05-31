from django.db import models # type: ignore


  

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


class comport_settings(models.Model):
    com_port = models.CharField(max_length=50)
    baud_rate = models.IntegerField()
    bytesize = models.IntegerField()  
    stopbits = models.IntegerField()
    parity = models.CharField(max_length=50)

    def __str__(self):
        return f"COM Port: {self.com_port}, Baud Rate: {self.baud_rate}"

class mastering_data(models.Model):
    probe_no = models.CharField(max_length=100)
    a = models.FloatField()
    b = models.FloatField()
    e = models.FloatField()
    d = models.FloatField()
    o1 = models.FloatField()
    parameter_name = models.CharField(max_length=100)
    selected_value = models.CharField(max_length=100)
    selected_mastering = models.CharField(max_length=100)
    date_time = models.CharField(max_length=30)  # Change to CharField

    def save(self, *args, **kwargs):
        if self.date_time:  # Format the date and time string with AM/PM information
            self.date_time = self.date_time.strftime("%d/%m/%Y, %I:%M:%S %p")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Probe No: {self.probe_no}, Parameter Name: {self.parameter_name}, DateTime: {self.date_time}"
    

class parameter_settings(models.Model):
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
    utl = models.FloatField()
    ltl = models.FloatField()
    job_dia = models.CharField(max_length=10)
    digits = models.IntegerField()
    mastering = models.FloatField()
    step_no = models.FloatField()
    hide_checkbox = models.BooleanField(default=False)


def __str__(self):
        return f'{self.model_id} - {self.parameter_name}'


class MeasurementData(models.Model):
    parameter_name = models.CharField(max_length=100)
    readings = models.FloatField()
    nominal = models.FloatField()
    lsl = models.FloatField()
    usl = models.FloatField()
    status_cell = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    operator = models.CharField(max_length=100)
    shift = models.CharField(max_length=100)
    machine = models.CharField(max_length=100)
    part_model = models.CharField(max_length=100)
    part_status = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    comp_sr_no = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.parameter_name} - {self.date}"
    
    def save(self, *args, **kwargs):
        if self.date:  # Format the date and time string with AM/PM information
            self.date = self.date.strftime("%d/%m/%Y, %I:%M:%S %p")
        super().save(*args, **kwargs)

