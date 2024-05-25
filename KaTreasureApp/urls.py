from django.urls import path
from KaTreasureApp import views

app_name = 'KaTreasureApp'

urlpatterns = [
    path('', views.index, name='index'),
]