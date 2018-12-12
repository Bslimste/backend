from Database import Persister, Content, Person
import datetime

def getPerson(person_id):
    return Persister.getPerson(person_id)



def getUsers():
    users = Persister.getPersons()
    if users != 400:
        result = []
        for user in users:
            name = user.firstname + " " + user.lastname
            result.append({"id": user.id, "name": name, "email": user.email})

    return result


def getUserByEmail(emailLogin):
    return Persister.getUserWithEmail(emailLogin)

def getEmail(emailLogin):
    return Persister.getEmail(emailLogin)

def getPassword(email):
    return Persister.getPassword(email)

def checkEmailExistance(email):
    return Persister.checkEmailExistance(email)

def saveNewPassword(temp,email):
    if Persister.checkEmailExistance(email):
        return Persister.savePassword(temp,email) #change to hashed
    else:
        return 400

def changePassword(id, oldPassword, newPassword):
    return Persister.changePassword(id, oldPassword, newPassword)

def changeEmail(id):
    return Persister.changeEmail(id)

def checkSecCode(oldEmail, secCode):
    return Persister.checkSecCode(oldEmail, secCode)

def changeUserEmail(oldEmail, newEmail):
    return Persister.changeUserEmail(oldEmail, newEmail)

def checkPoints(id):
    return Persister.checkPoints(id)

def addPoints(id):
    return Persister.addPoints(id)

def substractPoint(id):
    return Persister.substractPoint(id)

def resetStampCard(id):
    return Persister.resetStampCard(id)

def addProfilePhoto(url):
    return Persister.addProfilePhoto(url,id)

def getProfilePhoto(id):
    return Persister.getProfilePhoto(id)

def getAllAdmins():
    admins = Persister.getAllAdmins()
    if admins != 400:
        result = []
        for admin in admins:
            result.append({"id": admin.id, "firstName": admin.firstname, "lastName": admin.lastname})

    return result

def deleteNewsItem(id):
    return Persister.remove_news(id)

def createNewsItem(id, title, content, img):
    if (id == '' or title == '' or
            content == '' or
            img == ''):
        return 400
    item = Content(
        id=id,
        url=img,
        title=title,
        desc=content,
        link=None,
        created=datetime.datetime.now()
    )
    return Persister.persist_object(item)

def createNewsItemApp(title, content, img):
    if (title == '' or
            content == '' or
            img == ''):
        return 400 
    item = Content( 
        url=img,    
        title=title, 
        desc=content,
        link=None,
        created=datetime.datetime.now()
    )
    return Persister.persist_object(item)
