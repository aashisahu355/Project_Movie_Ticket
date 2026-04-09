from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from MovieAdmin.models import AddMovie



# inbuiltt user model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name' , 'last_name' ,'username','email']


# user registration
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['first_name','last_name','email','username','password']
    def create(self,validated_data):
        user = User.objects.create_user(**validated_data,is_active = False)
        return user

# user verification
class OTPVerify_serializer(serializers.Serializer):
    otp=serializers.CharField(max_length=6)


# user login
class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(write_only=True)



#user orders 
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        

