from django.db import models
from MovieAdmin.models import AddMovie
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


# Create your models here.
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

import random


#Theatre admin registration
class TUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=500)
    is_active = models.BooleanField()


# otp model 
class OTP(models.Model):
    user=models.OneToOneField(TUser,on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000,999999))


# Theatre
class Theatre(models.Model):
    user = models.ForeignKey(TUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    city = models.CharField(max_length=50)


# Theatre seatcategory
class TheatreSeatCategory(models.Model):
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    name = models.CharField(max_length=50) 
    price = models.DecimalField(max_digits=8, decimal_places=2)
    seat_count = models.IntegerField()


# show 
class Show(models.Model):
    movie = models.ForeignKey(AddMovie,on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre,on_delete=models.CASCADE)
    show_s_date = models.DateField()
    show_e_date = models.DateField()
    show_s_time = models.TimeField()
    show_e_time = models.TimeField()







