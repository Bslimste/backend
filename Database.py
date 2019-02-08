import sqlalchemy as sqla
from flask import jsonify
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import extract
from flask_login import UserMixin
import checks
import re
import random, string
import hashlib
import datetime

conn = sqla.create_engine('mysql+pymysql://ina:ina-app!@localhost/bslim?charset=utf8')

Session = scoped_session(sessionmaker(bind=conn))

Base = declarative_base()


class Person(Base, UserMixin):
    __tablename__ = 'person'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True, unique=True)
    firstname = sqla.Column('firstname', sqla.VARCHAR(64))
    lastname = sqla.Column('lastname', sqla.VARCHAR(64))
    email = sqla.Column('email', sqla.VARCHAR(64), unique=True)
    password = sqla.Column('password', sqla.VARCHAR(64))
    points = sqla.Column('points', sqla.Integer)
    clearance = sqla.Column('clearance', sqla.Integer)
    license = sqla.Column('license', sqla.Boolean)
    authenticated = sqla.Column('authenticated', sqla.Boolean)
    biography = sqla.Column('biography', sqla.VARCHAR(1000))
    profilePhoto = sqla.Column('profilePhoto', sqla.VARCHAR(400))
    wordpressKey = sqla.Column('wordpressKey', sqla.Integer, unique=True)
    securityCode = sqla.Column('securityCode', sqla.VARCHAR(5))


class Event(Base):
    __tablename__ = 'event'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True, unique=True)
    name = sqla.Column('name', sqla.VARCHAR(64))
    begin = sqla.Column('begin', sqla.DATETIME)
    end = sqla.Column('end', sqla.DATETIME)
    location = sqla.Column('location', sqla.VARCHAR(64))
    desc = sqla.Column('desc', sqla.VARCHAR(2000))
    leader = sqla.Column('leader', sqla.Integer, sqla.ForeignKey('person.wordpressKey'))
    cancel = sqla.Column('cancel', sqla.Integer)
    img = sqla.Column('img', sqla.VARCHAR(400))
    qr_code = sqla.Column('qr_code', sqla.VARCHAR(200))
    created = sqla.Column('created', sqla.DATETIME)
    link = sqla.Column('link', sqla.VARCHAR(400))


class Content(Base):
    __tablename__ = 'content'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True, unique=True)
    url = sqla.Column('url', sqla.VARCHAR(400))
    title = sqla.Column('title', sqla.VARCHAR(64))
    desc = sqla.Column('desc', sqla.VARCHAR(300))
    link = sqla.Column('link', sqla.VARCHAR(500))
    created = sqla.Column('created', sqla.DATETIME)


class Particepant(Base):
    __tablename__ = 'particepant'
    person_id = sqla.Column('person_id', sqla.Integer, sqla.ForeignKey('person.id'), primary_key=True)
    event_id = sqla.Column('event_id', sqla.Integer, sqla.ForeignKey('event.id'), primary_key=True)
    event_scanned = sqla.Column('event_scanned', sqla.Boolean)


class Media(Base):
    __tablename__ = 'media'
    event_id = sqla.Column('event_id', sqla.Integer, sqla.ForeignKey('event.id'), primary_key=True)
    url = sqla.Column('url', sqla.VARCHAR(400))


class Persister():
    def getPerson(id):
        db = Session()
        try:
            user = db.query(Person).filter(Person.id == id).first()
            db.close()
            return user
        except:
            db.rollback()
            db.close()

    def getEmail(email):
        db = Session()
        user = db.query(Person).filter(Person.email == email).first()
        db.close()

        if user is not None:
            return user.email
        else:
            return None

    def loginUser(user):
        db = Session()
        try:
            person = db.query(Person).filter(Person.id == user.id).first()
            person.authenticated = True
            db.commit()
            db.close()
        except:
            db.close()
            return False
        return True

    def logoutUser(user):
        db = Session()
        person = db.query(Person).filter(Person.id == user.id).first()
        person.authenticated = False
        db.commit()
        db.close()
        return True

    def getPassword(email):
        db = Session()
        user = db.query(Person).filter(Person.email == email).first()
        db.close()
        if user is not None:
            return user.password
        else:
            return None

    def getUserWithEmail(email):
        db = Session()
        user = db.query(Person).filter(Person.email == email).first()
        db.close()
        return user

    def remove_event(id):
        db = Session()
        try:
            particepant = db.query(Particepant).filter(Particepant.event_id == id).first()
            print(particepant)
            if particepant != None:
                db.delete(particepant)
                db.commit()
            event = db.query(Event).filter(Event.id == id).first()
            db.delete(event)
            db.commit()
        except:
            db.close()
            return 400
        db.close()
        return 200

    def remove_news(id):
        db = Session()
        try:
            content = db.query(Content).filter(Content.id == id).first()
            db.delete(content)
            db.commit()
        except:
            db.close()
            return 400
        db.close()
        return 200

    def persist_object(obj):
        db = Session()
        try:
            db.add(obj)
            db.commit()
        except Exception as e:
            print(e)
            db.close()
            return 400
        db.close()
        return 200

    def update_object(id, name, begin, end, location, description, leader, img, qr_code):
        db = Session()
        try:
            event = db.query(Event).filter(Event.id == id).first()
            if (event == None):
                obj = Event(
                    id=id,
                    name=name,
                    begin=begin,
                    end=end,
                    location=location,
                    desc=description,
                    leader=leader,
                    cancel=0,
                    img=img,
                    qr_code=qr_code,
                    created=datetime.datetime.now(),
                    link=None
                )
                db.add(obj)
                db.commit()
            else:
                print(name)
                print(begin)
                print(end)
                print(description)
                print(leader)
                print(img)
                print(qr_code)
                event.name = name
                event.begin = begin
                event.end = end
                event.desc = description
                event.leader = leader
                event.cancel = 0
                event.img = img
                event.qr_code = qr_code
                event.link = ''
                db.commit()
        except:
            db.close()
            return 400
        db.close()
        return 200

    def remove_object(obj):
        db = Session()
        print("hallo");
        try:
            print("trying to delete");
            db.delete(obj)
            db.commit()
            print("deleted");
        except:
            db.close()
            return 400
        db.close()
        return 200

        # Check if QR code is already scanned

    # If the user has not subscribed himself to the event and both the user and the event exists the user is automaticly subscribed to the event.
    def isScanned(eventId, personId):
        db = Session()
        particepant = db.query(Particepant).filter(Particepant.person_id == personId) \
            .filter(Particepant.event_id == eventId) \
            .first()
        db.close()
        if particepant == None:
            if (db.query(Event).filter(Event.id == eventId).count()):
                if (db.query(Person).filter(Person.id == personId).count()):
                    db = Session()
                    newParticepant = Particepant(
                        person_id=personId,
                        event_id=eventId,
                        event_scanned=0
                    )
                    db.add(newParticepant)
                    db.commit()
                    db.close()
                    particepant = db.query(Particepant).filter(Particepant.person_id == personId) \
                        .filter(Particepant.event_id == eventId) \
                        .first()
                    return particepant.event_scanned
        elif particepant.event_scanned:
            return 400
        return 200

    # Checks whether or not a particepant entry or beloging events and persons already exists
    def checkParticepant(eventId, personId):
        db = Session()
        if (db.query(Event).filter(Event.id == eventId).count()):
            if (db.query(Person).filter(Person.id == personId).count()):
                if (db.query(Particepant).filter(Particepant.person_id == personId).filter(
                        Particepant.event_id == eventId).count()):
                    db.close()
                    return True
        db.close()
        return False

    def getSubsForPerson(personId):
        db = Session()
        if (db.query(Person).filter(Person.id == personId).count()):
            particepants = db.query(Particepant).filter(Particepant.person_id == personId).all()
            events = []
            for part in particepants:
                eventEntry = {}
                eventEntry['id'] = part.event_id
                events.append(eventEntry)
            db.close()
            return events
        db.close()
        return []

    def getParticepant(eventId, personId):
        db = Session()
        participant = db.query(Particepant).filter(Particepant.person_id == personId).filter(
            Particepant.event_id == eventId).first()
        db.close()
        return participant

    def getAllParticepants(eventId):
        db = Session()
        if db.query(Particepant).filter(Particepant.event_id == eventId).count():
            participants = db.query(Particepant).filter(Particepant.event_id == eventId).all()
            db.close()
            return participants
        else:
            return {}

    def getParticepant(eventId, personId):
        db = Session()
        participant = db.query(Particepant).filter(Particepant.person_id == personId).filter(
            Particepant.event_id == eventId).first()
        db.close()
        return participant

    # Marks the particepant entry as scannend and adds a point to the user account
    def updateParticepantInfo(event_id, person_id):
        db = Session()
        particepant = db.query(Particepant).filter(Particepant.person_id == person_id) \
            .filter(Particepant.event_id == event_id) \
            .first()

        person = db.query(Person).filter(Person.id == person_id).first()
        person.points = person.points + 1

        particepant.event_scanned = True
        db.commit()
        db.close()
        return "200"

    def checkEmailExistance(email):
        db = Session()
        if db.query(Person).filter(Person.email == email).count():
            db.close()
            return True
        db.close()
        return False

    # searches for an event with a specifyc qr_code value
    # returns False if one isn't found otherwise returns the event
    def findEvent(qrCode):
        db = Session()
        if db.query(Event).filter(Event.qr_code == qrCode).count():
            event = db.query(Event).filter(Event.qr_code == qrCode).first()
            db.close()
            return event
        db.close()
        return False

    def searchNews(searchString):
        db = Session()
        # define month numbers to translate user searchString if it contains months
        months = {
            "january": '1',
            "february": '2',
            "maart": '3',
            "april": '4',
            "mei": '5',
            "juni": '6',
            "juli": '7',
            "augustus": '8',
            "september": '9',
            "oktober": '10',
            "november": '11',
            "december": '12'
        }
        returnData = {}
        newsByName = {}
        newsByDate = {}

        # Convert the user query to a date query
        for month in months:
            if month in searchString.lower():
                # searchString is a date query
                monthNumber = months[month]
                if any(char.isdigit() for char in searchString):
                    numbers = re.findall(r'\d+', searchString)
                    dayNumber = numbers[0]
                    if int(dayNumber) < 10:
                        dayNumber = "0" + dayNumber
                    yearNumber = ''
                    if len(numbers) > 1:
                        yearNumber = numbers[1] + '-'
                    dateString = yearNumber + monthNumber + "-" + dayNumber
                    newsByDate = db.query(Content).filter(Content.created.contains(dateString)).all()
                else:
                    newsByDate = db.query(Content).filter(extract('month', Content.created) == monthNumber).all()

        # get all the news items whose title contain the search string
        newsName = db.query(Content).filter(Content.title.contains(searchString)).all()

        for news in newsByDate:
            if news.id not in returnData:
                newsEntry = {}
                newsEntry['id'] = news.id
                newsEntry['title'] = news.title
                newsEntry['url'] = news.url
                newsEntry['desc'] = news.desc
                newsEntry['created'] = news.created

                returnData[news.id] = newsEntry

        # loop through all the news items whose title contain the search string and add them to the returnData if it isn't already there
        for news in newsName:
            if news.id not in returnData:
                newsEntry = {}
                newsEntry['id'] = news.id
                newsEntry['title'] = news.title
                newsEntry['url'] = news.url
                newsEntry['desc'] = news.desc
                newsEntry['created'] = news.created

                returnData[news.id] = newsEntry

        db.close()
        return returnData

    def searchEvent(searchString):
        db = Session()
        # define month numbers to translate user searchString if it contains months
        months = {
            "january": '1',
            "february": '2',
            "maart": '3',
            "april": '4',
            "mei": '5',
            "juni": '6',
            "juli": '7',
            "augustus": '8',
            "september": '9',
            "oktober": '10',
            "november": '11',
            "december": '12'
        }

        # declare all dicts: to be filled by query results later
        returnData = {}
        leaders = {}
        eventsByLeader = {}
        eventsByBegin = {}
        eventsByEnd = {}
        print(searchString)
        # query the db on event names containging the search string
        eventsName = db.query(Event).filter(Event.name.contains(searchString)).all()
        eventsLocation = db.query(Event).filter(Event.location.contains(searchString)).all()

        # query the db for persons whose first and/or last name contain the search string
        personsFirstName = db.query(Person).filter(Person.firstname.contains(searchString)).all()
        personsLastName = db.query(Person).filter(Person.lastname.contains(searchString)).all()

        # Convert the user query to a date query
        for month in months:
            if month in searchString.lower():
                # searchString is a date query
                monthNumber = months[month]
                if any(char.isdigit() for char in searchString):
                    numbers = re.findall(r'\d+', searchString)
                    dayNumber = numbers[0]
                    if int(dayNumber) < 10:
                        dayNumber = "0" + dayNumber
                    yearNumber = ''
                    if len(numbers) > 1:
                        yearNumber = numbers[1] + '-'
                    dateString = yearNumber + monthNumber + "-" + dayNumber
                    eventsByBegin = db.query(Event).filter(Event.begin.contains(dateString)).all()
                    eventsByEnd = db.query(Event).filter(Event.end.contains(dateString)).all()
                else:
                    eventsByBegin = db.query(Event).filter(extract('month', Event.begin) == monthNumber).all()
                    eventsByEnd = db.query(Event).filter(extract('month', Event.end) == monthNumber).all()

        for event in eventsByBegin:
            if event.id not in returnData:
                eventEntry = {}
                person = db.query(Person).filter(Person.wordpressKey == event.leader).first()
                eventEntry['id'] = event.id
                eventEntry['name'] = event.name
                eventEntry['begin'] = event.begin
                eventEntry['end'] = event.end
                eventEntry['location'] = event.location
                eventEntry['desc'] = event.desc
                eventEntry['leader'] = person.wordpressKey
                eventEntry['cancel'] = event.cancel
                eventEntry['img'] = event.img
                eventEntry['qr_code'] = event.qr_code
                eventEntry['created'] = event.created
                eventEntry['link'] = event.link

                returnData[event.id] = eventEntry

        for event in eventsByEnd:
            if event.id not in returnData:
                eventEntry = {}
                person = db.query(Person).filter(Person.wordpressKey == event.leader).first()
                eventEntry['id'] = event.id
                eventEntry['name'] = event.name
                eventEntry['begin'] = event.begin
                eventEntry['end'] = event.end
                eventEntry['location'] = event.location
                eventEntry['desc'] = event.desc
                eventEntry['leader'] = person.wordpressKey
                eventEntry['cancel'] = event.cancel
                eventEntry['img'] = event.img
                eventEntry['qr_code'] = event.qr_code
                eventEntry['created'] = event.created
                eventEntry['link'] = event.link

                returnData[event.id] = eventEntry

        # loop through query result and add the person to the leaders dict if it isn't there already
        for person in personsFirstName:
            if person.id not in leaders:
                leaders[person.id] = person

        # loop through query result and add the person to the leaders dict if it isn't there already
        for person in personsLastName:
            if person.id not in leaders:
                leaders[person.id] = person

        # loop through leaders dict and if it exists get all events that that person leads, if it isn't already in the returnData dict it adds the event
        for personId in leaders:
            person = leaders[personId]
            if db.query(Event).filter(Event.leader == person.wordpressKey).count():
                events = db.query(Event).filter(Event.leader == person.wordpressKey).all()
                for event in events:

                    if event.id not in returnData:
                        eventEntry = {}
                        eventEntry['id'] = event.id
                        eventEntry['name'] = event.name
                        eventEntry['begin'] = event.begin
                        eventEntry['end'] = event.end
                        eventEntry['location'] = event.location
                        eventEntry['desc'] = event.desc
                        eventEntry['leader'] = person.wordpressKey
                        eventEntry['cancel'] = event.cancel
                        eventEntry['img'] = event.img
                        eventEntry['qr_code'] = event.qr_code
                        eventEntry['created'] = event.created
                        eventEntry['link'] = event.link

                        returnData[event.id] = eventEntry

        # loop through eventsName dict and if it isn't already in the returnData dict it adds the event
        for event in eventsName:
            eventEntry = {}

            if event.id not in returnData:
                person = db.query(Person).filter(Person.wordpressKey == event.leader).first()
                eventEntry['id'] = event.id
                eventEntry['name'] = event.name
                eventEntry['begin'] = event.begin
                eventEntry['end'] = event.end
                eventEntry['location'] = event.location
                eventEntry['desc'] = event.desc
                eventEntry['leader'] = person.wordpressKey
                eventEntry['cancel'] = event.cancel
                eventEntry['img'] = event.img
                eventEntry['qr_code'] = event.qr_code
                eventEntry['created'] = event.created
                eventEntry['link'] = event.link

                returnData[event.id] = eventEntry

        for event in eventsLocation:
            eventEntry = {}
            if event.id not in returnData:
                person = db.query(Person).filter(Person.wordpressKey == event.leader).first()
                eventEntry['id'] = event.id
                eventEntry['name'] = event.name
                eventEntry['begin'] = event.begin
                eventEntry['end'] = event.end
                eventEntry['location'] = event.location
                eventEntry['desc'] = event.desc
                eventEntry['leader'] = person.wordpressKey
                eventEntry['cancel'] = event.cancel
                eventEntry['img'] = event.img
                eventEntry['qr_code'] = event.qr_code
                eventEntry['created'] = event.created
                eventEntry['link'] = event.link

                returnData[event.id] = eventEntry
        db.close()
        return returnData

    def savePassword(password, email):
        db = Session()
        person = db.query(Person).filter(Person.email == email).first()
        hashedNewPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
        person.password = hashedNewPassword

        db.commit()
        db.close()
        return 200

    def changePassword(id, oldPassword, newPassword):
        db = Session()
        person = db.query(Person).filter(Person.id == id).first()
        if person.password == oldPassword:
            if checks.emptyCheck([newPassword]) or len(newPassword) < 5 or person.password == newPassword:
                return 400
            else:
                person.password = newPassword
                db.commit()
                db.close()
                return 200
        return 400

    def changeEmail(id):
        db = Session()
        user = db.query(Person).filter(Person.id == id).first()
        secCode = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
        user.securityCode = secCode
        db.commit()
        db.close()
        return 200

    def checkSecCode(oldEmail, secCode):
        db = Session()
        userSecCode = db.query(Person.securityCode).filter(Person.email == oldEmail).first()[0]
        db.close()
        if secCode == userSecCode:
            return True
        return False

    def changeUserEmail(oldEmail, newEmail):
        db = Session()
        user = db.query(Person).filter(Person.email == oldEmail).first()
        user.email = newEmail.lower()
        user.securityCode = None
        db.commit()
        db.close()
        return 200

    def checkPoints(id):
        db = Session()
        points = db.query(Person.points).filter(Person.id == id).first()
        return points

    def addPoints(id):
        db = Session()
        person = db.query(Person).filter(Person.id == id).first()
        person.points = person.points + 1
        db.commit()
        db.close()
        return 200

    def substractPoint(id):
        db = Session()
        person = db.query(Person).filter(Person.id == id).first()

        if person.points <= 0:
            db.commit()
            db.close()
            return 400
        else:
            person.points = person.points - 1
            db.commit()
            db.close()
            return 200

    def resetStampCard(id):
        db = Session()
        person = db.query(Person).filter(Person.id == id).first()

        if person.points >= 15:
            person.points -= 15

            db.commit()
            db.close()
            return 200
        return 400

    def saveMedia(url, eventName):
        db = Session()

        if db.query(Event).filter(Event.name == eventName).count():
            eventId = db.query(Event.id).filter(Event.name == eventName).first()

            newMedia = Media(
                event_id=eventId,
                url=url

            )

            db.add(newMedia)
            db.commit()
            db.close()
            return 200
        else:
            return 400

    def addProfilePhoto(url, id):
        db = Session()

        if db.query(Person).filter(Person.id == id).count():

            person = db.query(Person).filter(Person.id == id).first()
            person.profilePhoto = url

            db.commit()
            db.close()

            return 200
        else:
            return 400

    def getProfilePhoto(id):
        db = Session()

        if db.query(Person).filter(Person.wordpressKey == id).count():

            profilePhoto = db.query(Person.profilePhoto).filter(Person.wordpressKey == id).first()
            db.close()

            return profilePhoto
        else:
            return 400

    def getLeader(id):
        db = Session()

        if db.query(Person).filter(Person.wordpressKey == id).count():
            fName = db.query(Person.firstname).filter(Person.wordpressKey == id).first()
            lName = db.query(Person.lastname).filter(Person.wordpressKey == id).first()

            db.close()
            return checks.fixName(fName, lName)

    def getEventById(eventId):
        db = Session()
        if db.query(Event).filter(Event.id == eventId).count():
            event = db.query(Event).filter(Event.id == eventId).first()
            db.close()
            return event
        else:
            return 400

    def getDescription(id):
        db = Session()

        if db.query(Person).filter(Person.wordpressKey == id).count():
            bio = db.query(Person.biography).filter(Person.wordpressKey == id).first()
            db.close()
            return bio

    def getAllEvents():
        db = Session()
        if db.query(Event).count():
            events = db.query(Event).order_by(Event.begin).all()

            db.close()
            return events
        else:
            return 400

    def getAllAdmins():
        db = Session()
        if db.query(Person).filter(Person.clearance == 1).count():
            admins = db.query(Person).filter(Person.clearance == 1).all()
            db.close()
            return admins
        else:
            return {}

    def getAllSubs(id):
        db = Session()
        print(id)
        if db.query(Particepant).filter(Particepant.person_id == id).count():
            eventIds = db.query(Particepant.event_id).filter(Particepant.person_id == id).all()
            db.close()
            list = []
            for id in eventIds:
                list.append(id[0])
            return list
        else:
            db.close()
            return {}

    def getAllNewsItems():
        db = Session()

        if db.query(Content).count():
            news = db.query(Content).order_by(Content.created).all()
            db.close()
            return news
        else:
            return {}

    def getAllSubbedEvents(eventId):
        db = Session()

        results = []
        for id in eventId:
            event = db.query(Event).filter(Event.id == id).all()
            results.append(event)
        db.close()
        print("dit zijn de evenementen", results)
        return results

    def getPersons():
        db = Session()
        if db.query(Person).count():
            users = db.query(Person).all()
            db.close()
            return users
        else:
            db.close()
            return {}

    def getEventName(item):
        db = Session()

        eventNames = db.query(Event.name).filter(Event.id == item).all()
        db.close()
        return eventNames


Base.metadata.create_all(conn)
