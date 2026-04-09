from django.db import models
import random

    
# -------------Movie Admin------------------
class MUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField()

class OTP(models.Model):
    user=models.OneToOneField(MUser,on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000,999999))

class AddMovie(models.Model):
    user = models.ForeignKey(MUser,on_delete=models.CASCADE)
    Title = models.CharField(max_length=200)
    Category = models.CharField(max_length=200)
    language = models.CharField(max_length=100)
    duration = models.CharField(max_length=20, help_text="Duration like '2 hr 30 min'")
    poster = models.ImageField(upload_to='media/')
    Trailer = models.FileField(upload_to='media/')
    discription = models.CharField(max_length=1000)
    release_date = models.DateField()



# -------------------User Admin----------------------------------



class UUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=500)
    is_active = models.BooleanField()

class UOTP(models.Model):
    user=models.OneToOneField(UUser,on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000,999999))

