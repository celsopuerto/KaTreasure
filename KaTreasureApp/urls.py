from django.urls import path
from KaTreasureApp import views

app_name = 'KaTreasureApp'

urlpatterns = [
    path('base', views.base, name='base'),
    path('home', views.home, name='home'),
    path('availability', views.availability, name='availability'),
    path('create-room/', views.create_room, name='create-room'),
    path('book-room', views.book_room, name='book-room'),
    path('all-rooms/', views.all_rooms, name='all-rooms'),
    path('signin', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('contactus', views.contactus, name='contactus'),
]