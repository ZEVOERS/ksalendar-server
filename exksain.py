from threading import Thread
from time import sleep

import requests
from sqlalchemy import desc

from db.connection import SessionLocal, get_db
from db.model import Schedules

from sqlalchemy.orm import Session

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

os.environ["WDM_LOG"] = "0"

options = webdriver.ChromeOptions()
# options.add_argument("headless")
options.add_experimental_option("excludeSwitches", ["enable-logging"])


def db_renewal():
    driver = webdriver.Chrome(options=options)
    login_ksain(driver)
    # data = get_posts_by_selenium(driver)
    #
    # )
    while True:
        # print("adad")
        for i in get_posts_by_selenium(driver, get_ksain_posts()):
            mariadb = SessionLocal()
            print(
                requests.post(
                    "https://api.haru64.com/calendar/parse",
                    headers={"Content-Type": "application/json"},
                    json={
                        "key": "haru-key-ksa-calendar-ydk",
                        "source": i,
                        "targets": [],
                    },
                ).json()
            )
            mariadb.close()
        print()
        sleep(10)


def get_ksain_posts():
    res = requests.post(
        "https://api.ksain.net/v1/document.php",
        data={
            "key": os.getenv("KSAIN_API_KEY"),
            "boardID": 2,
            "count": 10,
        },
    ).json()["data"]
    mariadb = SessionLocal()
    # print(res)
    data = [
        i["documentID"]
        for i in res
        if not mariadb.query(Schedules).filter(Schedules.id == i["documentID"]).all()
    ]
    # print(data)
    mariadb.close()
    return data


def get_posts_by_selenium(driver, data):

    result = []
    for i in data:
        try:
            driver.get(
                f"https://ksain.net/pages/boards/view.php?boardId=2&documentId={i}"
            )
            time.sleep(1)
            buf = []
            for i in driver.find_element(
                By.CSS_SELECTOR, ".desktop-body-div"
            ).find_elements(By.CSS_SELECTOR, "*"):
                if not i.text in buf and not i.text == "":
                    buf.append(i.text)
            result.append(" ".join(buf))
        except:
            result.append("no content")
    # print(result)
    return result


thread = Thread(target=db_renewal, daemon=True)


def login_ksain(driver):
    driver.get("https://ksain.net/pages/cert/login.php")
    time.sleep(3)
    login_input = driver.find_element(By.CSS_SELECTOR, "#login-username-input")
    login_input.click()
    login_input.send_keys("bsiku3622")
    pw_input = driver.find_element(By.CSS_SELECTOR, "#login-password-input")
    pw_input.click()
    pw_input.send_keys("qorwodnjs**3622")
    driver.find_element(By.CSS_SELECTOR, ".cbx").click()
    driver.find_element(By.CSS_SELECTOR, "#login-submit-button").click()
