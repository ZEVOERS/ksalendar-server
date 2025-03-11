import datetime
from tokenize import String
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import date

from db.connection import get_db
from db.model import Schedules
from users import getUserBySession
from responses import LOGIN_REQUIRED, SCHEDULE_NOT_FOUND, SEARCH_REQUIRED


def check_valid_session(req: Request, mariadb: Session = Depends(get_db)):
    userdata = getUserBySession(req=req, mariadb=mariadb)
    if not userdata:
        raise LOGIN_REQUIRED
    return userdata[0]


router = APIRouter(
    prefix="/schedules", tags=["schedules"], dependencies=[Depends(check_valid_session)]
)


schedules_order_by_ref = {
    "starts_at": 0,
    "ends_at": 1,
    "title": 2,
}

schedules_order_by = [Schedules.starts_at, Schedules.ends_at, Schedules.title]


@router.get("/search/by_starts_at")
def srfunc(
    count: int = 5,
    search: date = datetime.datetime.today().date(),
    mariadb: Session = Depends(get_db),
):
    return (
        mariadb.query(Schedules)
        .filter(
            or_(
                func.date(Schedules.starts_at) == search,
                func.date(Schedules.ends_at) == search,
            )
        )
        .order_by(schedules_order_by[schedules_order_by_ref["starts_at"]])
        .limit(count)
        .all()
    )


@router.get("/{sid}")
def srfunc(sid: int, mariadb: Session = Depends(get_db)):
    schedule_res = mariadb.query(Schedules).filter(Schedules.id == sid).all()
    if not schedule_res:
        raise SCHEDULE_NOT_FOUND
    return schedule_res
