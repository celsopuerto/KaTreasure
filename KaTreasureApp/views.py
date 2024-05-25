from django.http import HttpResponse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth as django_auth
from KaTreasureApp.firebase_config import config
import pyrebase
import firebase_admin
from django.core.mail import send_mail
from firebase_admin import credentials
from firebase_admin import auth
from google.cloud import storage

# pyrebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()
authn = firebase.auth()
storage_client = storage.Client()

# admin firebase
cred = credentials.Certificate('firebase-sdk.json')
firebase_admin.initialize_app(cred)

# Create your views here.
def index(request):
    return HttpResponse("Firebase.")
