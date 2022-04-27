from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routers.users import user
from routers.drones import drone

load_dotenv()

app = FastAPI()
app.include_router(user.router)
app.include_router(drone.router)

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


@app.get("/", tags=["ROOT"], summary="Root redirect")
async def docs_redirect():
    # Uudelleen ohjataan käyttäjä docs-sivulle
    return RedirectResponse(url='/docs')
