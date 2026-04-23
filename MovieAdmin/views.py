
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password


from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings


from .serializer import *
from .models import *
from theatreApp.models import Theatre,Show

# login check decorator
def movie_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('movieApp_id'):
            return redirect('maccount')
        return view_func(request, *args, **kwargs)
    return wrapper


# movie admin registration
def mRegister(request):
    return render(request,'mregister.html')

@api_view(['POST'])
def mRegisterAPI(request):
    
    if request.method == 'POST':
        ser= RegisterSerializer(data=request.data)
        
        
        if ser.is_valid():
            username = ser.validated_data.get("username")
        
            if MUser.objects.filter(username=username).exists():
                return Response({'error': "User with this username already exist"},status=status.HTTP_400_BAD_REQUEST)
        
            user = ser.save()
            otp_code = OTP.generate_otp()
            OTP.objects.create(user=user,otp=otp_code)

            subject ="Your one time Password dont share it with anyone"
            message = f" OTP : {otp_code}"
            recipient = user.email

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [recipient],
                    fail_silently=False 
                )
                return Response({'message': 'otp send please check email'},status=status.HTTP_200_OK)
            
            except Exception as e:
                user.delete()
                print("Error : ",e)
        return Response({'error': str(ser.errors)},status=status.HTTP_400_BAD_REQUEST)



# movie admin  otp verification
def mVerify(request):
    return render(request,'mverify.html')

@api_view(['POST'])
def mvarify_otp(request):
    otp_serializer = OTPVerify_serializer(data=request.data)
    print("Request data:", request.data) 
    
    if otp_serializer.is_valid():
        otp_value = otp_serializer.validated_data.get('otp')


        try:
            user = MUser.objects.all().last()
            otp_obj = OTP.objects.filter(user=user).last()

            if otp_obj and otp_obj.otp == otp_value:
                user.is_active = True
                user.save()
                otp_obj.delete()
                return Response({"message" : "verification successfully completed"},status=status.HTTP_200_OK)
            
            else:
                return Response({"message" : "Invalid otp"},status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"message" : e },status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response(otp_serializer.errors,status=status.HTTP_400_BAD_REQUEST)




# Movie admin login 
def maccount(request):
    return render(request,'mlogin.html')

@api_view(['POST'])
def mlogin_view(request):
    if request.method == 'POST':
        ser = LoginSerializer(data = request.data)
        
        if ser.is_valid():
            user = ser.validated_data.get('username')
            password = ser.validated_data.get('password')

            try:
                obj = MUser.objects.get(username = user)
            except MUser.DoesNotExist:
                return Response({'message': 'user not found '},status=status.HTTP_400_BAD_REQUEST)

            
            

            if(check_password(password,obj.password)):
                request.session['movieApp_id'] = obj.id
                return Response({'message':'Login Succesfull'},status=status.HTTP_200_OK)
            else:
                return Response({'message':"Invalid username or password"})
        else:
            return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)





# get all movie details
@movie_login_required
def get_movie(request):
    allmovies = AddMovie.objects.all()
    return render(request,'get_movie.html',{'allmovies' : allmovies})






# Add Movie
@movie_login_required
def add_movie(request):
    return render(request,'AddMovie.html')

@api_view(['POST'])
def add_movie_api(request):
    movie_id = request.session.get('movieApp_id')
    ser = AddMovieSer(data=request.data)
    print(request.data)
    print("Check:",ser.is_valid())
    if ser.is_valid():
        ser.save(user_id=movie_id)
        return Response({'message': 'Successfully Added'},status=status.HTTP_200_OK)
    else:
        print(ser.errors)
        return Response({'error': ser.errors},status=status.HTTP_400_BAD_REQUEST)



# delete movie
def del_movie(request,id):
    movie = AddMovie.objects.get(id=id)
    movie.delete()
    return redirect('get_movie')



# update movie
def update_movie(request,id):
    movie = AddMovie.objects.get(id=id)
    if request.method == 'POST':
        movie.Category = request.POST.get('Category')
        movie.language = request.POST.get('language')
        movie.duration = request.POST.get('duration')
        movie.release_date = request.POST.get('release_date')
        movie.poster = request.FILES['poster']
        movie.Trailer = request.FILES['Trailer']
        movie.discription = request.POST.get('discription')
        movie.save()
        return redirect('get_movie')
    return render(request,'update_movie.html',{'movie': movie})



# ---------------------User Admin Views------------------------


# user admin registration
def uRegister(request):
    return render(request,'uregister.html')

@api_view(['POST'])
def uRegisterAPI(request):
     if request.method == 'POST':
        ser= URegisterSerializer(data=request.data)
        print(request.data)
        print(ser.is_valid())
        
        if ser.is_valid():
            username=ser.validated_data.get("username")
            if UUser.objects.filter(username=username).exists():
                return Response({"error":"user with this username already exists"},status=status.HTTP_400_BAD_REQUEST)
            
            user = ser.save()
            
            otp_code = UOTP.generate_otp()
            print(otp_code)
            UOTP.objects.create(user=user,otp=otp_code)
            print("saved")

            subject ="Your one time Password dont share it with anyone"
            message = f" OTP : {otp_code}"
            recipient = user.email
            print(recipient)
            print(settings.EMAIL_HOST_USER)

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [recipient],
                    fail_silently=False 
                )
                return Response({'message': 'otp send please check email'},status=status.HTTP_200_OK)
            
            except Exception as e:
                user.delete()
                print("Error : ",e)
        return Response({"error": str(ser.errors)},status=status.HTTP_400_BAD_REQUEST)


# user admin otp verification
def uVerify(request):
    return render(request,'uverify.html')

@api_view(['POST'])
def uvarify_otp(request):
    otp_serializer = UOTPVerify_serializer(data=request.data)
    print("Request data:", request.data) 
    
    if otp_serializer.is_valid():
        otp_value = otp_serializer.validated_data.get('otp')


        try:
            user = UUser.objects.all().last()
            otp_obj = UOTP.objects.filter(user=user).last()

            if otp_obj and otp_obj.otp == otp_value:
                user.is_active = True
                user.save()
                otp_obj.delete()
                return Response({"message" : "verification successfully completed"},status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid otp"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : e },status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(otp_serializer.errors,status=status.HTTP_400_BAD_REQUEST)



# user admin login 
def uaccount(request):
    return render(request,'ulogin.html')


@api_view(['POST'])
def ulogin_view(request):
    if request.method == 'POST':
        ser = ULoginSerializer(data = request.data)
        if ser.is_valid():
            user = ser.validated_data.get('username')
            password = ser.validated_data.get('password')

            try:
                obj = UUser.objects.get(username = user)
            except UUser.DoesNotExist:
                return Response({'message': 'user not found '},status=status.HTTP_400_BAD_REQUEST)

            
            

            if(check_password(password,obj.password)):
                request.session['UserApp_id'] = obj.id
                return Response({'message':'Login Succesfull'},status=status.HTTP_200_OK)
            else:
                return Response({'message':"Invalid username or password"})
        else:
            return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)


# user detail
def get_user(request):
    u_id = request.session.get('UserApp_id')
    if not u_id:
        return redirect('uaccount')
    alluser = User.objects.all()
    return render(request,'get_user.html',{'alluser' : alluser})

# user deactive
def deactivate(request,id):
    user = User.objects.get(id=id)
    user.is_active= False
    user.save()
    return redirect('get_user')


# user active
def activate(request,id):
    user = User.objects.get(id=id)
    user.is_active = True
    user.save()
    return redirect('get_user')



# ----------------Theatre/show------------------------------


# delete theatre
def del_theatre(request,id):
    theatre = Theatre.objects.get(id=id)
    theatre.delete()
    return redirect('get_theatre')


# delete show
def del_show(request,id):
    show = Show.objects.get(id=id)
    show.delete()
    return redirect('get_show')

    