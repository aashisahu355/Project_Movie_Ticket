from rest_framework import serializers
from .models import *


# registration serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TUser
        fields = '__all__'
    def create(self, validated_data):
        user = TUser.objects.create(**validated_data)
        user.password = make_password(validated_data['password'])
        user.save()
        return user

# otp 
class OTPVerify_serializer(serializers.Serializer):
    otp=serializers.CharField(max_length=6)

# login 
class LoginSerializer(serializers.Serializer):
    username=serializers.CharField(max_length=50)
    password=serializers.CharField(max_length=50)


# theatre 
class TheaterSer(serializers.ModelSerializer):
    class Meta:
        model = Theatre
        fields = '__all__'


# theatre seatcategory
class TheatreSeatCategorySer(serializers.ModelSerializer):
    class Meta:
        model = TheatreSeatCategory
        fields = '__all__'

# show
class ShowSer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = '__all__'
