import bcrypt


def hash_password(password):
    password = password.encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(14))
    return hashed
#

