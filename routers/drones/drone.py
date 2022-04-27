from fastapi import HTTPException, APIRouter
from fastapi_sqlalchemy import db
from models import User, DrivingSessions, Drone
import schemas
import time
from . import drone_functions

router = APIRouter()
tag = "2 Drones"


# ######################################################################################################################
# GET SECTION
# ######################################################################################################################


@router.get("/drones/", tags=[tag])
def get_drones():
    # Tehdaan tietokantakysely joka hakee kaikki dronet
    drones = db.session.query(Drone).all()
    return drones


@router.post("/new-drone/", tags=[tag])
def add_drone(new_drone: schemas.DroneIn):
    # Luodaan uusi drone Schemasta DroneIn ja lisataan se tietokantaan
    drone = Drone(
        brand=new_drone.brand,
        model=new_drone.model,
        additional_info=new_drone.additional_info,
    )
    db.session.add(drone)
    db.session.commit()
    return {"message": f"Drone {drone.id} created"}


@router.get("/get-all-drive-sessions", tags=[tag])
def get_all_drive_sessions():
    # Tehdaan tietokantakysely joka hakee jokaisen ajosession tiedot
    sessions = db.session.query(DrivingSessions).all()
    return sessions


@router.get("/get-drive-session-by-id/{session_id}", tags=[tag])
def get_drive_session_by_id(session_id: int):
    # Tehdaan tietokantakysely joka hakee ajosession tiedot session_id:n perusteella
    session = db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id).first()
    return session


# ######################################################################################################################
# POST SECTION
# ######################################################################################################################


@router.post("/rent-drone/{username}/drone-{drone_id}", tags=[tag])
def rent_drone(username: str, drone_id: int):
    # 1.  Luodaan aluksi kaksi tietokantakyselya jotka hakee:
    #         Kayttajanimen, kayttajan login_statuksen seka, kayttaja id:n seka sen, onko kayttajalla drone ajossa
    #         drone_id:n seka dronen statusksen, onko se vapaana vai ei
    # 2.  Ajetaan error_handler funktio, jossa tarkastetaan etta kaikki on ok
    # 3.  Ajetaan start_driving funktio, jossa asetetaan dronen ja kayttajan idt ajosessiolle
    #     seka merkataan aloitusaika
    query_user = db.session.query(User.username, User.login_status, User.id, User.have_drone_in_use).filter(
        User.username == username).first()
    query_drone = db.session.query(Drone.id, Drone.booked_status).filter(Drone.id == drone_id).first()
    drone_functions.error_handler_on_rent(query_user, query_drone, username, drone_id)
    start_driving_id = drone_functions.start_driving_func(query_user, query_drone, drone_id)
    return {
        "msg": f"Drone {drone_id} booked",
        "session_id": start_driving_id,
        "On Return": f"Give username '{username}' and session_id {start_driving_id}"
    }


@router.post("/return-drone/{username}/{session_id}", tags=[tag])
def return_drone(username: str, session_id: int):
    # 1.  Tehdaan tietokantakysely User-taulusta, josta haetaan kayttajan id, loginstatus, kayttajanimi seka tieto,
    #     onko drone kaytossa
    # 2.  Tehdaan tietokantakysely DrivingSessions-taulusta drivingsessions-id:n perusteella
    # 3.  Ajetaan error_handler funktio, jossa tarkastetaan etta kaikki on ok
    # 3.  Ajetaan add_end_time funktio missa paivitetaan ajosession paattymisaika
    # 4.  Ajetaan get_session_length funktio missa lasketaan ajosession pituus
    # 5.  Lisataan ajosession tietoja tietokantaan update_session_length funktion kautta
    # 6.  Luodaan viimeinen tietokantakysely joka hakee ajosession pituuden tiedon

    query_user = db.session.query(User.username, User.login_status,
                                  User.id, User.have_drone_in_use).filter(User.username == username).first()
    query_session = db.session.query(DrivingSessions).filter(DrivingSessions.id == session_id).first()
    drone_functions.error_handler_on_return(query_user, query_session, username)
    drone_functions.add_end_time(session_id)
    diff = drone_functions.get_session_length(session_id)
    drone_functions.update_session_length(session_id, diff, username, query_session.drone_id)

    length = db.session.query(DrivingSessions.drive_session_length).filter(DrivingSessions.id == session_id).first()[0]
    return {
        "session_status": f"Drone session {session_id} ended",
        "drone_returned": f"Drone {query_session.drone_id} returned",
        "session_length": length
    }
