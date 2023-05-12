import sys
from bs4 import BeautifulSoup
from time import sleep
import os, json, logging, tqdm, requests

from fetchClass import fetchClass
from fetchTeacherId import fetchTeacherId
from fetchRate import fetchRate
from translateRate import translateRate
from fetchDescription import fetchDescription

dirPath = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
  # Setup logger
  logging.basicConfig(filename='example.log', format='%(asctime)s [%(levelname)s] %(message)s', encoding='utf-8')
  
  # 1. Fetch classes
  # fetch all deps first, make a single search less than 500
  units = requests.get("https://qrysub.nccu.edu.tw/assets/api/unit.json")
  units.raise_for_status()
  categories = list()
  for dp1 in [x for x in units.json() if x["utCodL1"] != "0"]:
    for dp2 in [x for x in dp1["utL2"] if x["utCodL2"] != "0"]:
      for dp3 in [x for x in dp2["utL3"] if x["utCodL3"] != "0"]:
        categories.append({"dp1": dp1["utCodL1"], "dp2": dp2["utCodL2"], "dp3": dp3["utCodL3"]})
  
  # run through all deps, get their classId
  coursesList = list()
  tqdmCategories = tqdm.tqdm(categories, leave=False)
  for category in tqdmCategories:
    try:
      tqdmCategories.set_postfix_str("processing: {}".format(category))
      sleep(0.2)
      res = requests.get("https://es.nccu.edu.tw/course/zh-TW/:sem=1112 :dp1={} :dp2={} :dp3={}".format(category["dp1"], category["dp2"], category["dp3"]))
      res.raise_for_status()
      courses = res.json()
      if len(courses) >= 500:
        raise Exception("{} too large".format(category))
      logging.debug([x["subNum"] for x in courses])
      coursesList += [x["subNum"] for x in courses]
    except Exception as e:
      logging.error(e)
      raise(e)
  logging.debug(coursesList)
  
  # Write courseList back to file
  if(os.path.exists(os.path.join(dirPath, "_data"))):
    os.makedirs(os.path.join(dirPath, "_data"), exist_ok=True)
  with open(os.path.join(dirPath, "_data", "classes.json"), "w+") as f:
    f.write(json.dumps(coursesList))
    f.close()
  
  # Read teacher list
  with open(os.path.join(dirPath, "_data", "teachers.json"), "r") as f:
    newTeacherList = json.loads(f.read())
  with open(os.path.join(dirPath, "old_data", "1111_teachers.json"), "r") as f:
    oldTeacherList = json.loads(f.read())
  teacherList = {**newTeacherList,**oldTeacherList}
  
  # Run through all teacherId, and fetch courses of teachers
  teachers = tqdm.tqdm(teacherList, total=len(teacherList), leave=False)
  for teacher in teachers:
    try:
      teacherId = teacherList[teacher]
      teachers.set_postfix_str("processing: {} {}".format(teacherId, teacher))
      location = "http://newdoc.nccu.edu.tw/teaschm/1112/statistic.jsp-tnum={}.htm".format(teacherId)
      res = requests.get(location)
      res.raise_for_status()
      soup = BeautifulSoup(res.content.decode("big5").encode("utf-8"), "html.parser")
      courses = soup.find_all('table')[2].find_all('tr')
      availableCourses = [x.find_all('td') for x in courses if x.find_all('td')[-1].find("a")]
      tqdmCourses = tqdm.tqdm(availableCourses, total=len(availableCourses), leave=False)
      
      for row in tqdmCourses:
        courseId = "{}{}{}".format(row[0].text, row[1].text, row[2].text)
        tqdmCourses.set_postfix_str("processing: {}".format(courseId))
        detail = fetchDescription(courseId)
        rates = fetchRate("http://newdoc.nccu.edu.tw/teaschm/1112/" + row[-1].find("a")["href"])
        logging.debug(detail)
        logging.debug(rates)
          
    except Exception as e:
      logging.error(e)
      continue
  

# translateRate()