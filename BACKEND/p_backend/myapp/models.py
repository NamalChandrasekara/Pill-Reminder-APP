from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    time =models.TimeField()

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"
    
