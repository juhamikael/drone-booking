from pydantic import BaseModel, Field
from typing import Dict

drone_default = {"Max Flight Distance": "30km",
                 "Max Flight Time": "46 minutes",
                 "Max Wind Speed Resistance": "12m/s",
                 }


class UserIn(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=20)
    username: str = Field(min_length=3, max_length=20)
    email: str = Field(max_length=100, default="email@email.com")
    password: str = Field(min_length=8, max_length=20, default="Password123")

    class Config:
        orm_mode = True


class DroneIn(BaseModel):
    id: int
    brand: str = Field(min_length=2, max_length=20, default="DJI")
    model: str = Field(min_length=2, max_length=20, default="Mavic 3")
    additional_info: Dict = Field(default=drone_default)

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    name: str
    username: str
    email: str

    class Config:
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str = Field(default="Password123")

    class Config:
        orm_mode = True


class StartDriving(BaseModel):
    user_id: int
    drone_id: int
    city: str

    class Config:
        orm_mode = True


class StopDriving(BaseModel):
    session_id: int

    class Config:
        orm_mode = True
