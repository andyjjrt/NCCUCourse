import requests, json, os, logging
from time import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from constant import URL, COURSE_RATE_URL, RATE_QRY
from fetchDescription import fetchDescription

dir_path = os.path.dirname(os.path.realpath(__file__))
i = 0

def course_rate(param, year_sem, rate_year_sem, course_id, name, teacher):
    try:
        res = requests.get(COURSE_RATE_URL(param, rate_year_sem)).content
        soup = BeautifulSoup(res, "html.parser")
        table = soup.find_all('table')[2]
        rows = table.find_all('tr')
        comments = list()
        for row in rows:
            comments.append(row.find('td').text)
            
        detail = fetchDescription(year_sem + course_id)
        
        # Initialize folder if not exist
        if not os.path.exists(os.path.join(dir_path, "result", teacher)):
            os.makedirs(os.path.join(dir_path, "result", teacher))
        if not os.path.exists(os.path.join(dir_path, "result", teacher, name)):
            os.makedirs(os.path.join(dir_path, "result", teacher, name))
            with open(os.path.join(dir_path, "result", teacher, name, "index.json"), 'w+') as f:
                json.dump(list(), f)
                f.close()
                
        # Read exist data
        course_index = list()
        with open(os.path.join(dir_path, "result", teacher, name, "index.json"), 'r') as f:
            course_index = json.loads(f.read())
        
        # Add this index
        course_index.append(dict({"year_sem": year_sem, "course_id": course_id}))
        
        with open(os.path.join(dir_path, "result", teacher, name, "index.json"), 'w+') as f:
            json.dump(course_index, f)
            f.close()
        
        with open(os.path.join(dir_path, "result", teacher, name, year_sem + course_id + ".json"), 'w+') as f:
            f.write(json.dumps({"comments": comments, "detail": detail}))
            f.close()
    except Exception as e:
        with open(os.path.join(dir_path, "_data", "log.txt"), "a") as f:
            f.write(str(e) + "\n")
            f.close()
        
def fetchRate(teacher_list):
    print("Fetching result")
    if not os.path.exists(os.path.join(dir_path, "result")):
        os.makedirs(os.path.join(dir_path, "result"))
    with open(os.path.join(dir_path, "old_data", "1111_teachers.json"), "r") as f:
        old_teacher_list = json.loads(f.read())
    total_teacher_list = {**old_teacher_list,**teacher_list}
    row_count = len(total_teacher_list)
    tqdm_list = tqdm(total_teacher_list, total=row_count, leave=False)
    for teacher in tqdm_list:
        teacher_id = total_teacher_list[teacher]
        tqdm_list.set_postfix_str("processing: " + teacher_id + " " + teacher)
        for qry_year_sem in RATE_QRY():
            try:
                res = requests.get(URL(teacher_id, qry_year_sem)).content.decode("big5").encode("utf-8")
                soup = BeautifulSoup(res, "html.parser")
                table = soup.find_all('table')[2]
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if cols[-1].find("a"):
                        year = cols[0].text
                        sem = cols[1].text
                        course_id = cols[2].text
                        name = cols[3].text
                        #print(COURSE_RATE_URL(cols[-1].find("a")["href"]))
                        course_rate(cols[-1].find("a")["href"], year + sem, qry_year_sem, course_id, name, teacher)
            except Exception as e:
                with open(os.path.join(dir_path, "_data", "log.txt"), "a") as f:
                    f.write(str(e) + "\n")
                    f.close()
    print("Fetching class done at " + str(time()))