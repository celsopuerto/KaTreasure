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

#pyrebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()
authn = firebase.auth()

#admin firebase
cred = credentials.Certificate('firebase-sdk.json')
firebase_admin.initialize_app(cred)

# Create your views here.
@login_required
def base(request):
    uid = request.session.get('uid')
    if uid:
        usermain = db.child("users").child(uid).get().val()
        print("Signed in: ", usermain)
        print("CELSGOD")
    return render(request, 'base/base.html')

def contactus(request):
    return render(request, 'core/contactus.html')

def login(request):
    return render(request, 'auth/login.html')

def signup(request):
    return render(request, 'auth/signup.html')

def logout(request):
    django_auth.logout(request)
    messages.success(request, "Logged out.")
    return redirect('KaTreasureApp:login')

def forgot_password(request):
    return render(request, 'auth/forgot_password.html')

def home(request):
    return render(request, 'core/home.html')