from datetime import datetime, timedelta

def checkSpecialChars(items):
    for item in items:
        if set('[~!#$%^&*+":;\']+$').intersection(item):
            return True
    return False


def checkSpecialCharsEmail(email):
    return set('[~!#$%^&*()_+{}":;\']+$').intersection(email)


def passwordLengthCheck(password):
    check1 = len(password) < 5
    check2 = len(password) > 64
    if check1:
        return [False, "short"]
    if check2:
        return [False, "long"]
    else:
        return [True, ""]

# Returns True if one of the items is empty
def emptyCheck(items):
    count = 0
    for item in items:
        if not item:
            print(count)
            return True
        count += 1
    return False

def lengthSixtyFourCheck(items):
    for item in items:
        if len(item) > 64:
            return True
    return False

def fixName(fName,lName):
    if '_' in str(fName):
        voornaam = " ".join([x for x in fName]).replace('_',' ')
        achternaam = "".join([x for x in lName])
        name = voornaam + " "  + achternaam
        return name
    elif '_' not in str(fName):
        voornaam = "".join([x for x in fName])
        achternaam = "".join([x for x in lName])
        name = voornaam + " "  + achternaam
        return name

