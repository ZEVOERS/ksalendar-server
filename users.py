from fastapi import Request
from db.model import Users

from sqlalchemy.orm import Session


def getUserBySession(req: Request, mariadb: Session):
    return (
        mariadb.query(Users)
        .filter(
            Users.idx == req.cookies.get("useridx"),
            Users.session == req.cookies.get("session_id"),
        )
        .all()
    )
