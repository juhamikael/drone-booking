from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import db
import os
from dotenv import load_dotenv
from models import User, DrivingSessions, Drone
import schemas
import time
from typing import List
import bcrypt

load_dotenv()

app = FastAPI()
app.add_middleware(
    DBSessionMiddleware,
    db_url=os.getenv('DATABASE_URL'))
origins = [
    "http://localhost",
]
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"], )


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


@app.get("/", tags=["ROOT"], summary="Root redirect")
async def docs_redirect():
    # Uudelleen ohjataan käyttäjä docs-sivulle
    return RedirectResponse(url='/docs')


@app.get("/drones/")
def get_drones():
    # Tehdään tietokantakysely joka hakee kaikki dronet
    drones = db.session.query(Drone).all()
    return drones


@app.get("/users", response_model=List[schemas.UserOut])
def get_user():
    # Tehdään tietokantakysely joka hakee kaikki käyttäjät, käytetään schemaa UserOut
    # Jotta salasana ei näy pyynnässä
    users = db.session.query(User).all()
    return users


@app.post("/user/")
def new_user(create_new_user: schemas.UserIn):
    # Uutta käyttäjää luodessa järjestelmään, tarkistetaan ensin, että käyttäjänimi tai sähkäposti ei ole käytässä
    user = db.session.query(User.username, User.email).filter(User.username == create_new_user.username,
                                                              User.email == create_new_user.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    # Tarkistetaan että salasana täyttää vaatimukset
    password = check_password(create_new_user.password)
    if not password:
        raise HTTPException(status_code=400, detail={"msg": "Password is too weak",
                                                     "detailed msg": "Password must be at least 8 characters long, "
                                                                     "have at least one uppercase lowercase "
                                                                     "and number"})
    # Kryptataan salasana
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14))
    # Luodaan uusi käyttäjä Schemasta UserIn ja lisätään se tietokantaan
    user = User(
        name=create_new_user.name,
        email=create_new_user.email,
        username=create_new_user.username,
        password=hashed_pw.decode('utf-8'),
    )
    db.session.add(user)
    db.session.commit()
    return {"message": f"User {user.username} created {user.email}"}


@app.post("/login/")
def user_login(login: schemas.Login):
    # Tallennetaan 'request':in käyttäjänimi sekä salasana muuttujiin
    username = login.username
    password = login.password
    # Tehdään tietokanta kysely, joka hakee käyttäjänimen, login statuksen sekä salasanan
    user = db.session.query(User.username, User.login_status, User.password).filter(User.username == username).first()
    if not username:
        raise HTTPException(status_code=400, detail={"msg": "User not found"})
    # Verratan annetun salasanan sekä tietokantaan tallennetun salasanan hasheja keskenään
    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # Mikäli salasanat täsmäävät, asetetaan käyttäjän login_status arvoksi True ja tallennetaan tietokantaan
        db.session.query(User).filter(User.username == username).update({User.login_status: True})
        db.session.commit()
        return "Login successful"
    else:
        return "Incorrect password"


@app.post("/{username}/logout/")
def user_logout(username: str):
    # Tehdään tietokanta kysely, joka hakee käyttäjänimen
    query_user = db.session.query(User.username, User.login_status).filter(User.username == username).first()
    if not query_user:
        raise HTTPException(status_code=400, detail={"msg": "User not found"})
    # Jos käyttäjän loginstatus on False, palautetaan virheilmoitus
    if not query_user.login_status:
        return f"User '{username}' is not logged in"
    # Muutoin asetetaan käyttäjän loginstatus arvoksi False ja tallennetaan tietokantaan
    db.session.query(User).filter(User.username == username).update({User.login_status: False})
    db.session.commit()
    return "Logout successful"


@app.post("/new-drone/")
def add_drone(new_drone: schemas.DroneIn):
    # Luodaan uusi drone Schemasta DroneIn ja lisätään se tietokantaan
    drone = Drone(
        brand=new_drone.brand,
        model=new_drone.model,
        additional_info=new_drone.additional_info,
    )
    db.session.add(drone)
    db.session.commit()
    return {"message": f"Drone {drone.id} created"}


@app.post("/rent-drone/{username}/drone-{drone_id}")
def rent_drone(username: str, drone_id: int):
    # Luodaan kaksi tietokantakyselyä jotka hakee:
    # Käyttäjänimen, käyttäjän login_statuksen sekä, käyttäjä id:n sekä sen, onko käyttäjällä drone ajossa
    # drone_id:n sekä dronen status, onko vapaa vai ei
    query_user = db.session.query(User.username, User.login_status, User.id, User.have_drone_in_use).filter(
        User.username == username).first()
    query_drone = db.session.query(Drone.id, Drone.booked_status).filter(Drone.id == drone_id).first()
    if not query_user:
        raise HTTPException(status_code=400, detail={"msg": "User not found"})
    if not query_drone:
        raise HTTPException(status_code=400, detail={"msg": "Drone not found"})
    if query_user.have_drone_in_use:
        raise HTTPException(status_code=400, detail={"msg": "User already has a drone in use"})
    if not query_user.login_status:
        return f"Not logged in as a '{username}'"
    if query_drone.booked_status:
        return f"Drone {drone_id} is already booked"

    # Asetetaan dronen varauksen status arvoksi True ja tallennetaan tietokantaan
    db.session.query(Drone).filter(Drone.id == drone_id).update({Drone.booked_status: True})
    db.session.query(User).filter(User.username == username).update({User.have_drone_in_use: drone_id})
    start_driving = DrivingSessions(
        user_id=query_user.id,
        drone_id=query_drone.id,
        drive_session_started=time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    )
    db.session.add(start_driving)
    db.session.commit()
    return {
        "msg": f"Drone {drone_id} booked",
        "session_id": start_driving.id,
        "On Return": f"Give username '{username}' and session_id {start_driving.id}"
    }


@app.post("/return-drone/{username}/{session_id}")
def return_drone(username: str, session_id: int):
    # Tehdään tietokantakysely User-taulusta,
    # haetaan käyttäjän id, loginstatus, käyttäjänimi sekä tieto, onko drone käytässä
    query_user = db.session.query(User.username,
                                  User.login_status,
                                  User.id,
                                  User.have_drone_in_use).filter(User.username == username).first()
    # Tehdään tietokantakysely DrivingSessions-taulusta drivingsessions-id:n perusteella
    query_session = db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id).first()
    if not query_user:
        raise HTTPException(status_code=400, detail={"msg": "User not found"})
    if not query_user.login_status:
        return f"Not logged in as a '{username}'"
    if not query_user.have_drone_in_use:
        return f"User '{username}' does not have a drone in use"
    if not query_session:
        return f"Session {query_session.session_id} not found"
    # Haetaan tämän hetkinen aika
    timenow = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())

    # ################################################################################
    # Tehdään tietokantakysely ja päivitetään tietokantaan käyttäjän ajosession päättymisaika
    db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id) \
        .update({DrivingSessions.drive_session_ended: timenow})
    # Lähetetään tietokantaan päivitetty ajosession tiedot
    db.session.commit()

    # ################################################################################
    # Tehdään uusi tietokantakysely, joka hakee ajosession tiedot, tässä mukana myäs päättymisaika
    new_session = db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id).first()
    # Haetaan Ajon alkamisaika sekä lopetusaika ja lasketaan näiden välinen erotus
    session_started = new_session.drive_session_started
    session_ended = new_session.drive_session_ended
    diff = session_ended - session_started

    # ################################################################################
    # Päivitetään tietokantaan ajon kesto, käytetään aiemmin luotua 'diff' muuttujaa
    db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id) \
        .update({DrivingSessions.drive_session_length: diff})
    # Muutetaan käyttäjän palauttaman dronen tilaksi False sekä vaihdetaan käyttäjän 'have_drone_in_use' arvoksi False
    db.session.query(Drone).filter(Drone.id == query_session.drone_id).update({Drone.booked_status: False})
    db.session.query(User).filter(User.username == username).update({User.have_drone_in_use: False})
    # Päivitetään ajo sessio päättyneeksi
    db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id).update(
        {DrivingSessions.session_ended: True})
    db.session.commit()
    # Lopuksi vielä tietokantakysely joka hakee ajosession pituuden tiedon
    length = db.session.query(DrivingSessions.drive_session_length).filter(DrivingSessions.id == session_id).first()[0]
    return {
        "msg": f"Drone {query_user} returned",
        "session_length": length
    }


@app.get("/get-all-drive-sessions")
def get_all_drive_sessions():
    sessions = db.session.query(DrivingSessions).all()
    return sessions


@app.get("/get-drive-session-by-id/{session_id}")
def get_drive_session_by_id(session_id: int):
    session = db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id).first()
    session_started = session.drive_session_started
    session_ended = session.drive_session_ended
    print("Session started: ", session_ended, type(session_ended))
    print("Session ended: ", session_ended, type(session_ended))
    diff = session_ended - session_started
    print("Diff", diff)
    return session

# drone_use_date_started=

# user_id = Column(Integer, ForeignKey('user.id'))
# drone_id = Column(Integer, ForeignKey('drone.id'))
# drone_use_date_started = Column(TIMESTAMP, nullable=False)
# drone_use_date_ended = Column(TIMESTAMP, nullable=True)
# drone_drive_length = Column(Float, nullable=True)

# hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
