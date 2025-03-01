from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine_type = models.CharField(max_length=255)
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    reminder_interval = models.FloatField()
    created_at = models.DateTimeField(null=True, blank=True)  

    def save(self, *args, **kwargs):
        """Set created_at only if it's a new record"""
        if not self.created_at:
            self.created_at = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage} (User: {self.user.username})"

# New model to track edits and deletions
class ReminderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_id = models.IntegerField()  # Store ID of deleted reminder
    action = models.CharField(max_length=10)  # 'edit' or 'delete'
    old_data = models.JSONField(null=True, blank=True)  # Store old reminder details
    new_data = models.JSONField(null=True, blank=True)  # Store new data if edited
    timestamp = models.DateTimeField(default=now)  # Time of action

    def __str__(self):
        return f"{self.user.username} {self.action} reminder {self.reminder_id} on {self.timestamp}"