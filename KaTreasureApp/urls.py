from django.urls import path
from KaTreasureApp import views, dashboard

app_name = 'KaTreasureApp'

urlpatterns = [
    # APP
    path('', views.base, name='base'),
    path('home', views.home, name='home'),
    path('availability', views.availability, name='availability'),
    path('create-room/', views.create_room, name='create-room'),
    path('book-room', views.book_room, name='book-room'),
    path('confirm-booking', views.confirm_booking, name='confirm-booking'),
    path('fetch-room-data/', views.fetch_room_data, name='fetch-room-data'),
    path('all-rooms/', views.all_rooms, name='all-rooms'),
    path('contactus', views.contactus, name='contactus'),

    # AUTH
    path('signin', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    
    # DASHBOARD
    path('dashboard/home', dashboard.home, name='dashboard'),
]