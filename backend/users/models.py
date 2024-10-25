
from django.db import models
from django.contrib.auth.models import User  # Ensure this import is present


class Caregiver(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

class Patient(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    cognitive_state = models.CharField(max_length=50)
    caregiver = models.ForeignKey(Caregiver, on_delete=models.CASCADE)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    dob = models.DateField()
class UserMemory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.TextField()


    class Meta:
        unique_together = ('user', 'key')

    def __str__(self):
        return f"{self.key}: {self.value}"
    
class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    reminder_text = models.TextField()

    def __str__(self):
        return f"{self.user} - {self.date}: {self.reminder_text}"


# Create your models here.
