import sys
from bs4 import BeautifulSoup
from time import sleep
import os, json, logging, tqdm, requests, datetime

from User import User
from fetchDescription import fetchDescription
from fetchRate import fetchRate
from translateRate import translateRate


dirPath = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
  # Setup logger
  logging.basicConfig(filename='example.log', format='%(asctime)s [%(levelname)s] %(message)s', encoding='utf-8')
  
  if(os.path.exists(os.path.join(dirPath, "_data"))):
    os.makedirs(os.path.join(dirPath, "_data"), exist_ok=True)
  
  # ==============================
  # \ 1. Fetch Classes           \
  # ==============================
  
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
      sleep(0.1)
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
  with open(os.path.join(dirPath, "_data", "classes.json"), "w+") as f:
    f.write(json.dumps(coursesList))
    f.close()
  
  print("Fetch Class done at {}".format(datetime.datetime.now()))
    
  # ==============================
  # \ 2. Fetch TeacherId         \
  # ==============================
  
  # Read course list
  with open(os.path.join(dirPath, "_data", "classes.json"), "r") as f:
    coursesList = json.loads(f.read())
  
  user = User()
 
  # Delete exist track courses before adding
  courses = user.getTrack()
  if len(courses) > 0:
    tqdmCourses =  tqdm.tqdm(courses, leave=False)
    for course in tqdmCourses:
      try:
        sleep(0.2)
        courseId = str(course["subNum"])
        tqdmCourses.set_postfix_str("Pre-deleting {}".format(courseId))
        user.deleteTrack(courseId)
      except Exception as e:
        logging.error(e)
        continue
  
  # Add courses to track list
  tqdmCourses = tqdm.tqdm(coursesList, leave=False)
  for courseId in tqdmCourses:
    try:
      sleep(0.2)
      tqdmCourses.set_postfix_str("Adding {}".format(courseId))
      user.addTrack(courseId)
    except Exception as e:
      logging.error(e)
      continue
  
  # get track list and parse out teacher id
  courses = user.getTrack()
  teacherIdDict = dict()
  tqdmCourses = tqdm.tqdm(courses, leave=False)
  for course in tqdmCourses:
    try:
      teacherStatUrl = str(course["teaStatUrl"])
      teacherName = str(course["teaNam"])
      tqdmCourses.set_postfix_str("Processing {}".format(teacherName))
      if teacherStatUrl.startswith("https://newdoc.nccu.edu.tw/teaschm/1112/statisticAll.jsp"):
        teacherId = teacherStatUrl.split("https://newdoc.nccu.edu.tw/teaschm/1112/statisticAll.jsp-tnum=")[1].split(".htm")[0]
        teacherIdDict[teacherName] = teacherId
      elif teacherStatUrl.startswith("https://newdoc.nccu.edu.tw/teaschm/1112/set20.jsp"):
        # use ip to avoid name resolve error, and add time out
        res = requests.get(teacherStatUrl.replace("newdoc.nccu.edu.tw", "140.119.229.20").replace("https://", "http://"), timeout=10)
        res.raise_for_status()
        sleep(0.2)
        soup = BeautifulSoup(res.content.decode("big5").encode("utf-8"), "html.parser")
        rows = soup.find_all("tr")
        for row in [x.find_all("td") for x in soup.find_all("tr") if x.find_all("td")[1].find("a")]:
          teacherName = str(row[0].text)
          teacherId = row[-1].find("a")["href"].split("statisticAll.jsp-tnum=")[1].split(".htm")[0]
          teacherIdDict[teacherName] = teacherId
    except Exception as e:
      logging.error(e)
      continue
      
  # Write teacherIdDict back to file
  with open(os.path.join(dirPath, "_data", "teachers.json"), "w+") as f:
    f.write(json.dumps(teacherIdDict))
    f.close()
  
  # Delete courses from track list
  tqdmCourses =  tqdm.tqdm(courses, leave=False)
  for course in tqdmCourses:
    try:
      sleep(0.2)
      courseId = str(course["subNum"])
      tqdmCourses.set_postfix_str("Deleting {}".format(courseId))
      user.deleteTrack(courseId)
    except Exception as e:
      logging.error(e)
      continue
  
  print("Fetch TeacherId done at {}".format(datetime.datetime.now()))
  
  # ==============================
  # \ 3. Fetch Rates and Details \
  # ==============================
  
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
  
  print("Fetch Rates and Details done at {}".format(datetime.datetime.now()))
  
# translateRate()