from fastapi import HTTPException


def check_password(password):
    # Password min length = 8, have at least one UpperCase, one LowerCase and one number
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    return password


def check_errors(user_schema, all_users: list):
    # Sijoitetaan uuden kayttajan request muuttujaan new_user jonka tyyppi on dict / json
    new_user = user_schema.dict()
    # Ja luodaan lista kaikista kayttajista
    user_list = [user.__dict__ for user in all_users]
    # Verrataan kayttajalistasta jokaisen kayttajan
    # Sahkopostia ja kayttajanimea uuden kayttajan sahkopostiin ja kayttajanimiin
    for i in user_list:
        if new_user['username'] == i['username'] and new_user['email'] == i['email']:
            raise HTTPException(status_code=400, detail='Username and Email already exists')
        if new_user['username'] == i['username']:
            raise HTTPException(status_code=400, detail='Username already exists')
        if new_user['email'] == i['email']:
            raise HTTPException(status_code=400, detail='Email already exists')
    return True
    # Jos kaikki on ok, palautetaan true, muutoin nostetaan virhe ilmoitus