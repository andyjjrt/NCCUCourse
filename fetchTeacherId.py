import requests, json, os, logging
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import time, sleep

from util import get_login_url, get_addtrack_url, get_deltrack_url, get_track_url
from constant import USERNAME, PASSWORD, YEAR_SEM

dir_path = os.path.dirname(os.path.realpath(__file__))

timeHold = 0.2

def fetchTeacherId(courseList):
  res = requests.get(get_login_url(USERNAME, PASSWORD)).json()
  encstu = res[0]["encstu"]
  data = {}
  i = 0
  reader = tqdm(courseList, leave=False)
  st = time()
  for courseId in reader:
    try:
      while time() - st < timeHold:
        sleep(0.01)
      st = time()
      # Add to trace
      requests.post(get_addtrack_url(encstu, courseId))
      while time() - st < timeHold:
        sleep(0.01)
      st = time()
      # Get all trace
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
      while time() - st < timeHold:
        sleep(0.01)
      st = time()
      # Delete from trace
      requests.delete(get_deltrack_url(encstu, courseId))
    except Exception as e:
      logging.exception("Error occurred while parsing course: " + courseId)
    i += 1
    
  with open(os.path.join(dir_path, "_data", "classes.json"), "w+", encoding="utf-8") as f:
    json.dump(data, f)
  
  return data
