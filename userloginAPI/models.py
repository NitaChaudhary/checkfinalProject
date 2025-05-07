from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

class NewUser(AbstractUser):

    id = models.CharField(max_length= 60, primary_key=True)
    user_birthdate = models.DateField(null=True, blank=True)
    user_mobileno = models.CharField(max_length=20, null=True, blank=True)
    user_gender = models.JSONField( null=True, blank=True)
    user_address = models.TextField(null=True, blank=True)
    user_country = models.JSONField(null=True, blank=True)
    user_description = models.TextField(null=True, blank=True)
    user_is_verified = models.BooleanField(default=False)
    user_is_loggedin = models.BooleanField(default=False)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
class UserEmailVerification(models.Model):
    
    class Meta:
        db_table = "nfc_email_verification"

    user = models.OneToOneField(NewUser, on_delete=models.CASCADE, primary_key=True)
    OTP_verify = models.CharField(max_length = 10, blank=False, null=False)
    expire_time = models.DateTimeField(default= datetime.datetime.now())


