from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth as django_auth
from KaTreasureApp.firebase_config import config
from django.core.mail import send_mail
from google.cloud import storage as store
from datetime import datetime
from .services import get_room_by_id, get_user_info

# firebase_config.py
import pyrebase
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Path to your firebase-sdk.json file
FIREBASE_CREDENTIALS_PATH = BASE_DIR / 'firebase-sdk.json'

# Ensure the file exists
if not FIREBASE_CREDENTIALS_PATH.exists():
    raise FileNotFoundError(f"Firebase credentials file not found at {FIREBASE_CREDENTIALS_PATH}")

# Firebase setup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

# pyrebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()
authn = firebase.auth()
storage = firebase.storage()

# admin firebase
cred = credentials.Certificate(str(FIREBASE_CREDENTIALS_PATH))
firebase_admin.initialize_app(cred)

# Create your views here.
def base(request):
    uid = request.session.get('uid')
    if uid:
        usermain = db.child("users").child(uid).get().val()
        print("Signed in: ", usermain)
        print("CELSGOD")
    
    return redirect('KaTreasureApp:home')
    # return render(request, 'base/base.html')

def home(request):
    authenticated = False
    info = None

    try:
        idToken = request.session.get('uid')
        if idToken:
            info = get_user_info(idToken)
            if info:
                authenticated = True
    except Exception as e:
        error = str(e)
        if 'INVALID_ID_TOKEN' in error:
            return redirect('KaTreasureApp:logout')
            # messages.success(request, 'Your Token has expired. Please login again')
            print('Your Token has expired. Please login again')
    except Exception as e:
        error = str(e)
        if 'INVALID_ID_TOKEN' in error:
            return redirect('KaTreasureApp:logout')
            # messages.success(request, 'Your Token has expired. Please login again')
            print('Your Token has expired. Please login again')

    if request.method == 'POST':
        check_in = request.POST.get('check-in')
        adults = request.POST.get('adults')
        child = request.POST.get('child')
        time_slot = request.POST.get('time-slot')

        # Store form data in session
        request.session['check_in'] = check_in
        request.session['adults'] = adults
        request.session['child'] = child
        request.session['time-slot'] = time_slot

        # Perform availability check logic

        return redirect('KaTreasureApp:availability')

    return render(request, 'core/home.html', {'info': info, 'authenticated': authenticated})

def availability(request):
    authenticated = False
    info = None

    try:
        idToken = request.session.get('uid')
        if idToken:
            info = get_user_info(idToken)
            if info:
                authenticated = True
    except Exception as e:
        error = str(e)
        if 'INVALID_ID_TOKEN' in error:
            return redirect('KaTreasureApp:logout')
            # messages.success(request, 'Your Token has expired. Please login again')
            print('Your Token has expired. Please login again')
        
    check_in = request.session.get('check_in')
    adults = request.session.get('adults')
    child = request.session.get('child')
    time_slot = request.session.get('time-slot')

    if request.method == 'POST':
        room_num = request.POST.get('room_num')
        time_slot = request.POST.get('time-slot') # day-use / night-use
        checkin = request.POST.get('check-in') # Mm/Dd/Yyyy
        room_type = request.POST.get('room-type') # aircon / non-aircon
        adult_count = int(request.POST.get('adult-count', 1)) #adult-count
        children_count = int(request.POST.get('children-count', 0)) #children-count
        authenticated = request.user.is_authenticated

        # Convert the date format to Mm-Dd-Yyyy for Firebase
        # checkin_formatted = checkin.split('-')
        # checkin_date = f"{checkin_formatted[0]}-{checkin_formatted[1]}-{checkin_formatted[2]}"
        
        # Convert the date format to Mm-Dd-Yyyy for Firebase
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').strftime('%m-%d-%Y')
        
        # Check if the selected date is before today
        if datetime.strptime(checkin, '%Y-%m-%d') < datetime.now():
            messages.error(request, "Check-In date must not be before today!")
            return render(request, 'core/check-availability.html', {
                'rooms': [],
                'room_count': 0,
                'filtered_data': [],
                'check_in': check_in,
                'time_slot': time_slot,
                'adults': adult_count,
                'child': children_count,
                'room_type': room_type,
                'info': info,
                'authenticated': authenticated,
                'error': 'Selected date cannot be before today.'
            })

        try:
            # Get all room data
            rooms = db.child("rooms").get().val()  # Fetching all room data
            
            if not rooms:
                return render(request, 'core/check-availability.html', {
                    'rooms': [],
                    'room_count': 0,
                    'filtered_data': [],
                    'check_in': checkin,
                    'time_slot': time_slot,
                    'adults': adult_count,
                    'child': children_count,
                    'room_type': room_type,
                    'info': info,
                    'authenticated': authenticated
                })
            
            filtered_data = []
            
            for room_id, room_data in rooms.items():
                if room_data.get('type') == room_type:
                    bookings = room_data.get('bookings', {})
                    # Default availability for both time slots
                    day_available = True
                    night_available = True

                    if room_data.get('max_adults') < adult_count:
                        continue
                    if room_data.get('max_children') < children_count:
                        continue

                    if checkin in bookings:
                        if 'day' in bookings[checkin]:
                            day_available = bookings[checkin]['day'].get('availability', False)
                        if 'night' in bookings[checkin]:
                            night_available = bookings[checkin]['night'].get('availability', False)

                    # If the date does not exist, the room is available
                    if checkin not in bookings:
                        day_available = True
                        night_available = True

                    # If the specific time slot is booked, set the corresponding availability to False
                    if time_slot == 'day' and not day_available:
                        continue
                    if time_slot == 'night' and not night_available:
                        continue

                    print(room_data)
                    if info:
                        filtered_room_data = {
                            "info": info,
                            "room_id": room_id,
                            "max_adults": room_data.get('max_adults'),
                            "max_children": room_data.get('max_children'),
                            "description": room_data.get('description'),
                            "price": room_data.get('price'),
                            "type": room_data.get('type'),
                            "day_available": day_available,
                            "night_available": night_available,
                            "bookings": bookings.get(checkin, {})
                        }
                        print(info)
                        filtered_data.append(filtered_room_data)
                    else:
                        filtered_room_data = {
                            "info": info,
                            "room_id": room_id,
                            "max_adults": room_data.get('max_adults'),
                            "max_children": room_data.get('max_children'),
                            "description": room_data.get('description'),
                            "price": room_data.get('price'),
                            "type": room_data.get('type'),
                            "day_available": day_available,
                            "night_available": night_available,
                            "bookings": bookings.get(checkin, {})
                        }
                        print(info)
                        filtered_data.append(filtered_room_data)

            room_count = len(filtered_data)  # Count of available rooms

            print(f"Available rooms of type '{room_type}' with '{time_slot}' time slot on {checkin}: {filtered_data}")
            print(f"Total available rooms: {room_count}")

        except Exception as e:
            rooms = {}
            room_count = 0
            print(f"Error fetching data from Firebase: {e}")

        return render(request, 'core/check-availability.html', 
            {'rooms': rooms,
            'room_count': room_count,
            'filtered_data': filtered_data,
            'check_in': checkin,
            'time_slot': time_slot,
            'adults': adult_count,
            'child': children_count,
            'room_type': room_type,
            'info': info, 
            'authenticated': authenticated})


    return render(request, 'core/check-availability.html', 
        {'check_in': check_in,
        'adults': adults,
        'child': child,
        'time_slot': time_slot,
        'info': info, 
        'authenticated': authenticated})

def book_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal-code')
        purpose = request.POST.get('purpose')
        remarks = request.POST.get('remarks')

        check_in = request.POST.get('check_in')
        adults = request.POST.get('adults')
        child = request.POST.get('children')

        shuttle_pickup = request.POST.get('shuttle-pickup')

        if(not shuttle_pickup):
            shuttle_pickup = "No"

        file = request.FILES.get('gcash')  # 'gcash' is the name of the file input field
        file_url = None
        if file:
            # Generate a unique file name
            file_name = f'{last_name}, {first_name}/{check_in}/{file.name}'
            # Upload the file to Firebase Storage
            storage.child(file_name).put(file)
            # Get the URL of the uploaded file
            file_url = storage.child(file_name).get_url(None)
            print(f"File uploaded to Firebase Storage with URL: {file_url}")
        else:
            print("No file uploaded")

        # Save booking data to Firebase Realtime Database
        booking_data = {
            'room_id': room_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'address': address,
            'city': city,
            'postal_code': postal_code,
            'purpose': purpose,
            'remarks': remarks,
            'check_in': check_in,
            'adults': adults,
            'child': child,
            'shuttle_pickup': shuttle_pickup,
            'file_url': file_url  # Save the URL of the uploaded file
        }

        # Push booking data to Firebase Realtime Database
        #db.child('bookings').push(booking_data)
        print(f"Booking data pushed to Firebase Realtime Database: {booking_data}")
        print("SUCCESS")
        # Redirect or return a response
        return HttpResponse("Room booked successfully")

    return redirect('availability_results')

def confirm_booking(request):


    return redirect('')

def fetch_room_data(request):
    room_id = request.GET.get('room_id')
    room_data = get_room_by_id(room_id)

    print(room_data)
    if room_data:
        return JsonResponse({'success': True, 'room_data': room_data})
    else:
        return JsonResponse({'success': False, 'message': 'Room not found'}, status=404)

def all_rooms(request):
    rooms = db.child('rooms').get().val
    
    context = {
        'rooms': rooms
    }

    print(context)
    return render(request, 'core/all-rooms.html', context)

def create_room(request):
    if request.method == 'POST':
        room_id = "room" + request.POST.get('id')
        max_adults = request.POST.get('max-adults')
        max_children = request.POST.get('max-children')
        room_type = request.POST.get('type')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        formatted_price = "{:.2f}".format(float(price))
        
        data = {
            "max_adults": int(max_adults),
            "max_children": int(max_children),
            "type": room_type,
            "description": description,
            "price": float(formatted_price),
            "bookings": {}
        }

        db.child('rooms').child(room_id).set(data)

        print(data)

        return HttpResponse("Room created successfully")

    return render(request, 'core/create-room.html')

def contactus(request):
    idToken = request.session.get('uid')
    authenticated = False

    info = None

    try:
        idToken = request.session.get('uid')
        if idToken:
            info = get_user_info(idToken)
            if info:
                authenticated = True
    except Exception as e:
        error = str(e)
        if 'INVALID_ID_TOKEN' in error:
            return redirect('KaTreasureApp:logout')
            # messages.success(request, 'Your Token has expired. Please login again')
            print('Your Token has expired. Please login again')
            
    if request.method == "POST":
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        data = {"full_name": full_name, "email": email, "message": message}

        db.child('contact-us').child(subject).child("details").set(data)

        messages.success(request, f"Thank you {full_name}, we will contact you as soon.")

    return render(request, 'core/contactus.html', {'info': info, 'authenticated': authenticated})

def logout(request):
    django_auth.logout(request)
    messages.success(request, "Logged out.")
    return redirect('KaTreasureApp:login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        link = auth.generate_password_reset_link(email, action_code_settings=None)
        sender = 'katreasureeh@gmail.com'
        subject = "KaTreasure: Password Reset"

        message = f'You requested to reset your password for your KaTreasure account. Use the link below to change it. \n\nReset Link: {link}'

        recipient_list = [email]

        send_mail(subject, message, sender, recipient_list)
        messages.success(request, f'Reset link has been sent to {email}')
        return redirect('KaTreasureApp:login')
    return render(request, 'auth/forgot_password.html')

def login(request):
    uid = request.session.get('uid')
    if uid:
        messages.success(request, "You are already signined.")
        return redirect('KaTreasureApp:home')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            try:
                user = authn.sign_in_with_email_and_password(email, password)
                session_id = user['idToken']
                request.session['uid'] = str(session_id)

                uid = str(user['localId'])
                user_data = db.child("users").child(uid).child('details').child('full_name').get().val()
                print("Userdata:", user_data)
                messages.success(request, "Account Login Successfully")
                authenticated = True
                print("Login Success")
                return render(request, 'core/home.html', {'authenticated': authenticated, 'full_name': user_data})
            except Exception as e:
                error_message = str(e)
                if 'INVALID_EMAIL' in error_message:
                    messages.error(request, "Invalid email, please try again.")
                    return render(request, 'auth/login.html')
                elif 'INVALID_LOGIN_CREDENTIALS' in error_message:
                    messages.error(request, "Invalid credentials, please try again.")
                    return render(request, 'auth/login.html')
                elif 'INVALID_ID_TOKEN' in error_message:
                    messages.error(request, "Invalid token, please try again.")
                    return render(request, 'auth/login.html')
                else:
                    messages.error(request, "Invalid input, please try again.")
                    print("ERROR:", error_message)
                    return render(request, 'auth/login.html')
        return render(request, 'auth/login.html')

def signup(request):
    uid = request.session.get('uid')
    if uid:
        messages.success(request, "You are already signined.")
        return redirect('KaTreasureApp:home')
    else:
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')

            try:
                user = authn.create_user_with_email_and_password(email, password)

                link = auth.generate_email_verification_link(email)
                sender = 'katreasureeh@gmail.com'
                subject = "KaTreasure: Verification Link"
                message = f'We requested to verify your email for your KaTreasure account. Use the link below to verify it. \n\nReset Link: {link}'

                recipient_list = [email]

                data = {"first_name": first_name, "last_name": last_name, "email": email, "status":"unverified", "role": "user"}

                uid = user['localId']

                db.child('users').child(uid).child("details").set(data)

                send_mail(subject, message, sender, recipient_list)
                messages.success(request, f'Account Created Successfully - Verification link has been sent to {email}')

                print("Signup Success")
                return redirect('KaTreasureApp:login')
            except Exception as e:
                error_message = str(e)
                if 'EMAIL_EXISTS' in error_message:
                    messages.error(request, "Email already exists. Please login or use a different email address.")
                    return render(request, 'auth/signup.html')
                elif 'WEAK_PASSWORD' in error_message:
                    messages.error(request, "Weak password.")
                    return render(request, 'auth/signup.html')
                else:
                    print(error_message)
                    error_message = "Invalid Email Format."
                    messages.error(request, error_message)
                    return render(request, 'auth/signup.html')
        return render(request, 'auth/signup.html')