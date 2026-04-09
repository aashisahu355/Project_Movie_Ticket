from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password



# ------------movie admin --------------


# register 
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MUser
        fields = '__all__'
    def create(self, validated_data):
        user = MUser.objects.create(**validated_data)
        user.password = make_password(validated_data['password'])
        user.save()
        return user

# otp verification
class OTPVerify_serializer(serializers.Serializer):
    otp=serializers.CharField(max_length=6)

# login 
class LoginSerializer(serializers.Serializer):
    username=serializers.CharField(max_length=50)
    password=serializers.CharField(max_length=50)

# Add Movie
class AddMovieSer(serializers.ModelSerializer):
    class Meta:
        model = AddMovie
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}  
        }

# update movie
class updateMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddMovie
        fields = ['Category','language' ,'duration','poster','Trailer','discription']




# ---------------------------User Admin------------------------

# user registration
class URegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UUser
        fields = '__all__'
    def create(self, validated_data):
        user = UUser.objects.create(**validated_data)
        user.password = make_password(validated_data['password'])
        user.save()
        return user

# user admin otp verification
class UOTPVerify_serializer(serializers.Serializer):
    otp=serializers.CharField(max_length=6)


# user admin login
class ULoginSerializer(serializers.Serializer):
    username=serializers.CharField(max_length=50)
    password=serializers.CharField(max_length=50)


