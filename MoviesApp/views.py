from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
import requests
from datetime import datetime,timedelta
from django.utils import timezone

from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
import jwt

from .serializer import *

from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from MovieAdmin.models import AddMovie
from theatreApp.models import Theatre,Show,TheatreSeatCategory
import json
from django.http import HttpResponse


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import razorpay

import io


from django.template.loader import get_template
from xhtml2pdf import pisa

from datetime import date, timedelta
from django.db.models import Q



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))




# home page
def index(request):
    allmovies = AddMovie.objects.all()
    recent_movies = AddMovie.objects.order_by('-release_date')[:3]
    for r in recent_movies:
        r.promote = r.release_date > date.today()

    
    cat_wise_movies = list(AddMovie.objects.all())
    cat_wise_movies.reverse()
    data = [cat_wise_movies[i:i + 4] for i in range(0, len(cat_wise_movies), 4)]
    return render(request,'index.html',{'allmovies' : allmovies,'recent_movies':recent_movies,'data':data})    

# about page
def about(request):
    return render(request,'about.html')

# support
def support(request):
    return render(request,'support.html')


# user registration
def Register(request):
    return render(request,'register.html')

@api_view(['POST'])
def RegisterAPI(request):
     if request.method == 'POST':
        serializer= RegisterSerializer(data=request.data)
        print(request.data)
        print(serializer.is_valid())
        if serializer.is_valid():
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
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



# user otp verification
def Verify(request):
    return render(request,'verify.html')

@api_view(['POST'])
def varify_otp(request):
    otp_serializer = OTPVerify_serializer(data=request.data)
    print("Request data:", request.data) 
    if otp_serializer.is_valid():
        otp_value = otp_serializer.validated_data.get('otp')


        try:
            user = User.objects.all().last()
            otp_obj = OTP.objects.filter(user=user).last()

            if otp_obj and otp_obj.otp == otp_value:
                user.is_active = True
                user.save()
                otp_obj.delete()
                return Response({"message" : "verification successfully completed"},status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid otp"},status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message" : "user not found"},status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(otp_serializer.errors,status=status.HTTP_400_BAD_REQUEST)



# User login
def account(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        response = requests.post('http://127.0.0.1:8000/token/',json={'username':username,'password':password})
        print("status code  :",response.status_code)
        if response.status_code == 200:
            token = response.json()
            access= token['access']
            refresh = token['refresh']
            print('token', token,'\n\n\n','access',access,"\n\n\n",'refresh',refresh)
            response_redirect = redirect(next_url if next_url else 'index')
            response_redirect.set_cookie('access',access,httponly=True)
            response_redirect.set_cookie('refresh',refresh,httponly=True)
            return response_redirect
    return render(request,'login.html') 



# logout
def logout_user(request):
    token_key = request.COOKIES.get('access')
    print(token_key)

    if not token_key:
         return HttpResponse("<h1>No Login Found....!!!</h1>")
    response = redirect('index')   
    response.delete_cookie('access')
    return response 



# all movies avilable
def allMovies(request):
    allmovies = AddMovie.objects.all()
    return render(request,'AllMovies.html',{'allmovies' : allmovies})


# particular movie detail
def moviedetails(request,id):
    movie = AddMovie.objects.get(id=id)
    movie.promote = movie.release_date > date.today()
    return render(request,'moviedetail.html',{'movie' : movie})



# show avilable
def show_details(request,id):
    # today = date.today()

    # for display 7 dates from today
    days_list = [ date.today() + timedelta(days=i) for i in range(7)]

    input_date = request.POST.get('date')
    print(date)

    if input_date:
        input_date = date.fromisoformat(input_date)  
        print(input_date)
    else:
        input_date = date.today() 
        print(input_date)
    

    # filter available ones(available 2hours before showtime)
    filtered_shows =[]

    
    close_time = (datetime.now() + timedelta(hours=2))
    all_shows = Show.objects.filter(
        movie_id=id,
        show_s_date__lte=input_date,
        show_e_date__gte=input_date
       )

    
    if input_date == date.today():
        for show in all_shows:
            show_datetime = datetime.combine(input_date, show.show_s_time)

            if show_datetime > close_time:   # ONLY UPCOMING SHOWS
                filtered_shows.append(show)
    else:
        filtered_shows = all_shows
        
        
    
    if 'show_id' in request.POST:
        s_id= int(request.POST.get('show_id'))
        s_date = request.POST.get('s_date')
        print(s_date)
        if s_date:
            request.session['s_date'] = s_date
        else:
            request.session['s_date'] = date.today()
        return redirect(f"/seat_Selection/{s_id}/")
    return render(request,'shows.html',{'shows':filtered_shows,'dates':days_list,'selected_date': input_date})

# seat selction
def seat_Selection(request,id):
    obj = Show.objects.get(id=id)
    user_id = None

    if request.session.get("pending_seats"):
        SeatLock.objects.filter(show=obj, user_id=user_id).delete()
        del request.session["pending_seats"] 

    # getting already booked seats
    s_date = date.fromisoformat(request.session.get("s_date"))
    booked = Booking.objects.filter(show_id=id,date=s_date,status="CONFIRMED").values_list("seats", flat=True)
    
    booked_seats = []
    for b in booked:
        booked_seats.extend(b)
    print(booked_seats)

    # getting locked seat
    active_locks = SeatLock.objects.filter(
        show=obj,
        locked_at__date=s_date,
        locked_at__gte=timezone.now() - timedelta(minutes=10)
    ).values_list("seat", flat=True)

    locked_seats = list(active_locks)

    unavailable_seats = booked_seats + locked_seats

    seat_category=TheatreSeatCategory.objects.filter(theatre=obj.theatre_id)
    seats = {}
    for s in seat_category:
        seats[s.name]={
        "price": s.price,
        "numbers": range(1, s.seat_count + 1)
        }
        
    
    
    if request.method == "POST":
        raw = request.POST.get("seats")
        print("raw :",raw)
        if isinstance(raw, list):
            seat = raw                      
        else:
            seat = json.loads(raw)

        access = request.COOKIES.get('access')
        if not access:
            return redirect(f"/account/?next=/seat_Selection/{obj.id}/")
        token_obj = AccessToken(access)  
        user_id = token_obj['user_id']

        for s in seat:
            if s in unavailable_seats:
                return HttpResponse(f"<h3>Seat {s} is no longer available. Please choose another seat.</h3>")

        for s in seat:
            SeatLock.objects.create(
                show=obj,
                seat=s,
                user_id=user_id
            )

        request.session["pending_seats"] = seat
       
        return redirect(f"/booking/{id}/")

    return render(request,'seat_selection.html',{
                 'seat_category':seat_category,
                 'seats':seats,
                 'show_id':id,
                 'booked': unavailable_seats,
                })

# booking generate
def booking(request,show_id):
    obj = Show.objects.get(id=show_id)
    t_obj = Theatre.objects.get(id=obj.theatre_id)
    m_obj = AddMovie.objects.get(id=obj.movie_id)
    
    seats = request.session.get("pending_seats") 

    s_date = date.fromisoformat(request.session["s_date"])
    print(s_date)

    
    
    total_price = 0
    cat_dic=[]
    
    for seat in seats:
        category, num = seat.split("-")
        cat_dic.append(seat)
        cat_obj = TheatreSeatCategory.objects.get(name__iexact= category,theatre=t_obj)
        total_price += cat_obj.price
    if request.method == 'POST':
            access = request.COOKIES.get('access')

            token_obj = AccessToken(access)  
            user_id = token_obj['user_id']

            user = User.objects.get(id=user_id)
            booking=Booking.objects.create(user=user,show=obj,amount=total_price,seats=seats,status="PENDING",date = s_date)
            if "pending_seats" in request.session:
                del request.session["pending_seats"]
                del request.session["s_date"]
            return redirect(f"/payment/{booking.id}/")

    
           
    return render(request,'booking.html', {
           't_obj':t_obj,
           'm_obj':m_obj,
           'seat':seat,
           'obj':obj,
           'total_price':total_price,
           'cat_dic':cat_dic,
           'date':s_date

           })


# payment 
def payment(request,book_id):
    booking = Booking.objects.get(id=book_id)
    show_obj = booking.show
    seats = booking.seats           # JSON list 
    user_id = booking.user_id
    try:
        amount = int(booking.amount) * 100  # Convert to paise
        currency = "INR"
        print("KEY:", settings.RAZORPAY_KEY_ID)

            # Create order in Razorpay
        razorpay_order = razorpay_client.order.create(
            dict(amount=amount, currency=currency, payment_capture=1)
        )

            #Save order in database
        order = Order.objects.create(
                book_id = booking,
                amount=amount,
                currency=currency,
                razorpay_order_id=razorpay_order["id"]
        )

            #Pass order data to template for checkout
        context = {
                "order_id": razorpay_order["id"],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "amount": amount,
                "currency": currency,
        }



        return render(request, "checkout.html", context)

    except requests.exceptions.ConnectTimeout:
        SeatLock.objects.filter(
                        show=show_obj,
                        seat__in=seats,
                        user_id=user_id
                    ).delete()
        # booking.delete()
        return JsonResponse({"error": "Connection to Razorpay timed out. Check your internet."}, status=500)
     
    except Exception as e:
        # booking.delete()
        return JsonResponse({"error": str(e)}, status=500)

    return render(request, "payment.html")


# payment verification
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":

        data = request.POST
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        
        booking = order.book_id
        show_obj = booking.show
        seats = booking.seats           # JSON list 
        user_id = booking.user_id  

        active_locks = SeatLock.objects.filter(
                show=show_obj,
                seat__in=seats,
                user_id=user_id,
                locked_at__gte=timezone.now() - timedelta(minutes=10)
            )

        print(active_locks)
        print(seats)

        if active_locks.count() != len(seats):
                return HttpResponse("<h3>Some seats were taken by another user during payment!</h3>")
        else:


            try:
                print("happy")
                # Verify payment signature
                razorpay_client.utility.verify_payment_signature({
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                })

                print("hello")

                order.status = "paid"

                order.razorpay_payment_id = razorpay_payment_id
                order.razorpay_signature = razorpay_signature
                payment = razorpay_client.payment.fetch(razorpay_payment_id)
                order.payment_status = payment.get("status", "unknown")
                order.book_id.status = "confirmed"
                order.book_id.save()
                order.save()
                SeatLock.objects.filter(
                        show=show_obj,
                        seat__in=seats,
                        user_id=user_id
                    ).delete()


                pdf_bytes = generate_ticket_pdf(order)
                
                email = EmailMessage(
                    subject="Booking Confirmed",
                    body=f"""Your booking was confirmed succesfully.\n\nBooking Details :\n  Movie : {order.book_id.show.movie.Title}\n  Thetare : {order.book_id.show.theatre.name}\n  Location : {order.book_id.show.theatre.location}\n  Date : {order.book_id.date}\n  Showtime : {order.book_id.show.show_s_time}\n  Seats : { order.book_id.seats}\nCancellation is allowed only up to 3 hours before the show starts\n\nHave a nice day...Thank you..!!!""",
                    from_email=settings.EMAIL_HOST_USER,
                    to=[order.book_id.user.email]
                    )
                email.attach(f"ticket_{order.id}.pdf", pdf_bytes, "application/pdf")
                email.send()
                return render(request, "success.html", {"status": order.status,"order":order})
            except Exception as e:
                
                order.status = "failed"
                order.save()
                order.book_id.delete()
                SeatLock.objects.filter(
                        show=show_obj,
                        seat__in=seats,
                        user_id=user_id
                    ).delete()
    
    return JsonResponse({"error": "Invalid request"}, status=400)


# generate ticket pdf
def generate_ticket_pdf(order):

    # Load HTML template
    template_path = "ticket.html"
    template = get_template(template_path)
    html = template.render({'order': order})

    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse("Error generating ticket")
    

    return pdf_buffer.getvalue()

    


# download ticket
def download_ticket(request,id):
    order = Order.objects.get(id=order_id)

    pdf_bytes = generate_ticket_pdf(order)

    # Create response
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="ticket_{order_id}.pdf"'

    return response


# user bookings
def user_booking_details(request):
    try:
        access = request.COOKIES.get('access')


        token_obj = AccessToken(access)  
        user_id = token_obj['user_id']
    except Exception as e:
        return redirect('account')

    all_bookings = Booking.objects.filter(user_id=user_id)
    now = datetime.today()

    for booking in all_bookings:
        show_datetime = datetime.combine(booking.date, booking.show.show_s_time)

        # for download button
        booking.is_show_over = now > show_datetime
        if(booking.status.upper() == 'CONFIRMED') and not booking.is_show_over:
            booking.order_id = Order.objects.get(book_id = booking.id)
        else:
            booking.order_id = None
        
        # for allow cancellation
        cancel_deadline = show_datetime - timedelta(hours=3)
        booking.can_cancel = ( now < cancel_deadline and booking.status.upper() == 'CONFIRMED')
                
    return render(request,'all_bookings.html',{'all_bookings': all_bookings})

    


# cancel bookings
def cancel_bookings(request,id):
    try:
        order = Order.objects.get(book_id_id=id)
        print(order)
    except Order.DoesNotExist:
        print("error")

    
    if order.payment_status != "captured":
        return JsonResponse({"error": "Payment not captured, refund not possible"}, status=400)

    payment_id = order.razorpay_payment_id
    print(payment_id)
    payment = razorpay_client.payment.fetch(payment_id)
    method = payment.get("method")
    if method == "upi":
        days = "within 24 hours"
    elif method == "card":
        days = "within 3-7 days"
    elif method == "wallet":
        days = " in your Wallet withhin 3 days"
    print(payment["status"])
    tickets = len(order.book_id.seats)
    print(order.amount)
    amount = int(order.amount) - tickets*5000
    print(amount)

    if payment_id:
        try:

            refund = razorpay_client.payment.refund(
                payment_id,
                {
                    "amount" : amount,
                    
                }
            )

            print(refund)

            order.status = "refunded"
            order.payment_status = "refunded"
            order.save()

            order.book_id.status = 'CANCELLED'
            order.book_id.save()
            send_mail(
                    subject="Booking Cancelled",
                    message=f"Your booking for {order.book_id.show.movie.Title} on {order.book_id.date} "
                            f"was cancelled succesfully.\n\nTotal Charges you paid : {(order.amount)/100}\n\n Total cancellation charges : {(order.amount-amount)/100}.\n\nRemaining {amount/100} Rs will be refunded {days}...!!"
                            f"\nHave a nice day...Thank you..!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.book_id.user.email],
                    fail_silently=False,
                )



            return JsonResponse({'message' : "Successfully Cancelled \nCheck mail....."},status=200)


        except Exception as e:
            print(e)
            return JsonResponse({'error' : str(e)},status=400)




# search function 
def search(request):
    movie = request.POST.get('movie')
    results = AddMovie.objects.filter(Q(Title__icontains=movie) | Q(discription__icontains=movie) | Q(Category__icontains=movie)) if movie else []
    return render(request, 'search.html', {'results': results, 'movie': movie})


                
    
        
    







