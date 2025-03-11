from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    VARCHAR,
    CHAR,
    DATETIME,
    Enum,
    func,
    ForeignKey,
)
from db.connection import Base


class Schedules(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(VARCHAR(60), nullable=False)
    uploaded_at = Column(DATETIME, nullable=False, default=func.now())
    title = Column(VARCHAR(900), nullable=False)
    starts_at = Column(DATETIME, nullable=True, default=func.now())
    ends_at = Column(DATETIME, nullable=True, default=func.now())
    content = Column(VARCHAR(9000), nullable=True)
    ksain_id = Column(Integer, nullable=False)


class UnprocessedSchedules(Base):
    __tablename__ = "unprocessed_schedules"

    ksain_id = Column(Integer, primary_key=True)


class Users(Base):
    __tablename__ = "users"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(VARCHAR(40), nullable=False)
    username = Column(VARCHAR(60), nullable=False)
    password = Column(CHAR(32), nullable=False)
    batch = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    session = Column(CHAR(52), nullable=True)
    expires_in = Column(DATETIME, nullable=True)
