from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from django.db.models import Q
from MoviesApp.models import Booking,Order



from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings

from .ser import *
from .models import *

from django.contrib.auth.hashers import check_password

from MovieAdmin.models import AddMovie

import razorpay


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# theatre admin login check decorator
def theatre_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('theatreApp_id'):
            return redirect('taccount')   
        return view_func(request, *args, **kwargs)
    return wrapper


# home page  for admin pannel
def theatre_dashboard(request):
    return render(request,'theatre_dashboard.html')



# -----------------------------theatre--------------------------------------------


# theatre registeration
def tRegister(request):
    return render(request,'Tregister.html')

@api_view(['POST'])
def tRegisterAPI(request):
     if request.method == 'POST':
        serializer= RegisterSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            if TUser.objects.filter(username=username).exists():
                return Response({"error": "User with this username already exist"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
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
                otp_sent=True
                return Response({'message': 'otp send please check email'},status=status.HTTP_200_OK)
            except Exception as e:
                user.delete()
                print("Error : ",e)
        return Response({"error": str(serializer.errors)},status=status.HTTP_400_BAD_REQUEST)


# theatre admin otp verification
def tVerify(request):
    return render(request,'Tverify.html')

@api_view(['POST'])
def tvarify_otp(request):
    otp_serializer = OTPVerify_serializer(data=request.data)
    print("Request data:", request.data) 
    if otp_serializer.is_valid():
        otp_value = otp_serializer.validated_data.get('otp')


        try:
            user = TUser.objects.all().last()
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



# Choose admin type for login
def chooseadmin(request):
    return render(request,'chooseadmin.html')


# Theatre login
def taccount(request):
    return render(request,'tlogin.html')

@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        ser = LoginSerializer(data = request.data)
        if ser.is_valid():
            user = ser.validated_data.get('username')
            password = ser.validated_data.get('password')

            try:
                obj = TUser.objects.get(username = user)
            except TUser.DoesNotExist:
                return Response({'message': 'user not found '},status=status.HTTP_400_BAD_REQUEST)

            if(check_password(password,obj.password)):
                request.session['theatreApp_id'] = obj.id
                return Response({'message':'Login Succesfull'},status=status.HTTP_200_OK)
            else:
                return Response({'message':"Invalid username or password"})
        else:
            return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)



# logout for all admins
def logout(request):
    tadmin_id = request.session.get('theatreApp_id')
    madmin_id = request.session.get('movieApp_id')
    uadmin_id = request.session.get('UserApp_id')
    print(tadmin_id)
    print(madmin_id)
    print(uadmin_id)


    if tadmin_id:
        try:
            del request.session['theatreApp_id']
            return redirect('theatre_dashboard')
        except KeyError as e:
            print(e)
    elif madmin_id:
        try:
            del request.session['movieApp_id']
            return redirect('theatre_dashboard')
        except KeyError as e:
            print(e)
    elif uadmin_id:
        try:
            del request.session['UserApp_id']
            return redirect('theatre_dashboard')
        except KeyError as e:
            
            print(e) 
    else:
        return HttpResponse("<h1>No Login Found....!!!</h1>")




# Add new theatres
@theatre_login_required
def AddTheatre(request):
    admin_id = request.session.get('theatreApp_id') 
    
    if request.method == 'POST':
        name = request.POST['name']
        location = request.POST['location']
        city = request.POST['city']

        theatreApp_id = request.session.get('theatreApp_id')
        obj = TUser.objects.get(id=theatreApp_id)
        Theatre.objects.create(user=obj,name=name,location=location,city=city)
        return redirect('addseatcategory')
    return render(request,'addTheatre.html')


# add seat category to particular theatre
def add_seat_categories(request):
    if request.method == "POST":
        names = request.POST.getlist('category_name[]')
        prices = request.POST.getlist('category_price[]')
        seat_counts = request.POST.getlist('seat_count[]')

        for name, price, seat_count in zip(names, prices,seat_counts):
            theatre = request.session.get('theatreApp_id')
            theatre_obj = Theatre.objects.all().last()
            TheatreSeatCategory.objects.create(theatre=theatre_obj,name=name, price=price ,seat_count=seat_count)
        messages.success(request, "All seat categories added successfully!")
        return redirect('theatre_dashboard')

    return render(request, 'add_seat_category.html',)


# Get all theatres
@theatre_login_required
def get_theatre(request):
    alltheatre = Theatre.objects.all()
    return render(request,'get_theatre.html',{'alltheatre' : alltheatre})


# update theatre detail
def Update_theatre(request,id):
    theatre = Theatre.objects.get(id=id)
    if request.method == 'POST':
        theatre.name = request.POST.get('name')
        theatre.location = request.POST.get('location')
        theatre.city = request.POST.get('city')
        theatre.save()
        return redirect('get_theatre')
    return render(request,'update_theatre.html')


# ---------------------------Show Details-------------------------------



# select theatre for new show
@theatre_login_required
def Select_Theatre(request):
    admin_id = request.session.get('theatreApp_id')
    t_obj = Theatre.objects.filter(user_id = admin_id)
    return render(request,'select_theatre.html',{'t_obj' : t_obj})




# Add show for particular theatre
def addShow(request,id):
    allmovies=AddMovie.objects.all()
    # t_id = request.session.get('theatreApp_id')
    theatre_obj = Theatre.objects.get(id = id)
    if request.method == 'POST':
        
       
        try:    
            movie = request.POST['movie']
            movie_obj = AddMovie.objects.get(id=movie)
            
            show_s_time = request.POST['show_s_time']
            show_e_time = request.POST['show_e_time']
            show_s_date = request.POST['show_s_date']
            show_e_date = request.POST['show_e_date']

            check = Show.objects.filter(theatre = theatre_obj,movie=movie_obj,show_s_time=show_s_time,show_e_time=show_e_time,show_s_date=show_s_date,show_e_date=show_e_date).exists()
            if not check:
                Show.objects.create(theatre = theatre_obj,movie=movie_obj,show_s_time=show_s_time,show_e_time=show_e_time,show_s_date=show_s_date,show_e_date=show_e_date)
            else:
                return JsonResponse({'message' : "Show already exist"})
            return JsonResponse({'message':'successfully added'})
        except Exception as e:
            return JsonResponse({'error': str(e)})    
    return render(request,'add_show.html',{'allmovies':allmovies,'t_obj':theatre_obj})



# get show deatils
@theatre_login_required
def get_show(request):
    allshow = Show.objects.all()
    return render(request,'get_show.html',{'allshow': allshow})



# update show of particular theatre
def Update_show(request,id):
    show = Show.objects.get(id=id)
    alltheatre = Theatre.objects.all()
    allmovies = AddMovie.objects.all()

    if request.method == 'POST':
        movie_id=request.POST.get('movie')
        m_obj = AddMovie.objects.get(id=movie_id)
        show.movie = m_obj

        t_id = request.POST.get('theatre')
        t_obj = Theatre.objects.get(id=t_id)
        show.theatre = t_obj

        new_start = request.POST.get('show_s_date')
        new_end = request.POST.get('show_e_date')

        show.show_s_date = new_start
        show.show_e_date = new_end

        old_start_time = show.show_s_time
        old_end_time = show.show_e_time
        old_start_date = show.show_s_date
        old_end_date = show.show_e_date


        show.show_s_time = request.POST.get('show_s_time')
        show.show_e_time = request.POST.get('show_e_time')
        show.save()

        invalid_bookings = Booking.objects.filter(
                show=show
                    ).filter(
                        Q(date__lt=new_start) | Q(date__gt=new_end)
                )

        time_changed = (old_start_time != show.show_s_time) or (old_end_time != show.show_e_time)

        if time_changed:
            time_conflict_bookings = Booking.objects.filter(
                show=show,
                date__gte=old_start_date,
                date__lte=old_end_date
                )
        else:
            time_conflict_bookings = Booking.objects.none()
        
        all_affected_bookings = invalid_bookings | time_conflict_bookings


        for booking in all_affected_bookings:
            try:
                order = Order.objects.get(book_id=booking)
                payment_id = order.razorpay_payment_id
            except Order.DoesNotExist:
                payment_id = None
            
            if payment_id:
                try:
                    amount = int(float(booking.amount) * 100)  

                    refund = razorpay_client.payment.refund(
                        payment_id,
                        {
                            "amount": amount,
                            "speed": "normal"
                        }
                    )

                    order.status = "refunded"
                    order.save()
                    booking.status = "CANCELLED"
                    booking.save()
                    send_mail(
                    subject="Your booking has been cancelled and charges were refunded ..Please check",
                    message=f"Sorry for the inconvience."
                            f"Your booking for {show.movie.Title} on {booking.date} "
                            f"was cancelled because the show schedule has changed.\nCharges will be refunded in a week ..."
                            f"\nPlease book ticket for another show",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[booking.user.email],
                    fail_silently=False,
                    )
                    

                except Exception as e:
                    print("Refund error:", e)
                return redirect('get_show')
    return render(request,'update_show.html',{'allmovies':allmovies,'alltheatre':alltheatre})





