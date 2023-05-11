from bs4 import BeautifulSoup
import re
import requests

def fetchDescription(courseId: str):
  if len(courseId) != 13:
    raise Exception("Wrong courseId format")
  result = {
    "description": list(),
    "objectives": list()
  }
  
  # construct syllabus location
  year = courseId[0:3]
  sem = courseId[3:4]
  num = courseId[4:10]
  gop = courseId[10:12]
  s = courseId[12:13]
  location = "http://newdoc.nccu.edu.tw/teaschm/{}{}/schmPrv.jsp-yy={}&smt={}&num={}&gop={}&s={}.html".format(year, sem, year, sem, num, gop, s)
  
  # fetching content
  res = requests.get(location)
  soup = BeautifulSoup(res.content, "html.parser")
  
  # get course description
  descriptions = soup.find("div", {"class": "col-sm-7 sylview--mtop col-p-6"}).find_all("p", recursive=False)
  for description in descriptions:
    for line in [x for x in re.split(r'[\n\r]+', description.get_text(strip=True)) if len(x) > 0 and x != " "]:
      result["description"].append(line)    
  
  # get objectives
  objectives = soup.find("div", {"class": "container sylview-section"}).select_one(".col-p-8")
  for objective in objectives:
    for line in [x for x in re.split(r'[\n\r]+', objective.get_text(strip=True)) if len(x) > 0 and x != " "]:
      result["objectives"].append(line)
      
  return result
  
if __name__ == "__main__":
  print(fetchDescription("110225891200"))