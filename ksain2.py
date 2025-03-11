import datetime
from itertools import count
import json
import requests
from bs4 import BeautifulSoup

from threading import Thread
from time import sleep

import requests

from db.connection import SessionLocal
from db.model import Schedules, UnprocessedSchedules

import os


haru_url = "https://api.haru64.com/calendar/parse"

haru_headers = {"Content-Type": "application/json"}


def getDocument(board: int, doc: int):
    data = requests.get(
        f"https://ksain.net/web/boards/view_d.php?boardId={board}&docId={doc}"
    )
    # HTML 파싱
    soup = BeautifulSoup(data.content, "html.parser")

    # body-desktop 요소 찾기
    body_desktop = soup.find(id="body-desktop")

    # 두 번째 자식 요소 출력
    if body_desktop:
        second_child = body_desktop.find_all(recursive=False)[
            1
        ]  # 두 번째 직접 자식 선택
        # 두 번째 자식 내의 p 태그들 찾기
        p_tags = second_child.find_all("p")

        # p 태그들의 내용 출력
        text = "\n".join([p.get_text(strip=True) for p in p_tags])

        data = {
            "source": text,
            "targets": [],
            "key": "haru-key-ksa-calendar-ydk",
            "lang": "korean",
        }

        response = requests.post(haru_url, json=data, headers=haru_headers)

        # soup.find("document-top-writer-board").get_text(strip=True)
        return json.loads(response.content)
    else:
        return "no content"


def get_ksain_posts(count: int):
    res = requests.post(
        "https://api.ksain.net/v1/document.php",
        data={
            "key": os.getenv("KSAIN_API_KEY"),
            "boardID": 2,
            "count": count,
        },
    ).json()["data"]
    mariadb = SessionLocal()
    # print(res)
    data = [
        i
        for i in res
        if not mariadb.query(Schedules)
        .filter(Schedules.ksain_id == i["documentID"])
        .all()
    ]
    # print(data)
    mariadb.close()
    return data


def db_renewal(count):
    # data = get_posts_by_selenium(driver)
    #
    # )
    while True:
        # print("adad")
        for i in get_ksain_posts(count):
            print(i)
            try:
                d = getDocument(2, i["documentID"])
                # print(d)
                if d != "no content":

                    mariadb = SessionLocal()
                    # mariadb.add(
                    #     Schedules(
                    #         author=i["name"],
                    #         title=d["title"],
                    #         content=d["description"],
                    #         uploaded_at=datetime.datetime.strptime(
                    #             i["regDate"], "%Y-%m-%d %H:%M:%S"
                    #         ),
                    #         starts_at=(
                    #             datetime.datetime.strptime(
                    #                 d["starts_at"], "%Y-%m-%d %H:%M:%S"
                    #             )
                    #             if d["starts_at"]
                    #             else None
                    #         ),
                    #         ends_at=(
                    #             datetime.datetime.strptime(
                    #                 d["ends_at"], "%Y-%m-%d %H:%M:%S"
                    #             )
                    #             if d["ends_at"]
                    #             else None
                    #         ),
                    #         ksain_id=i["documentID"],
                    #     )
                    # )
                    mariadb.add(
                        Schedules(
                            author=i["name"],
                            title=d["title"],
                            content=d["description"],
                            uploaded_at=datetime.datetime.strptime(
                                i["regDate"], "%Y-%m-%d %H:%M:%S"
                            ),
                            starts_at=(
                                datetime.datetime.fromtimestamp(d["starts_at"])
                                if d["starts_at"]
                                else None
                            ),
                            ends_at=(
                                datetime.datetime.fromtimestamp(d["ends_at"])
                                if d["ends_at"]
                                else None
                            ),
                            ksain_id=i["documentID"],
                        )
                    )
                    mariadb.commit()
                    mariadb.close()
                    print("processed:", i["documentID"])
            except:
                mariadb = SessionLocal()
                mariadb.add(UnprocessedSchedules(ksain_id=i["documentID"]))
                mariadb.commit()
                mariadb.close()
                print("error:", i["documentID"])
        sleep(60)


thread = Thread(target=db_renewal, daemon=True)

if __name__ == "__main__":
    count = input("Count: ")
    print("hello")
    db_renewal(count)
else:
    pass

# mariadb = SessionLocal()

# d = getDocument(2, 1468)
# print(d)
# x = Schedules(
#     author=d["author"],
#     title=d["title"],
#     content=d["description"],
#     uploaded_at=datetime.datetime.strptime(d["uploaded_at"], "%Y-%m-%d %H:%M:%S"),
#     starts_at=(
#         datetime.datetime.strptime(d["starts_at"], "%Y-%m-%d %H:%M:%S")
#         if d["starts_at"]
#         else None
#     ),
#     ends_at=(
#         datetime.datetime.strptime(d["ends_at"], "%Y-%m-%d %H:%M:%S")
#         if d["ends_at"]
#         else None
#     ),
# )
# mariadb.add(x)
# mariadb.commit()
# print(x)
# mariadb.close()
