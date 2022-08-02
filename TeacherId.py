import requests, csv, json
from bs4 import BeautifulSoup
from tqdm import tqdm, trange

from util import get_login_url, get_addtrack_url, get_deltrack_url, get_track_url
from constant import USERNAME, PASSWORD, YEAR_SEM, COURSELIST_CSV

def main():
    row_count = sum(1 for line in open('data/' + COURSELIST_CSV, 'r'))

    with open('data/' + COURSELIST_CSV, 'r') as file:
        res = requests.get(get_login_url(USERNAME, PASSWORD)).json()
        encstu = res[0]["encstu"]
        data = {}
        i = 0
        reader = tqdm(csv.reader(file), total=row_count)
        for row in reader:
            #if i > 100: break
            courseid = str(row[0])
            reader.set_postfix_str("processing: " + courseid)
            try:
                res = requests.post(get_addtrack_url(encstu, courseid)).text
                res = requests.get(get_track_url(encstu)).json()
                if str(res[0]["teaStatUrl"]).startswith('https://newdoc.nccu.edu.tw/teaschm/' + YEAR_SEM + '/statisticAll.jsp'):
                    teacher_name = str(res[0]["teaNam"])
                    teacher_id = str(res[0]["teaStatUrl"]).split("https://newdoc.nccu.edu.tw/teaschm/" + YEAR_SEM + "/statisticAll.jsp-tnum=")[1].split(".htm")[0]
                    data[teacher_name] = teacher_id
                elif str(res[0]["teaStatUrl"]).startswith('https://newdoc.nccu.edu.tw/teaschm/' + YEAR_SEM + '/set20.jsp'):
                    res = requests.get(str(res[0]["teaStatUrl"]).replace("https://", "http://")).content.decode("big5").encode("utf-8")
                    soup = BeautifulSoup(res, "html.parser")
                    rows = soup.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if cols[1].find("a"):
                            teacher_name = str(cols[0].text)
                            teacher_id = str(cols[1].find("a")["href"].split("statisticAll.jsp-tnum=")[1].split(".htm")[0])
                            data[teacher_name] = teacher_id
                res = requests.delete(get_deltrack_url(encstu, courseid)).text
                # print(res)
            except:
                print(courseid + " error")
                res = requests.delete(get_deltrack_url(encstu, courseid)).text
            i += 1
        reader.set_postfix_str("done")
    
    with open('result/result.json', 'w', encoding="utf-8") as fp:
        json.dump(data, fp)

if __name__ == "__main__":
    main()
