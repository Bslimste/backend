from Database import Persister, Particepant, Event
import string, random
from passlib.handlers.pbkdf2 import pbkdf2_sha256


# returns 200 to indicate successful updating of the particepant info
def eventScanned(event_id, person_id):
    return Persister.updateParticepantInfo(event_id, person_id)

# Checks whether an event has already been scannend by the user scanning it.
def isScanned(eventId, person_id):
    return Persister.isScanned(eventId, person_id)

# returns 
def findEvent(qrCode):
	return Persister.findEvent(qrCode)

def createEvent(id,name,begin,end,location,description,leader,img):
	size=6
	chars=string.ascii_uppercase + string.digits
	unHashed = ''.join(random.choice(chars) for _ in range(size))
	qr_code = pbkdf2_sha256.hash(unHashed)

	if(id or
	   name or
	   begin or
	   end or
	   location or
	   description or
	   leader == None):
		return 400

	event = Event(
			id=id,
			name=name,
			begin=begin,
			end=end,
			location=location,
			desc=description,
			leader=leader,
			cancel=0,
			img=img,
			qr_code=qr_code
		)
	return Persister.persist_object(event)

def subToEvent(eventId, personId):
	if not Persister.checkParticepant(eventId, personId):
		particepant = Particepant(
				person_id=personId,
				event_id=eventId,
				event_scanned=0
			)
		return ({"responseCode": Persister.persist_object(particepant), "msg": "Added particepant entry."})
	return ({"responseCode": 400, "msg": "Could not add participant entry because either some of the given data did not match or the entry already exists."})

def saveMedia(url, eventName):
    return Persister.saveMedia(url, eventName)