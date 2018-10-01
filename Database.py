import sqlalchemy as sqla
from flask import jsonify
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_login import UserMixin
import checks


conn = sqla.create_engine('mysql+pymysql://root:@localhost/bslim?charset=utf8')

Session = scoped_session(sessionmaker(bind=conn))

Base = declarative_base()

class Person(Base,UserMixin):
    __tablename__ = 'person'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True, unique=True)
    firstname = sqla.Column('firstname', sqla.VARCHAR(64))
    lastname = sqla.Column('lastname', sqla.VARCHAR(64))
    email = sqla.Column('email', sqla.VARCHAR(64), unique=True)
    password = sqla.Column('password', sqla.VARCHAR(64))
    points = sqla.Column('points',sqla.Integer)
    clearance = sqla.Column('clearance',sqla.Integer)
    license = sqla.Column('license',sqla.Boolean)
    authenticated = sqla.Column('authenticated', sqla.Boolean)
    profilePhoto = sqla.Column('profilePhoto', sqla.VARCHAR(200))

class Event(Base):
    __tablename__ = 'event'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True , unique=True)
    name = sqla.Column('name',sqla.VARCHAR(64))
    begin = sqla.Column('begin',sqla.DATETIME)
    end = sqla.Column('end',sqla.DATETIME)
    location = sqla.Column('location',sqla.VARCHAR(64))
    desc = sqla.Column('desc',sqla.VARCHAR(200))
    leader = sqla.Column('leader',sqla.Integer,sqla.ForeignKey('person.id'))
    cancel = sqla.Column('cancel',sqla.Integer)
    img = sqla.Column('img',sqla.VARCHAR(200))
    qr_code = sqla.Column('qr_code',sqla.VARCHAR(200))

class Content(Base):
    __tablename__ = 'content'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True , unique=True)
    url = sqla.Column('url',sqla.VARCHAR(200))
    title = sqla.Column('title',sqla.VARCHAR(64))
    desc = sqla.Column('desc',sqla.VARCHAR(300))

class Particepant(Base):
    __tablename__ = 'particepant'
    person_id = sqla.Column('person_id',sqla.Integer,sqla.ForeignKey('person.id'), primary_key=True)
    event_id = sqla.Column('event_id',sqla.Integer,sqla.ForeignKey('event.id'), primary_key=True)
    event_scanned = sqla.Column('event_scanned',sqla.Boolean)

class Media(Base):
    __tablename__ = 'media'
    event_id = sqla.Column('event_id',sqla.Integer,sqla.ForeignKey('event.id'), primary_key=True)
    url = sqla.Column('url',sqla.VARCHAR(200))




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
        person = db.query(Person).filter(Person.id == user.id).first()
        if not person.authenticated:
            person.authenticated = True
            db.commit()
            db.close()
            return True
        return False

    def logoutUser(user):
        db = Session()
        person = db.query(Person).filter(Person.id == user.id).first()
        if person.authenticated:
            person.authenticated = False
            db.commit()
            db.close()
            return True
        return False

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

    def persist_object(obj):
        db = Session()
        try:
            db.add(obj)
            db.commit()
        except:
            db.close()
            return 400
        db.close()
        return 200

    # Check if QR code is already scanned
    # If the user has not subscribed himself to the event and both the user and the event exists the user is automaticly subscribed to the event.
    def isScanned(eventId,personId):
        db = Session()
        particepant = db.query(Particepant).filter(Particepant.person_id == personId)\
                                           .filter(Particepant.event_id == eventId)\
                                           .first()
        db.close()
        if particepant == None:
            if(db.query(Event).filter(Event.id == eventId).count()):
                if(db.query(Person).filter(Person.id == personId).count()):
                    db = Session()
                    newParticepant = Particepant(
                        person_id=personId,
                        event_id=eventId,
                        event_scanned=0
                    )
                    db.add(newParticepant)
                    db.commit()
                    db.close()
                    particepant = db.query(Particepant).filter(Particepant.person_id == personId)\
                                           .filter(Particepant.event_id == eventId)\
                                           .first()
                    return particepant.event_scanned
        elif particepant.event_scanned:
            return 400
        return 200

    # Checks whether or not a particepant entry or beloging events and persons already exists
    def checkParticepant(eventId, personId):
        db = Session()
        if(db.query(Event).filter(Event.id == eventId).count()):
                if(db.query(Person).filter(Person.id == personId).count()):
                    if(db.query(Particepant).filter(Particepant.person_id == personId).filter(Particepant.event_id == eventId).count()):
                        db.close()
                        return True
        db.close()
        return False

    # Marks the particepant entry as scannend and adds a point to the user account
    def updateParticepantInfo(event_id, person_id):
        db = Session()
        particepant = db.query(Particepant).filter(Particepant.person_id == person_id)\
                                           .filter(Particepant.event_id == event_id)\
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
            print(event)
            db.close()
            return event
        db.close()
        return False
      
    def savePassword(password, email):
        db = Session()
        person = db.query(Person).filter(Person.email == email).first()

        person.password = password

        db.commit()
        db.close()
        return 200

    def savePasswordHashed(password, email):
        db = Session()
        person = db.query(Person).filter(Person.email == email).first()

        person.password = pbkdf2_sha256.hash(password)

        db.commit()
        db.close()
        return 200

    def changePassword(id, oldPassword, newPassword):
        db = Session()
        print(id)
        person = db.query(Person).filter(Person.id == id).first()
        # hashedNewPassword = pbkdf2_sha256.hash(newPassword) CHANGE BACK
        hashedNewPassword = newPassword
        if person.password == oldPassword:
            if checks.emptyCheck([newPassword]) or len(newPassword) < 5 or person.password == hashedNewPassword:
                return 400
            else:
                person.password = hashedNewPassword
    
                db.commit()
                db.close()
                return 200
        return 400


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
            person.points = 0

            db.commit()
            db.close()
            return 200

    def saveMedia(url,eventName):
        db = Session()

        if db.query(Event).filter(Event.name == eventName).count():
            eventId = db.query(Event.id).filter(Event.name == eventName).first()

            newMedia = Media(
                event_id=eventId,
                url = url

            )

            db.add(newMedia)
            db.commit()
            db.close()
            return 200
        else:
            return 400

    def addProfilePhoto(url,id):
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

        if db.query(Person).filter(Person.id == id).count():

            profilePhoto = db.query(Person.profilePhoto).filter(Person.id == id).first()
            db.close()

            return profilePhoto
        else:
            return 400



Base.metadata.create_all(conn)