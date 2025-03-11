import datetime
import os
from fastapi import APIRouter, Depends, Request
import requests
from sqlalchemy.orm import Session
from datetime import date

from db.connection import get_db
from users import getUserBySession
from responses import LOGIN_REQUIRED


def check_valid_session(req: Request, mariadb: Session = Depends(get_db)):
    userdata = getUserBySession(req=req, mariadb=mariadb)
    if not userdata:
        raise LOGIN_REQUIRED
    return userdata[0]


router = APIRouter(
    prefix="/meals", tags=["meals"], dependencies=[Depends(check_valid_session)]
)


@router.get("/")
def srfunc(date: date = datetime.datetime.today().date()):
    return requests.post(
        "https://api.ksain.net/v1/meal.php",
        data={
            "key": os.getenv("KSAIN_API_KEY"),
            "date": date.isoformat(),
        },
    ).json()["data"]
