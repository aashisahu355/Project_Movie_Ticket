from django.urls import path
from .views import *
from .reportviews import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
urlpatterns = [
    path('',theatre_dashboard,name='theatre_dashboard'),
    
    # login
    path('chooseadmin/',chooseadmin,name='chooseadmin'),
    path('taccount/',taccount,name='taccount'),
    path('tlogin2/',login_view,name='tlogin2'),

    # register
    path('tregister/',tRegister,name='tregister'),
    path('tRegisterAPI/',tRegisterAPI,name='tRegisterAPI'),
    path('tverify/',tVerify,name='tverify'),
    path('tverify_otp/',tvarify_otp,name='tverify_otp'),

    # logout
    path('logout/',logout,name='logout'),

    # theatre
    path('addtheatre/',AddTheatre,name='addtheatre'),
    path('get_theatre/',get_theatre,name='get_theatre'),
    path('addseatcategory/',add_seat_categories,name='addseatcategory'),
    path('update_theatre/<int:id>/',Update_theatre,name='update_theatre'),


    # show 
    path('addshow<int:id>/',addShow,name='addshow'),
    path('get_show/',get_show,name='get_show'),
    path('update_show/<int:id>/',Update_show,name='update_show'),
    
    # theatre reports 
    path('select_theatre/',Select_Theatre,name='select_theatre'),
    path('theatre_report/<int:id>/',theatre_sales_report,name='theatre_report'),
    path('select_theatre_for_report/',Select_Theatre_For_Report,name='select_theatre_for_report'),
    path('select_show/',select_show,name='select_show'),
    path('show_bookings/<int:id>/',booking_details,name='show_bookings'),


    
]
