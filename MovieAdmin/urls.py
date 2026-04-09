from django.urls import path
from theatreApp.views import get_theatre
from .views import *
from .report_view import *


urlpatterns = [

   

    # movie admin
    path('maccount/',maccount,name='maccount'),
    path('mregister/',mRegister,name='mregister'),
    path('mRegisterAPI/',mRegisterAPI,name='mRegisterAPI'),
    path('mverify/',mVerify,name='mverify'),
    path('mverify_otp/',mvarify_otp,name='mverify_otp'),
    path('mlogin2/',mlogin_view,name='mlogin2'),
     path('add_movie/',add_movie,name='add_movie'),
    path('add_movie_api/',add_movie_api,name='add_movie_api'),
    path('get_movie/',get_movie,name='get_movie'),
    path('del_movie/<int:id>/',del_movie,name='del_movie'),
    path('update_movie/<int:id>/',update_movie,name='update_movie'),


    # user admin
    path('uaccount/',uaccount,name='uaccount'),
    path('uregister/',uRegister,name='uregister'),
    path('uRegisterAPI/',uRegisterAPI,name='uRegisterAPI'),
    path('uverify/',uVerify,name='uverify'),
    path('uverify_otp/',uvarify_otp,name='uverify_otp'),
    path('ulogin2/',ulogin_view,name='ulogin2'),
    path('get_user/',get_user,name='get_user'),
    path('deactivate/<int:id>/',deactivate,name='deactivate'),
    path('activate/<int:id>/',activate,name='activate'),


    # report
    path('movie_report/<int:id>/',movie_sales_report,name='movie_report'),
    path('select_movie_for_report/',Select_Movie_For_Report,name='select_movie_for_report'),

    #theatre/show
    path('del_theatre/<int:id>/',del_theatre,name='del_theatre'),
    path('del_show/<int:id>/',del_show,name='del_show'),

    


]
 