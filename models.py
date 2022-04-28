from sqlalchemy import DATE, Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy import TEXT, JSON, Boolean, TIME, Sequence, PrimaryKeyConstraint
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_id"),
    )
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False, unique=True)
    username = Column(String(64), nullable=False, unique=True)
    password = Column(TEXT, nullable=False)
    login_status = Column(Boolean, nullable=False, default=False)
    have_drone_in_use = Column(Boolean, nullable=False, default=False)



class DrivingSessions(Base):
    __tablename__ = "driving_sessions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    drone_id = Column(Integer, ForeignKey('drone.id'))
    drive_session_started = Column(TIMESTAMP, nullable=False)
    drive_session_ended = Column(TIMESTAMP, nullable=True)
    drive_session_length = Column(Integer, nullable=True)
    session_ended = Column(Boolean, nullable=False, default=False)


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    path_to_images = Column(String(256), nullable=False)
    images_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    # Relationship with images table
    # images = relationship("Images", back_populates="address")


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
    info = Column(TEXT)
    coordinates = Column(String(64))
    session_id = Column(Integer, ForeignKey('driving_sessions.id'))
    # Relationship with driving_sessions table
    # driving_sessions = relationship("DrivingSessions", back_populates="images")


Base.metadata.create_all(engine)
