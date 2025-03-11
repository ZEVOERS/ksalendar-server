from datetime import datetime
import json
import typing
from fastapi import Response
from sqlalchemy.orm.attributes import InstrumentedAttribute
from starlette.background import BackgroundTask

from fastapi import HTTPException, Response

LOGIN_REQUIRED = HTTPException(status_code=401, detail="Login required")
USER_NOT_FOUND = HTTPException(status_code=404, detail="User not found")
SCHEDULE_NOT_FOUND = HTTPException(status_code=404, detail="Schedule not found")
USER_NOT_FOUND_IN_DB = HTTPException(status_code=402, detail="User not found in db")
INVALID_SESSION = HTTPException(status_code=401, detail="Invalid session")
DB_NOT_FOUND = HTTPException(status_code=404, detail="DB not found")
THREAD_NOT_FOUND = HTTPException(status_code=404, detail="Thread not found")
SEARCH_REQUIRED = HTTPException(status_code=400, detail="Search required")


def convertJsonFromSql(obj):
    data = {}
    for key, value in type(obj).__dict__.items():
        if isinstance(value, InstrumentedAttribute):
            value = object.__getattribute__(obj, key)
            if isinstance(value, datetime):
                value = str(value)
            data[key] = value
    return data


class DBResponse(Response):
    media_type = "application/json"

    def __init__(
        self,
        content: typing.Any,
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: typing.Any) -> bytes:
        data = convertJsonFromSql(content)
        return json.dumps(
            data,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
