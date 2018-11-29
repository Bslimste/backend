import sys, UserApi, RegisterForm
from flask_login import login_user, current_user
from passlib.hash import pbkdf2_sha256
from Database import Persister, Person
import requests
import json

def loginUser(form):
    emailLogin = form.get('email')
    passwordLogin = form.get('password')
    dbEmail = UserApi.getEmail(emailLogin)

    if dbEmail is None:
        return {"responseCode": 400, "boolean": "false", "userId": None, "clearance": None, "msg": "Email klopt niet"}

    dbPassword = UserApi.getPassword(emailLogin)

    if dbPassword == passwordLogin:
        user = UserApi.getUserByEmail(emailLogin)
        Persister.loginUser(user)
        if(user.clearance == 1):
            return {"responseCode": 200, "boolean": "true", "userId": user.id, "wordpresskey": user.wordpressKey, "clearance": user.clearance, "msg": "OK"}
        else:
            return {"responseCode": 200, "boolean": "true", "userId": user.id, "clearance": user.clearance, "msg": "OK"}
    else:
        return {"responseCode": 400, "boolean": "false", "userId": None, "clearance": None, "msg": "Wachtwoord klopt niet"}

def logoutUser(form):
    user = Persister.getPerson(form.get('id'))
    if Persister.logoutUser(user):
        return {"responseCode": 200, "boolean": True}
    return {"responseCode": 500, "boolean": False}


def loginCheck(form):
    user = Persister.getPerson(form.get('id'))
    return user.authenticated

def facebookLogin(form):
    emailLogin = form.get('email')
    dbEmail = UserApi.getEmail(emailLogin)

    if dbEmail is None:
        RegisterForm.registerFacebookUser(form)

    user = UserApi.getUserByEmail(emailLogin)
    if(Persister.loginUser(user)):
        if(user.clearance == 1):
            return {"responseCode": 200, "boolean": "true", "userId": user.id, "wordpresskey": user.wordpressKey, "clearance": user.clearance, "msg": "Ingelogd met facebook"}
        else:
            return {"responseCode": 200, "boolean": "true", "userId": user.id, "wordpresskey": None,"clearance": user.clearance, "msg": "Ingelogd met facebook"}
    else:
        return {"responseCode": 400, "boolean": "false", "userId": None, "clearance": None, "msg": "Kon niet inloggen met facebook"}

