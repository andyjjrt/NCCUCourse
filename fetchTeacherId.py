import requests, json, os, logging
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import time, sleep

from util import get_login_url, get_addtrack_url, get_deltrack_url, get_track_url
from constant import USERNAME, PASSWORD, YEAR_SEM

dir_path = os.path.dirname(os.path.realpath(__file__))

timeHold = 0.2


def fetchTeacherId(courseList):
    print("Fetching teacher id, USERNAME=" + USERNAME + " YEAR_SEM=" + YEAR_SEM)
    res = requests.get(get_login_url(USERNAME, PASSWORD)).json()
    encstu = res[0]["encstu"]
    data = {}
    i = 0

    st = time()
    encstu = res[0]["encstu"]

    courseres = requests.get(get_track_url(encstu)).json()
    if courseres:
        print("not NULL")
        reset = tqdm(courseres, leave=False)
        for course in reset:
            while time() - st < timeHold:
                sleep(0.01)
            st = time()
            courseId = str(course["subNum"])
            reset.set_description("Deleting %s" % courseId)
            deleteres = requests.delete(get_deltrack_url(encstu, courseId)).json()
            if deleteres[0]["procid"] != "9":
                print("Delete fail: " + courseId)

    courses = tqdm(courseList, leave=False)
    for courseId in courses:
        while time() - st < timeHold:
            sleep(0.01)
        st = time()
        try:
            courses.set_description("Adding %s" % courseId)
            addres = requests.post(get_addtrack_url(encstu, courseId)).json()
            if addres[0]["procid"] != "1":
                raise ("Add fail: " + courseId)
        except Exception as e:
            with open(os.path.join(dir_path, "_data", "log.txt"), "a") as f:
                f.write(str(e) + "\n")
                f.close()

    courseres = requests.get(get_track_url(encstu)).json()
    reader = tqdm(courseres, leave=False)
    for course in reader:
        try:
            if str(course["teaStatUrl"]).startswith(
                "https://newdoc.nccu.edu.tw/teaschm/" + YEAR_SEM + "/statisticAll.jsp"
            ):
                teacher_name = str(course["teaNam"])
                teacher_id = (
                    str(course["teaStatUrl"])
                    .split(
                        "https://newdoc.nccu.edu.tw/teaschm/"
                        + YEAR_SEM
                        + "/statisticAll.jsp-tnum="
                    )[1]
                    .split(".htm")[0]
                )
                data[teacher_name] = teacher_id
            elif str(course["teaStatUrl"]).startswith(
                "https://newdoc.nccu.edu.tw/teaschm/" + YEAR_SEM + "/set20.jsp"
            ):
                res = (
                    requests.get(
                        str(course["teaStatUrl"]).replace("https://", "http://")
                    )
                    .content.decode("big5")
                    .encode("utf-8")
                )
                soup = BeautifulSoup(res, "html.parser")
                rows = soup.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if cols[1].find("a"):
                        teacher_name = str(cols[0].text)
                        teacher_id = str(
                            cols[1]
                            .find("a")["href"]
                            .split("statisticAll.jsp-tnum=")[1]
                            .split(".htm")[0]
                        )
                        data[teacher_name] = teacher_id
        except Exception as e:
            with open(os.path.join(dir_path, "_data", "log.txt"), "a") as f:
                f.write(str(e) + "\n")
                f.close()

    with open(
        os.path.join(dir_path, "_data", "teachers.json"), "w+", encoding="utf-8"
    ) as f:
        json.dump(data, f)
        f.close()

    delcourses = tqdm(courseres, leave=False)
    for course in delcourses:
        while time() - st < timeHold:
            sleep(0.01)
        st = time()
        courseId = str(course["subNum"])
        delcourses.set_description("Deleting %s" % courseId)
        deleteres = requests.delete(get_deltrack_url(encstu, courseId)).json()
        if deleteres[0]["procid"] != "9":
            print("Delete fail: " + courseId)

    print("Fetching teacher id done at " + str(time()))

    return data
