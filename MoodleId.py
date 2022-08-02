import requests
from bs4 import BeautifulSoup
import csv, json
from tqdm import tqdm, trange

from constant import YEAR_SEM, COURSELIST_CSV

def main():
    course_data = {}
    i = 0

    row_count = sum(1 for line in open('data/' + COURSELIST_CSV, 'r'))

    with open('data/' + COURSELIST_CSV, 'r') as file:
        reader = tqdm(csv.reader(file), total=row_count)
        for row in reader:
            #if i > 100: break
            courseid = str(row[0])
            reader.set_postfix_str("processing: " + courseid)
            course_data[courseid] = {}
            try:
                res = requests.get("https://moodle.nccu.edu.tw/course/search.php?search=" + YEAR_SEM + "_" + str(courseid))
                soup = BeautifulSoup(res.content, "html.parser")
                moodle_url = soup.find("h3", {"class": "coursename"}).find("a")["href"]
                course_data[courseid]["moodle_id"] = moodle_url.split("https://moodle.nccu.edu.tw/course/view.php?id=")[1]
            except:
                course_data[courseid]["moodle_id"] = ""
                print(courseid + " error")
                
            try:
                res = requests.get("https://es.nccu.edu.tw/course/zh-TW/:sem=" + YEAR_SEM + "%20" + str(courseid) + "%20/").json()
                if res[0]["lmtKind"] != "":
                    course_data[courseid]["subject_kind"] = ""
                    if res[0]["core"] == "是":
                        course_data[courseid]["subject_kind"] = "核心"
                    course_data[courseid]["subject_kind"] += res[0]["lmtKind"]
                elif res[0]["subKind"] != "":
                    course_data[courseid]["subject_kind"] = res[0]["subKind"]
            except:
                course_data[courseid]["subject_kind"] = ""
                print(courseid + " error")
            i += 1
        reader.set_postfix_str("done")

    with open('result/course.json', 'w', encoding="utf-8") as fp:
        json.dump(course_data, fp)

if __name__ == "__main__":
    main()