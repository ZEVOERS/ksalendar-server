from fastapi import FastAPI
import ksain2

# from routes import meals, schedules
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, meals, schedules


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://ksalendar_api.zevoers.dev",
    "https://ksalendar.zevoers.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def srfunc():
    return "Developed by _baek.jw"


app.include_router(schedules.router)
app.include_router(auth.router)
app.include_router(meals.router)
