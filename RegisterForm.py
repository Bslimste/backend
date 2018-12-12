from flask import jsonify
from passlib.handlers.pbkdf2 import pbkdf2_sha256

import checks
from Database import Persister, Person


# Function that validates all the gotten data and registers a new user
def registerSubmit(form, clearance):
    firstName = form.get('firstName', None)
    lastName = form.get('lastName', None)
    email = form.get('email', None)
    password = form.get('password', None)
    wordpresskey = form.get('wordpresskey', None)

    firstName = firstName.strip()
    lastName = lastName.strip()
    firstName = firstName.lower()
    lastName = lastName.lower()
    email = email.lower()
    password = password.lower()

    if checks.checkSpecialChars([firstName, lastName]):
        msg = "Gebruik alstublieft geen speciale karakters in uw naam!"
        return {"code": 400, "message": msg}

    if checks.checkSpecialCharsEmail(email):
        msg = "Gebruik alstublieft geen speciale karakters in uw email!"
        return {"code": 400, "message": msg}

    if checks.emptyCheck([firstName, lastName, email, password]):
        msg = "Vul alstublieft alle velden in."
        return {"code": 400, "message": msg}

    if checks.lengthSixtyFourCheck([firstName, lastName, email]):
        msg = "Vul alsublieft niet meer dan 64 karakters in."
        return {"code": 400, "message": msg}

    password = form.get('password', None)
    check = checks.passwordLengthCheck(password)

    if check == [False, "short"]:
        msg = "Uw wachtwoord moet langer dan 5 karakters zijn."
        return {"code": 400, "message": msg}

    if check == [False, "long"]:
        msg = "Uw wachtwoord moet korter zijn dan 64 karakters."
        return {"code": 400, "message": msg}

    if Persister.checkEmailExistance(email):
        msg = "Dit emailadres bestaat al."
        return {"code": 400, "message": msg}

    if(clearance == 0):
        person = Person(
            firstname=firstName,
            lastname=lastName,
            email=email,
            password=password,
            points=0,
            clearance=0,
            license=True,
            authenticated=False
        )
        return Persister.persist_object(person)
    elif(clearance == 1):
        person = Person(
            firstname=firstName,
            lastname=lastName,
            email=email,
            password=password,
            points=0,
            clearance=1,
            wordpressKey=wordpresskey,
            license=True,
            authenticated=False,
            biography=form.get('biography'),
            profilePhoto=form.get('img')
        )
        return Persister.persist_object(person)
    else:
        return None

def registerFacebookUser(form):
    person = Person(
        firstname=form.get('firstName'),
        lastname=form.get('lastName'),
        email=form.get('email'),
        password='',
        points=0,
        clearance=0,
        license=True,
        authenticated=False
    )
    return Persister.persist_object(person)

