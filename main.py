import sys
from bs4 import BeautifulSoup
from time import sleep
import os, json, logging, tqdm, requests, datetime, getopt
from DB import DB

from User import User
from constant import YEAR_SEM, YEAR, SEM
from fetchDescription import fetchDescription
from fetchRate import fetchRate
from translateRate import translateRate

options = "h"
longOptions = ["help", "skip_class", "skip_teacher", "skip_rate", "skip_class_detail"]
argumentList = sys.argv[1:]
allSemesters = ["1011", "1012","1021", "1022","1031", "1032", "1041", "1042", "1051", "1052", "1061", "1062", "1071", "1072", "1081", "1082", "1091", "1092", "1101", "1102", "1111", "1112"]

programOptions = {
  "skip_class": False,
  "skip_class_detail": False,
  "skip_teacher": False,
  "skip_rate": False
}

dirPath = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":  
  try:
    arguments, values = getopt.getopt(argumentList, options, longOptions)
    for currentArgument, currentValue in arguments:
      if currentArgument in ("-h", "--help"):
        print ("""
  Usage: python main.py [OPTIONS]...

  Options:
    --skip_class          Skip fetch class operation.
    --skip_class_detail   Skip fetch class detail operation.
    --skip_teacher        Skip fetch teacher operation.
    --skip_rate           Skip fetch rate operation.
    --help, -h            Display this help and exit.            
""")
        sys.exit()
      elif currentArgument in ("--skip_class"):
        programOptions["skip_class"] = True
      elif currentArgument in ("--skip_class_detail"):
        programOptions["skip_class_detail"] = True
      elif currentArgument in ("--skip_teacher"):
        programOptions["skip_teacher"] = True
      elif currentArgument in ("--skip_rate"):
        programOptions["skip_rate"] = True
  except getopt.error as err:
    print (str(err))
    sys.exit()
  

  # Setup logger
  logging.basicConfig(filename='log.log', format='%(asctime)s [%(levelname)s] %(message)s', encoding='utf-8')
  
  if(os.path.exists(os.path.join(dirPath, "_data"))):
    os.makedirs(os.path.join(dirPath, "_data"), exist_ok=True)
    
  db = DB("test.db")
  
  # ==============================
  # \ 1. Fetch Classes           \
  # ==============================
  
  if not programOptions["skip_class"]:
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
      tqdmCategories.set_postfix_str("{}".format(category))
      if not programOptions["skip_class_detail"]:
        semesters = tqdm.tqdm(allSemesters, leave=False)
      else:
        semesters = ["1112"]
      for semester in semesters:
        if not programOptions["skip_class_detail"]:
          semesters.set_postfix_str("processing: {}".format(semester))
        try:
          sleep(0.1)
          res = requests.get("https://es.nccu.edu.tw/course/zh-TW/:sem={} :dp1={} :dp2={} :dp3={}".format(semester, category["dp1"], category["dp2"], category["dp3"]))
          res.raise_for_status()
          courses = res.json()
          if len(courses) >= 500:
            raise Exception("{} too large".format(category))
          
          # Add to courseList
          if(semester == YEAR_SEM):
            coursesList += [x["subNum"] for x in courses]
          
          # Write to databse
          if not programOptions["skip_class_detail"]:
            for course in tqdm.tqdm(courses, leave=False):
              courseId = "{}{}".format(semester, course["subNum"])
              if db.isCourseExist(courseId, category):
                continue
              detail = fetchDescription(courseId)
              db.addCourse(detail["qrysub"], detail["qrysubEn"], category["dp1"], category["dp2"], category["dp3"], "".join(detail["description"]), "".join(detail["objectives"]))
        except Exception as e:
          logging.error(e)

    logging.debug(coursesList)
    
    print("Fetch Class done at {}".format(datetime.datetime.now()))
  else:
    print("Skipping Fetch Class")
    
  # ==============================
  # \ 2. Fetch TeacherId         \
  # ==============================
  
  if not programOptions["skip_teacher"]:
    # Read course list
    coursesList = db.getThisSemesterCourse(YEAR, SEM)
    
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
    tqdmCourses = tqdm.tqdm([*set(coursesList)], leave=False)
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
        if teacherStatUrl.startswith("https://newdoc.nccu.edu.tw/teaschm/{}/statisticAll.jsp".format(YEAR_SEM)):
          teacherId = teacherStatUrl.split("https://newdoc.nccu.edu.tw/teaschm/{}/statisticAll.jsp-tnum=".format(YEAR_SEM))[1].split(".htm")[0]
          teacherIdDict[teacherName] = teacherId
          db.addTeacher(teacherId, teacherName)
        elif teacherStatUrl.startswith("https://newdoc.nccu.edu.tw/teaschm/{}/set20.jsp".format(YEAR_SEM)):
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
            db.addTeacher(teacherId, teacherName)
      except Exception as e:
        logging.error(e)
        continue
    
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
  else:
    print("Skipping Fetch TeacherId")
  
  # ==============================
  # \ 3. Fetch Rates and Details \
  # ==============================
  
  if not programOptions["skip_rate"]:
    # Read teacher list
    newTeacherList = db.getTeachers()
    with open(os.path.join(dirPath, "old_data", "1111_teachers.json"), "r") as f:
      oldTeacherList = json.loads(f.read())
    teacherList = {**newTeacherList,**oldTeacherList}
    
    # Run through all teacherId, and fetch courses of teachers
    teachers = tqdm.tqdm(teacherList, total=len(teacherList), leave=False)
    for teacher in teachers:
      teacherId = teacherList[teacher]
      teachers.set_postfix_str("processing: {} {}".format(teacherId, teacher))
      semesters = tqdm.tqdm(allSemesters, total=len(allSemesters), leave=False)
      for semester in semesters:
        semesters.set_postfix_str("processing: {}".format(semester))
        try:
          location = "http://newdoc.nccu.edu.tw/teaschm/{}/statistic.jsp-tnum={}.htm".format(semester, teacherId)
          res = requests.get(location)
          res.raise_for_status()
          soup = BeautifulSoup(res.content.decode("big5").encode("utf-8"), "html.parser")
          courses = soup.find('table', {"border": "1"}).find_all('tr')
          availableCourses = [x.find_all('td') for x in courses if x.find_all('td')[-1].find("a") and int(x.find_all('td')[0].text) > 100]
          tqdmCourses = tqdm.tqdm(availableCourses, total=len(availableCourses), leave=False)
          
          for row in tqdmCourses:
            courseId = "{}{}{}".format(row[0].text, row[1].text, row[2].text)
            tqdmCourses.set_postfix_str("processing: {}".format(courseId))
            if db.isRateExist(courseId):
              continue
            rates = fetchRate("http://newdoc.nccu.edu.tw/teaschm/{}/{}".format(semester, row[-1].find("a")["href"]))
            
            # Write to database
            for index, rate in enumerate(rates):
              db.addRate(index, courseId, teacherId, str(rate))

            # # Create folder if not exist
            # path = os.path.join(dirPath, "result", teacher, detail["qrysub"]["subNam"])
            # if not os.path.exists(path):
            #   os.makedirs(path, exist_ok=True)
                        
            # # Write detail back to file
            # with open(os.path.join(path, "{}.json".format(courseId)), "w+") as f:
            #   f.write(json.dumps({"comments": rates}))
            #   f.close()
              
        except Exception as e:
          logging.error(e)
          continue
    
    print("Fetch Rates and Details done at {}".format(datetime.datetime.now()))
  else:
    print("Skipping Fetch Rate")
  
# translateRate()