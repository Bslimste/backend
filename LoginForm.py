import sys, UserApi
from flask_login import login_user, current_user
from passlib.hash import pbkdf2_sha256
from Database import Persister, Person


def loginUser(form):
    emailLogin = form.get('email')
    passwordLogin = form.get('password')
    print(UserApi.getEmail(emailLogin))
    dbEmail = UserApi.getEmail(emailLogin)

    if dbEmail is None:
        return {"boolean": "false", "userId": None, "clearance": None, "msg": "Email klopt niet"}

    dbPassword = UserApi.getPassword(emailLogin)

    if dbPassword == passwordLogin:
        user = UserApi.getUserByEmail(emailLogin)
        Persister.loginUser(user)
        return {"boolean": "true", "userId": user.id, "clearance": user.clearance, "msg": "OK"}

    else:
        print(" email2")
        print(" pass2")
        return {"boolean": "false", "userId": None, "clearance": None, "msg": "Wachtwoord klopt niet"}

    # if dbEmail is None:
    #     msg = "Email klopt niet"
    #     return {"bool": False, "message": msg}
    #
    # if dbPassword is None:
    #     msg = "Wachtwoord klopt niet"
    #     return {"bool": False, "message": msg}
    #
    # elif dbPassword == passwordLogin:
    #     user = UserApi.getUserByEmail(emailLogin)
    #     Persister.loginUser(user)
    #     return {"bool"}user


def logoutUser(form):
    user = Persister.getPerson(form.get('id'))
    return Persister.logoutUser(user)


def checkLogin(form):
    user = Persister.getPerson(form.get('id'))
    return user.authenticated
