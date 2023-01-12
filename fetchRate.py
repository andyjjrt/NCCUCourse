import requests, json, os
from bs4 import BeautifulSoup
from tqdm import tqdm
from constant import URL, COURSE_RATE_URL

teacher_list = dict()
i = 0

def course_rate(param, year_sem, course_id, name, teacher):
    try:
        res = requests.get(COURSE_RATE_URL(param)).content
        soup = BeautifulSoup(res, "html.parser")
        table = soup.find_all('table')[2]
        rows = table.find_all('tr')
        comments = list()
        for row in rows:
            comments.append(row.find('td').text)
        
        # Initialize folder if not exist
        if not os.path.exists("./result/" + teacher):
            os.makedirs("./result/" + teacher)
        if not os.path.exists("./result/" + teacher + "/" + name):
            os.makedirs("./result/" + teacher + "/" + name)
            with open("./result/" + teacher + "/" + name + "/index.json", 'a+') as f:
                json.dump(list(), f)
                
        # Read exist data
        course_index = list()
        with open("./result/" + teacher + "/" + name + "/index.json", 'r') as f:
            course_index = json.loads(f.read())
        
        # Add this index
        course_index.append(dict({"year_sem": year_sem, "course_id": course_id}))
        
        with open("./result/" + teacher + "/" + name + "/index.json", 'w') as f:
            json.dump(course_index, f)
        
        with open("./result/" + teacher + "/" + name + "/" + year_sem + "_" + course_id + ".json", 'a+') as f:
            json.dump(comments, f)
    except:
        print("Course Page not found or Parse error")
        
def main():
    with open("./result/result.json", "r") as f:
        teacher_list = json.load(f)

    if not os.path.exists("./result"):
        os.makedirs("./result")
    row_count = len(teacher_list)
    tqdm_list = tqdm(teacher_list, total=row_count)
    for teacher in tqdm_list:
        teacher_id = teacher_list[teacher]
        tqdm_list.set_postfix_str("processing: " + teacher_id + " " + teacher)
        try:
            res = requests.get(URL(teacher_id)).content.decode("big5").encode("utf-8")
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
                    course_rate(cols[-1].find("a")["href"], year + sem, course_id, name, teacher)
        except:
            print(teacher_id + " " + teacher + "Teacher Page not found or Parse error")