from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView

urlpatterns = [

    
    path('',index,name='index'),
    path('about/',about,name='about'),
    path('support/',support,name='support'),


    # login
    path('account/',account,name='account'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # register
    path('register/',Register,name='register'),
    path('RegisterAPI/',RegisterAPI,name='RegisterAPI'),
    
    # verification
    path('verify/',Verify,name='verify'),
    path('verify_otp/',varify_otp,name='verify_otp'),
    

    path('moviedetails<int:id>/',moviedetails,name='moviedetails'),
    path('all_movie/',allMovies,name='all_movie'),
    path('logout_user/',logout_user,name='logout_user'),
    path('show_details<int:id>/',show_details,name='show_details'),
    path('seat_Selection/<int:id>/',seat_Selection,name='seat_Selection'),
    path('booking/<int:show_id>/',booking,name='booking'),
    path('payment/<int:book_id>/',payment,name='payment'),
    path("orders/verify/",verify_payment, name="verify_payment"),
    path('download_ticket_pdf/<int:order_id>/',download_ticket,name='download_ticket_pdf'),
    path('all_bookings/',user_booking_details, name='all_bookings'),
    path('search/',search, name='search'),
    path('cancel_booking/<int:id>/',cancel_bookings,name='cancel_booking')

]

