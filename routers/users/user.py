from fastapi import APIRouter, HTTPException
from typing import List
import schemas
from models import User
from fastapi_sqlalchemy import db
import bcrypt
from . import user_functions

router = APIRouter()
tag = "1 Sign in | Sign out | Sign Up"


@router.get("/users", tags=[tag], response_model=List[schemas.UserOut])
def get_user():
    # Tehdaan tietokantakysely joka hakee kaikki kayttajat,
    # Kaytetaan schemaa UserOut, jotta salasana ei nay pyynnossa

    users = db.session.query(User).all()
    return users


@router.post("/user/", tags=[tag], summary="Create new users")
def new_user(create_new_user: schemas.UserIn):
    # Uutta kayttajaa luodessa jarjestelmaan, tarkistetaan ensin, etta kayttajanimi tai sahkoposti ei ole kaytossa
    user = db.session.query(User).all()
    user_functions.check_errors(create_new_user, user)

    # print(f"\n\n\n---New User info{create_new_user}\n\n\n")
    # print(f"\n\n\n---New User info{user}\n\n\n")

    # if user:
    #     raise HTTPException(status_code=400, detail="User already exists")

    # Tarkistetaan etta salasana tayttaa vaatimukset
    password = user_functions.check_password(create_new_user.password)
    if not password:
        raise HTTPException(status_code=400, detail={"msg": "Password is too weak",
                                                     "detailed msg": "Password must be at least 8 characters long, "
                                                                     "have at least one uppercase lowercase "
                                                                     "and number"})
    # Kryptataan salasana
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14))
    # Luodaan uusi kayttaja Schemasta UserIn ja lisataan se tietokantaan
    user = User(
        name=create_new_user.name,
        email=create_new_user.email,
        username=create_new_user.username,
        password=hashed_pw.decode('utf-8'),
    )
    db.session.add(user)
    db.session.commit()
    return {"message": f"User {user.username} created {user.email}"}


@router.post("/login/", tags=[tag], summary="Login users")
def user_login(login: schemas.Login):
    # Tallennetaan 'request':in kayttajanimi seka salasana muuttujiin
    username = login.username
    password = login.password
    # Tehdaan tietokanta kysely, joka hakee kayttajanimen, login statuksen seka salasanan
    user = db.session.query(User.username, User.login_status, User.password).filter(User.username == username).first()
    if not username:
        raise HTTPException(status_code=400, detail={"msg": "User not found"})
    # Verratan annetun salasanan seka tietokantaan tallennetun salasanan hasheja keskenaan
    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # Mikali salasanat tasmaavat, asetetaan kayttajan login_status arvoksi True ja tallennetaan tietokantaan
        db.session.query(User).filter(User.username == username).update({User.login_status: True})
        db.session.commit()
        return "Login successful"
    else:
        return "Incorrect password"


@router.post("/{username}/logout/", tags=[tag], summary="Logout users")
def user_logout(username: str):
    # Tehdaan tietokanta kysely, joka hakee kayttajanimen
    query_user = db.session.query(User.username, User.login_status).filter(User.username == username).first()
    if not query_user:
        raise HTTPException(status_code=400, detail={"msg": "User not found"})
    # Jos kayttajan loginstatus on False, palautetaan virheilmoitus
    if not query_user.login_status:
        return f"User '{username}' is not logged in"
    # Muutoin asetetaan kayttajan loginstatus arvoksi False ja tallennetaan tietokantaan
    db.session.query(User).filter(User.username == username).update({User.login_status: False})
    db.session.commit()
    return "Logout successful"
