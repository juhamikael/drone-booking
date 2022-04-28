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
    new_user = user_schema.dict()
    user_list = [user.__dict__ for user in all_users]
    for i in user_list:
        if new_user['username'] == i['username'] and new_user['email'] == i['email']:
            raise HTTPException(status_code=400, detail='Username and Email already exists')
        if new_user['username'] == i['username']:
            raise HTTPException(status_code=400, detail='Username already exists')
        if new_user['email'] == i['email']:
            raise HTTPException(status_code=400, detail='Email already exists')
