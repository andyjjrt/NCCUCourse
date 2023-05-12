from bs4 import BeautifulSoup
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