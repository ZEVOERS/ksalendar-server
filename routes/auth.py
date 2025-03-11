import os
from fastapi import APIRouter, Depends, Request, Response, HTTPException
import requests
from db.connection import get_db
from db.model import *
from pydantic import BaseModel

from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import hashlib

from responses import LOGIN_REQUIRED, DBResponse
from users import getUserBySession


class AccountJoin(BaseModel):
    userid: str
    password: str


router = APIRouter(prefix="/auth", tags=["auths"])


@router.post("/signup")
def srfunc(data: AccountJoin, mariadb: Session = Depends(get_db)):
    ksain_res = requests.post(
        "https://api.ksain.net/v1/login.php",
        data={
            "key": os.getenv("KSAIN_API_KEY"),
            "username": data.userid,
            "password": data.password,
        },
    )
    if not ksain_res.status_code == 200:
        raise HTTPException(status_code=401, detail="Failed to login")
    d = ksain_res.json()["data"]
    mariadb.add(
        Users(
            userid=data.userid,
            username=d["name"],
            password=hashlib.md5(data.password.encode()).hexdigest(),
            batch=d["batch"],
            student_id=d["studentID"],
        )
    )
    mariadb.commit()
    return Response(status_code=201)


class AccountLogin(BaseModel):
    userid: str
    password: str


def generage_session_id():
    return str(uuid4()) + str(int(datetime.timestamp(datetime.now()) * 1000000))


@router.post("/login")
def srfunc(data: AccountLogin, mariadb: Session = Depends(get_db)):
    if len(data.password) != 32:
        return HTTPException(status_code=400, detail="Unallowed password length.")
    user = mariadb.query(Users).filter(
        Users.userid == data.userid, Users.password == data.password
    )
    if user.all():
        userd = user.all()[0]
        if userd.session:
            session_id = userd.session
        else:
            session_id = generage_session_id()
            user.update({Users.session: session_id})
            mariadb.commit()
        mariadb.commit()
        res = Response(status_code=200)
        res.set_cookie(
            key="useridx",
            value=userd.idx,
            samesite="none",
            secure=True,
            httponly=True,
            max_age=99999999,
            path="/",
        )
        res.set_cookie(
            key="session_id",
            value=session_id,
            samesite="none",
            secure=True,
            httponly=True,
            max_age=99999999,
            path="/",
        )
        return res
    raise HTTPException(status_code=401, detail="Login failed")


@router.get("/session_info")
def srfunc(req: Request, mariadb: Session = Depends(get_db)):
    d = getUserBySession(req=req, mariadb=mariadb)
    if d:
        return d
    return LOGIN_REQUIRED


@router.get("/logout")
def srfunc():
    res = Response(status_code=204)
    res.delete_cookie("useridx")
    res.delete_cookie("session_id")
    return res
