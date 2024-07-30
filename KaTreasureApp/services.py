import pyrebase
from .firebase_config import config

firebase = pyrebase.initialize_app(config)
db = firebase.database()
authn = firebase.auth()

def get_room_by_id(room_id):
    room = db.child("rooms").child(room_id).get()
    if room.val():
        return room.val()
    else:
        return None
    
def get_user_info(id_token):
    if id_token:
        a = authn.get_account_info(id_token)
        a = a['users']
        a = a[0]
        a = a['localId']

        first_name = db.child("users").child(a).child('details').child('first_name').get().val()
        last_name = db.child("users").child(a).child('details').child('last_name').get().val()
        phone_number = db.child("users").child(a).child('details').child('phone_number').get().val()
        email = db.child("users").child(a).child('details').child('email').get().val()
        return {"first_name": first_name, "last_name": last_name, "phone_number": phone_number, "email":  email}
    else:
        return None