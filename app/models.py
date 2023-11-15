from django.db import models

class SerialData(models.Model):
    data = models.CharField(max_length=255)
