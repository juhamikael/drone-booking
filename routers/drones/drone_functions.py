from models import User, DrivingSessions, Drone
import time
from fastapi_sqlalchemy import db
from fastapi import HTTPException


def start_driving_func(query_user, query_drone, drone_id):
    """
    1.  Asetetaan parametreista saadusta kayttajasta seka dronesta id tietokantaan
    2.  Asetetaan ajon alkamisaika tietokantaan
    3.  Asetetaan dronen booked_status arvoksi True
    4.  Asetetaan kayttajan have_drone_in_use arvoksi True
    5.  Tallennetaan tietokantaan

    """
    start_driving = DrivingSessions(
        user_id=query_user.id,
        drone_id=query_drone.id,
        drive_session_started=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    )
    db.session.query(Drone).filter(Drone.id == drone_id).update({Drone.booked_status: True})
    db.session.query(User).filter(User.id == query_user.id).update({User.have_drone_in_use: True})
    db.session.add(start_driving)
    db.session.commit()
    return start_driving.id


def user_not_found_nor_logged_in(user_query, username):
    """
    Tarkistetaan onko kayttajanimi olemassa tai onko kayttaja kirjautunut sisalle

    Args:
        user_query (object): Parametrina saatu tietokantakysely
        username (str): Requestissa saadun kayttajan kayttajanimi

    Raises:
        HTTPException: 400 Bad Request, "User not found"
        HTTPException: 400 Bad Request, "User not logged in"
    """
    if not user_query:
        raise HTTPException(status_code=400, detail={"msg": "User not found"})
    if not user_query.login_status:
        raise HTTPException(status_code=400, detail=f"Not logged in as a '{username}'")


def error_handler_on_rent(user_query, drone_query, username, drone_id):
    """
    - Tarkistaa virheet dronen käyttöönotto pyynnössä

    Args:
        user_query (object): --
        drone_query (object): 
        username (str): --
        drone_id (int): --

    Raises:
        HTTPException: 400 Bad Request, "Drone not found"
        HTTPException: 400 Bad Request, "User already has a drone in use"
        HTTPException: 400 Bad Request, "Drone {drone_id} is already booked"
    """
    user_not_found_nor_logged_in(user_query, username)
    if not drone_query:
        raise HTTPException(status_code=400, detail={"msg": "Drone not found"})
    if user_query.have_drone_in_use:
        raise HTTPException(status_code=400, detail={"msg": "User already has a drone in use"})
    if drone_query.booked_status:
        raise HTTPException(status_code=400, detail=f"Drone {drone_id} is already booked")


def error_handler_on_return(user_query, session_query, username):
    """
    - Tarkistaa virheet dronen palautus pyynnössä
    """
    user_not_found_nor_logged_in(user_query, username)
    if session_query.user_id != user_query.id:
        raise HTTPException(status_code=400, detail={"msg": "User is not the owner of this session"})
    if not user_query.have_drone_in_use:
        raise HTTPException(status_code=400, detail=f"User '{username}' does not have a drone in use")
    if not session_query:
        raise HTTPException(status_code=400, detail=f"Session {session_query.id} not found")
    if session_query.session_ended:
        raise HTTPException(status_code=400, detail=f"Session {session_query.id} already ended")


def add_end_time(session_id: int):
    """
    1.  Haetaan taman hetkinen aika
    2.  Tehdaan tietokantakysely ja paivitetaan tietokantaan kayttajan ajosession paattymisaika
    3.  Lahetetaan tietokantaan paivitetty ajosession tiedot
    4.  Lisataan tiedot tietokantaan

    """
    timenow = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id) \
        .update({DrivingSessions.drive_session_ended: timenow})
    db.session.commit()


def get_session_length(session_id: int):
    """
    1.  Tehdaan  tietokantakysely, joka hakee ajosession tiedot, tassa mukana nyt paattymisaika
    2.  Haetaan Ajon alkamisaika seka lopetusaika ja lasketaan naiden valinen erotus
    """
    # 
    new_session = db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id).first()
    session_started = new_session.drive_session_started
    session_ended = new_session.drive_session_ended
    difference = session_ended - session_started
    return difference.seconds


def update_session_length(session_id: int, diff, username: str, session_drone_id: int):
    """
    1.  Paivitetaan tietokantaan ajon kesto, kaytetaan aiemmin luotua 'diff' muuttujaa
    2.  Muutetaan kayttajan palauttaman dronen tilaksi False seka vaihdetaan kayttajan 'have_drone_in_use' arvoksi False
    3.  Paivitetaan ajo sessio paattyneeksi
    """
    db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id) \
        .update({DrivingSessions.drive_session_length: diff})
    db.session.query(Drone).filter(Drone.id == session_drone_id).update({Drone.booked_status: False})
    db.session.query(User).filter(User.username == username).update({User.have_drone_in_use: False})
    db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id).update(
        {DrivingSessions.session_ended: True})
    db.session.commit()

