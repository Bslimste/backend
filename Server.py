import requests
from flask_login import LoginManager, current_user, login_required, logout_user
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file, make_response, session
import os
import UserApi, LoginForm, eventApi
import sys
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

from bs4 import BeautifulSoup as BSHTML

import UserApi, LoginForm, eventApi, RegisterForm
import sys, string, os, random

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)


# function for flask_login
@login_manager.user_loader
def load_user(person_id):
    return UserApi.getPerson(person_id)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
    return render_template('index.html')


@app.route('/api/deleteEventTrigger', methods=['GET'])
def deleteEventTrigger():
    id = request.args.get("id")
    return jsonify({"responseCode": eventApi.deleteEvent(id)})


# sends the event to the wordpress website and sends a notification to the app

@app.route('/api/createEventTrigger', methods=['GET'])
def createEventTrigger():
    data = requests.get("http://gromdroid.nl/bslim/wp-json/wp/v2/events/" + request.args.get("id")).json()
    print(data)
    address = requests.get(
        "http://gromdroid.nl/bslim/wp-json/wp/v2/event-venues/" + str(data['event-venues'][0])).json()
    soup = BSHTML(data["content"]["rendered"])
    images = soup.findAll('img')
    img = " "
    for image in images:
        img = image['src']
    apiKey = "YTFkZGY1OGUtNGM5NC00ODdmLWJmN2QtNjMxYzNjMzk0MWJl"
    appId = "893db161-0c60-438b-af84-8520b89c6d93"
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic " + apiKey}

    payload = {"app_id": appId,
               "included_segments": ["All"],
               "contents": {"en": "Nieuw evenement van Bslim!"},
               "headings": {"en": data['title']['rendered']}}
    print("YAY")
    # req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    print(data["author"])
    return jsonify({"responseCode": eventApi.createEvent(request.args.get("id"),
                                                         data["title"]["rendered"],
                                                         data["start"],
                                                         data["end"],
                                                         address['name'],
                                                         data["content"]["rendered"],
                                                         data["author"],
                                                         img)})


@app.route('/api/updateEventTrigger', methods=['GET'])
def updateEventTrigger():
    data = requests.get("http://gromdroid.nl/bslim/wp-json/wp/v2/events/" + request.args.get("id")).json()
    print(data)
    address = requests.get(
        "http://gromdroid.nl/bslim/wp-json/wp/v2/event-venues/" + str(data['event-venues'][0])).json()
    soup = BSHTML(data["content"]["rendered"])
    images = soup.findAll('img')
    img = " "
    for image in images:
        img = image['src']
    apiKey = "YTFkZGY1OGUtNGM5NC00ODdmLWJmN2QtNjMxYzNjMzk0MWJl"
    appId = "893db161-0c60-438b-af84-8520b89c6d93"
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic " + apiKey}

    payload = {"app_id": appId,
               "included_segments": ["All"],
               "contents": {"en": "Nieuw evenement van Bslim!"},
               "headings": {"en": data["title"]["rendered"]}}
    # req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    return jsonify({"responseCode": eventApi.updateEvent(request.args.get("id"),
                                                         data["title"]["rendered"],
                                                         data["start"],
                                                         data["end"],
                                                         address['name'],
                                                         data["content"]["rendered"],
                                                         data["author"],
                                                         img)})


################################################################
# login/logout
################################################################

# check if user is loggedin if not try to log user in.
# return 0/1 for counselor, true is for showing login or logout in menu.
@app.route('/login', methods=['POST'])
def loginPageHandler():
    if current_user.is_authenticated:
        return jsonify(
            {"responseCode": 400, 'value': False, 'clearance': None, 'userId': None, "msg": "U bent al ingelogd"})
    else:
        response = LoginForm.loginUser(request.get_json())
        return jsonify(response)


# check if user is loggedin using current_user from flask.
@app.route('/api/loginCheck', methods=['POST'])
def loginCheck():
    return jsonify("auth": {LoginForm.loginCheck(request.get_json())})


@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    return jsonify(LoginForm.logoutUser(data))


# generates a security code and sends it via email to the user
@app.route('/changeEmailRequest', methods=['POST'])
def changeMail():
    data = request.get_json()
    oldEmail = data.get('oldEmail')
    if UserApi.getEmail(oldEmail) == None:
        return jsonify({'responseCode': 400, 'msg': "Email is not recognized"})
    user = UserApi.getUserByEmail(oldEmail)
    if UserApi.changeEmail(user.id) == 200:
        msg = MIMEMultipart()

        user = UserApi.getUserByEmail(oldEmail)
        message = "Om je e-mail adres te veranderen is er een veiligheids code gegenereerd: " + user.securityCode + ". Vul deze code in de app in en voer u nieuwe e-mail adres in."

        # setup the parameters of the message
        msg['From'] = "bslim@grombouts.nl"
        msg['To'] = oldEmail
        msg['Subject'] = "E-mail veranderen"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # Send the message via our own SMTP server.
        server = smtplib.SMTP('mail.grombouts.nl', 587)
        server.starttls()
        server.login('bslim@grombouts.nl', "bslim")
        server.sendmail('bslim@grombouts.nl', oldEmail, msg.as_string())
        server.quit()
        return jsonify({'responseCode': 200, 'msg': 'Security code generated for ' + oldEmail, 'oldEmail': oldEmail})
    return jsonify({'responseCode': 500, 'msg': 'Could not generate security code'})


# changes the email of the user if the security code is correct
@app.route('/changeUserEmail', methods=['POST'])
def changeUserEmail():
    data = request.get_json()
    oldEmail = data.get('oldEmail')
    newEmail = data.get('newEmail')
    secCode = data.get('secCode')
    if not UserApi.checkSecCode(oldEmail, secCode):
        return jsonify({'responseCode': 400, 'msg': "Veiligheidscode is ongeldig."})
    if UserApi.changeUserEmail(oldEmail, newEmail) == 200:
        msg = MIMEMultipart()

        user = UserApi.getUserByEmail(newEmail)
        message = "Uw e-mail adres is succesvol verandert."

        # setup the parameters of the message
        msg['From'] = "bslim@grombouts.nl"
        msg['To'] = newEmail
        msg['Subject'] = "E-mail adres verandert"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # Send the message via our own SMTP server.
        server = smtplib.SMTP('mail.grombouts.nl', 587)
        server.starttls()
        server.login('bslim@grombouts.nl', "bslim")
        server.sendmail('bslim@grombouts.nl', newEmail, msg.as_string())
        server.quit()
        return jsonify({'responseCode': 200, 'msg': 'Succesfuly changed e-mail address to ' + newEmail})
    return jsonify({'responseCode': 500, 'msg': 'Could not change e-mail address'})


# generates a new password and sends it to the user via email

@app.route('/reset-password', methods=['POST'])
def resetPassword():
    if (request.method == "POST"):
        data = json.loads(request.data)
        email = data['email']
        if (UserApi.getEmail(email) == None):
            return jsonify({"boolean": False, "responseCode": 400})
        newPass = getNewPassword(email)

        # create message object instance
        msg = MIMEMultipart()

        message = "Je wachtwoord is gereset. Je nieuwe wachtwoord is " + newPass + ". Verander u wachtwoord zo snel mogelijk aub."

        # setup the parameters of the message
        msg['From'] = "bslim@grombouts.nl"
        msg['To'] = email
        msg['Subject'] = "Wachtwoord reset"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # Send the message via our own SMTP server.
        server = smtplib.SMTP('mail.grombouts.nl', 587)
        server.starttls()
        server.login('bslim@grombouts.nl', "bslim")
        server.sendmail('bslim@grombouts.nl', email, msg.as_string())
        server.quit()
    return jsonify({"boolean": True, "responseCode": 200})


# generates a new password
def getNewPassword(email, size=6, chars=string.ascii_uppercase + string.digits):
    email = email
    temp = ''.join(random.choice(chars) for _ in range(size))
    UserApi.saveNewPassword(temp, email)
    return temp


# changes the password of a user
@app.route('/api/changePassword', methods=['POST'])
def changePassword():
    data = request.get_json()
    id = data.get('id')
    oldPassword = data.get('oldPassword')
    newPassword = data.get('newPassword')
    return jsonify({"responseCode": UserApi.changePassword(id, oldPassword, newPassword)})


################################################################
# points and stampcard
################################################################

# returns the amount of stamps a user has
@app.route('/api/checkPoints', methods=['POST'])
def checkPoints():
    data = request.get_json()
    return jsonify({"points": UserApi.checkPoints(data.get('id')), "responseCode": 200})


# adds 1 stamp to a user
@app.route('/api/addPoint', methods=['POST'])
def addPoint():
    data = request.get_json()
    return jsonify({"responseCode": UserApi.addPoints(data.get('id'))})


# removes 1 stamp from a user
@app.route('/api/substractPoint', methods=['POST'])
def substractPoint():
    data = request.get_json()
    return jsonify({"responseCode": UserApi.substractPoint(data.get('id'))})


# resets the stampcard of a user
@app.route('/api/resetStampCard', methods=['POST'])
def resetStampCard():
    data = request.get_json()
    return jsonify({"responseCode": UserApi.resetStampCard(data.get('id'))})


@app.route('/api/getParticipants', methods=['POST'])
def getParticipants():
    data = request.get_json()
    result = eventApi.getParticipantInfo(data.get('eventId'))
    if len(result) > 0:
        return jsonify({"responseCode": 200, "participants": result})
    return jsonify({"responseCode": 400, "participants": {}})


################################################################
# events
################################################################

# starts the creating of an event on the app side
@app.route('/api/createEvent', methods=['POST'])
def createEvent():
    data = request.get_json()
    return jsonify({"responseCode": eventApi.createEvent(data.get('name'),
                                                         data.get('begin'),
                                                         data.get('end'),
                                                         data.get('location'),
                                                         data.get('description'),
                                                         data.get('leader'),
                                                         data.get('img'))})


# adds a participent entry to the db with a specific event and user
@app.route('/api/subToEvent', methods=['POST'])
def subToEvent():
    data = request.get_json()
    return jsonify(eventApi.subToEvent(data.get("eventId"), data.get("personId")))


# removes a participent entry from the db with a specific event and user

@app.route('/api/unSubToEvent', methods=['POST'])
def unSubToEvent():
    data = request.get_json()
    return jsonify(eventApi.unSubToEvent(data.get("eventId"), data.get("personId")))


# checks whether a participent entry with a specific event and person exists
@app.route('/api/checkSub', methods=['POST'])
def checkSub():
    data = request.get_json()
    return jsonify(eventApi.checkSubs(data.get("personId")))


@app.route('/api/saveMedia', methods=['POST'])
def saveMedia():
    data = request.get_json()
    return eventApi.saveMedia(data.get("url"), data.get("eventName"))


# searches through all the events in the db on title/leader and begin-/end- date
@app.route('/api/searchEvent', methods=['POST'])
def searchEvent():
    data = request.get_json()
    print(data)
    result = eventApi.searchEvent(data.get("searchString"))
    if len(result) > 0:
        return jsonify({"responseCode": 200, "events": result})
    return jsonify({"responseCode": 400, "events": {}})


################################################################
# news
################################################################

# starts the proces of creating a news item on the app side and sends a notification to the app
@app.route('/api/createNewsItem', methods=['GET'])
def createNewsItem():
    data = requests.get("http://gromdroid.nl/bslim/wp-json/wp/v2/posts/" + request.args.get("id")).json()
    soup = BSHTML(data["content"]["rendered"])
    images = soup.findAll('video')
    img = " "
    for image in images:
        img = image['src']

    apiKey = "YTFkZGY1OGUtNGM5NC00ODdmLWJmN2QtNjMxYzNjMzk0MWJl"
    appId = "893db161-0c60-438b-af84-8520b89c6d93"
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic " + apiKey}

    payload = {"app_id": appId,
               "included_segments": ["All"],
               "contents": {"en": "Nieuws van bslim"},
               "headings": {"en": data.get('title')}}

    # req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    return jsonify({"responseCode": UserApi.createNewsItem(data["title"]["rendered"],
                                                           data["content"]["rendered"],
                                                           img)})


@app.route('/api/createNewsItemApp', methods=['POST'])
def createNewsItemApp():
    data = request.get_json()
    apiKey = "YTFkZGY1OGUtNGM5NC00ODdmLWJmN2QtNjMxYzNjMzk0MWJl"
    appId = "893db161-0c60-438b-af84-8520b89c6d93"
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic " + apiKey}

    payload = {"app_id": appId,
               "included_segments": ["All"],
               "contents": {"en": "Nieuws van bslim"},
               "headings": {"en": data.get('title')}}

    # req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    return jsonify({"responseCode": UserApi.createNewsItem(data["title"],
                                                           data["content"],
                                                           data["img"])})


# searches through all the news items in the db on title and created date
@app.route('/api/searchNews', methods=['POST'])
def searchNews():
    data = request.get_json()
    result = eventApi.searchNews(data.get("searchString"))
    if len(result) > 0:
        return jsonify({"responseCode": 200, "news": result})
    return jsonify({"responseCode": 400, "news": {}})


################################################################
# mentor
################################################################

# adds a profilephoto to a leader account
@app.route('/api/addProfilePhoto', methods=['POST'])
def addProfilePhoto():
    data = request.get_json()
    return jsonify({"responseCode": UserApi.addProfilePhoto(data.get('url'), data.get('id'))})


# returns the profilephoto from a leader account
@app.route('/api/getProfilePhoto', methods=['POST'])
def getProfilePhoto():
    data = request.get_json()
    return jsonify({"profilePhoto": UserApi.getProfilePhoto(data.get('id'))})


################################################################
# miscellaneous
################################################################

# Is called to add points to the user account when an event is scannend
@app.route('/api/qrEvent', methods=['POST'])
def eventScanned():
    data = request.get_json()
    eventId = data.get('eventId')
    personId = data.get('personId')
    if eventApi.isScanned(eventId, personId) == 400:
        return jsonify({"responseCode": "400"})
    else:
        responseCode = eventApi.eventScanned(eventId, personId)
        return jsonify({"responseCode": responseCode})


# Is called to get the id from an event when giving a qrCode, returns 200 when succesfull and 400 when not
@app.route('/api/eventByCode', methods=['POST'])
def findEvent():
    data = request.get_json()
    qrCode = data.get("qrCode")
    result = eventApi.findEvent(qrCode)
    if result:
        return jsonify({"responseCode": "200", "eventId": result.id})
    return jsonify({"responseCode": "400", "eventId": None})


# Is called to register a new user
@app.route('/register', methods=['POST'])
def registerNormalUser():
    return jsonify({"responseCode": RegisterForm.registerSubmit(request.get_json(), 0)})


@app.route('/facebookLogin', methods=['POST'])
def facebookLogin():
    return jsonify(LoginForm.facebookLogin(request.get_json()))


# Is called to register a new admin
@app.route('/register-admin', methods=['POST'])
def registerAdmin():
    return jsonify({"responseCode": RegisterForm.registerSubmit(request.get_json(), 1)})


# returns all the events from the db
@app.route('/api/getAllEvents', methods=['POST'])
def getEvents():
    result = eventApi.getAllEvents()
    if len(result) > 0:
        return jsonify({"responseCode": 200, "events": result})
    return jsonify({"responseCode": 400, "events": {}})


# returns all the admins/leaders in the db
@app.route('/api/getAllAdmins', methods=['POST'])
def getAdmins():
    result = UserApi.getAllAdmins()
    if len(result) > 0:
        return jsonify({"responseCode": 200, "admins": result})
    return jsonify({"responseCode": 400, "admins": {}})


# returns all the news items from the db
@app.route('/api/getAllNewsItems', methods=['GET'])
def getNews():
    result = eventApi.getAllNewsItems()
    if len(result) > 0:
        return jsonify({"responseCode": 200, "news": result})
    return jsonify({"responseCode": 400, "news": {}})


@app.route('/api/getAllSubs', methods=['POST'])
def getAllSubs():
    data = request.get_json()
    id = data.get("id")
    result = eventApi.getAllSubs(id)
    if len(result) > 0:
        return jsonify({"responseCode": 200, "subs": result})
    return jsonify({"responseCode": 400, "subs": {}})


@app.route('/api/getUsers', methods=['POST'])
def getUsers():
    result = UserApi.getUsers()
    print(result)
    if len(result) > 0:
        return jsonify({"responseCode": 200, "users": result})
    return jsonify({"responseCode": 400, "users": {}})


@app.route('/api/sendFeedbackForm', methods=['POST'])
def sendFeedbackForm():
    data = request.get_json()
    email = data.get('email')
    subject = data.get('subject')
    problem = data.get('problem')

    if UserApi.checkEmailExistance(email):
        msg = MIMEMultipart()

        message = "onderwerp:" + subject + + "\n" + "probleem:" + problem

        # setup the parameters of the message
        msg['From'] = "bslim@grombouts.nl"
        msg['To'] = "bslim@grombouts.nl"
        msg['Subject'] = "Feedback van gebruiker"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # Send the message via our own SMTP server.
        server = smtplib.SMTP('mail.grombouts.nl', 587)
        server.starttls()
        server.login('bslim@grombouts.nl', "bslim")
        server.sendmail('bslim@grombouts.nl', 'bslim@grombouts.nl', msg.as_string())
        server.quit()
        print("ok")
        return jsonify({'responseCode': 200, 'msg': 'Bedankt voor uw feedack.'})
    else:
        return jsonify({'responseCode': 400, 'msg': "Email is not recognized"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
