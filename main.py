from bs4 import BeautifulSoup
import os, json, logging, tqdm, requests

from fetchClass import fetchClass
from fetchTeacherId import fetchTeacherId
from fetchRate import fetchRate
from translateRate import translateRate
from fetchDescription import fetchDescription

dir_path = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
  
  logging.basicConfig(filename='example.log', format='%(asctime)s [%(levelname)s] %(message)s', encoding='utf-8')
  
  with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "_data", "teachers.json"), "r") as f:
    newTeacherList = json.loads(f.read())
  with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "old_data", "1111_teachers.json"), "r") as f:
    oldTeacherList = json.loads(f.read())
  
  teacherList = {**newTeacherList,**oldTeacherList}
  
  teachers = tqdm.tqdm(teacherList, total=len(teacherList), leave=False)
  for teacher in teachers:
    try:
      teacherId = teacherList[teacher]
      teachers.set_postfix_str("processing: {} {}".format(teacherId, teacher))
      location = "http://newdoc.nccu.edu.tw/teaschm/1082/statistic.jsp-tnum={}.htm".format(teacherId)
      res = requests.get(location)
      res.raise_for_status()
      soup = BeautifulSoup(res.content.decode("big5").encode("utf-8"), "html.parser")
      courses = soup.find_all('table')[2].find_all('tr')
      tqdmCourses = tqdm.tqdm(courses, total=len(courses), leave=False)
      
      for row in tqdmCourses:
        cols = row.find_all('td')
        courseId = "{}{}{}".format(cols[0].text, cols[1].text, cols[2].text)
        tqdmCourses.set_postfix_str("processing: {}".format(courseId))
        if cols[-1].find("a"):
          detail = fetchDescription(courseId)
          rates = fetchRate("http://newdoc.nccu.edu.tw/teaschm/1082/" + cols[-1].find("a")["href"])
          logging.debug(detail)
          logging.debug(rates)
    except Exception as e:
      logging.error(e)
      continue
  

# translateRate()