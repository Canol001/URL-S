import pyrebase
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("url-s-7d09d-firebase-adminsdk-fbsvc-e180e6d9f8.json")  # Make sure this file is correct
firebase_admin.initialize_app(cred)

load_dotenv()

firebase_config = {
    "apiKey": "AIzaSyDDjRobxbHqeqADo8nY-A_vSNVStKySxME",
    "authDomain": "url-s-7d09d.firebaseapp.com",
    "databaseURL": "https://url-s-7d09d-default-rtdb.firebaseio.com",
    "projectId": "url-s-7d09d",
    "storageBucket": "url-s-7d09d.appspot.com",
    "messagingSenderId": "843610118470",
    "appId": "1:843610118470:web:fa5eb065100c7748baed47",
    "measurementId": "G-0JYPZK7ZM5"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

