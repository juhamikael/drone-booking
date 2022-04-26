from sqlalchemy import DATE, Column, Integer, String, Float, ForeignKey, TIMESTAMP, TEXT, JSON, Boolean, TIME
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False, unique=True)
    username = Column(String(64), nullable=False, unique=True)
    password = Column(TEXT, nullable=False)
    login_status = Column(Boolean, nullable=False, default=False)
    have_drone_in_use = Column(Boolean, nullable=False, default=False)


class DrivingSessions(Base):
    __tablename__ = "driving_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    drone_id = Column(Integer, ForeignKey('drone.id'))
    drive_session_started = Column(TIMESTAMP, nullable=False)
    drive_session_ended = Column(TIMESTAMP, nullable=True)
    drive_session_length = Column(TIME, nullable=True)
    session_ended = Column(Boolean, nullable=False, default=False)


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(64))
    user_id = Column(Integer, ForeignKey('user.id'))


class Drone(Base):
    __tablename__ = "drone"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(64))
    model = Column(String(64))
    additional_info = Column(JSON)
    booked_status = Column(Boolean, nullable=False, default=False)



class Images(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    info = Column(String(64))
    date = Column(DATE)
    coordinates = Column(String(64))
    drone_id = Column(Integer, ForeignKey('drone.id'))
    address_id = Column(Integer, ForeignKey('address.id'))


Base.metadata.create_all(engine)
