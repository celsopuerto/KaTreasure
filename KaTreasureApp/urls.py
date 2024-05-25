from django.urls import path
from . import views

app_name = 'KaTreasureApp'

urlpatterns = [
    path('base/', views.base, name='base'),
    path('contactus/', views.contactus, name='contactus'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('', views.home, name="home"),
]