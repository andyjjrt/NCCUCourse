from bs4 import BeautifulSoup
import re, requests, logging

def fetchDescription(courseId: str):
  if len(courseId) != 13:
    raise Exception("Wrong courseId format")
  result = {
    "description": list(),
    "objectives": list(),
    "qrysub": dict(),
  }
  
  try:
    # get qrysub detail
    qrysub = requests.get("http://es.nccu.edu.tw/course/zh-TW/{} /".format(courseId)).json()
    if len(qrysub) != 1:
      raise Exception("No matched course")
    result["qrysub"] = qrysub[0]
    location = str(result["qrysub"]["teaSchmUrl"]).replace("https://", "http://")
    
    # fetching content
    res = requests.get(location)
    soup = BeautifulSoup(res.content, "html.parser")
    
    # get syllabus description
    descriptions = soup.find("div", {"class": "col-sm-7 sylview--mtop col-p-6"}).find_all("p", recursive=False) + soup.find("div", {"class": "col-sm-7 sylview--mtop col-p-6"}).find_all("table")
    for description in descriptions:
      for line in [x for x in re.split(r'[\n\r]+', description.get_text(strip=True)) if len(x) > 0 and x != " "]:
        result["description"].append(line)    
    
    # get syllabus objectives
    objectives = soup.find("div", {"class": "container sylview-section"}).select_one(".col-p-8")
    for objective in objectives:
      for line in [x for x in re.split(r'[\n\r]+', objective.get_text(strip=True)) if len(x) > 0 and x != " "]:
        result["objectives"].append(line)
    
  except Exception as e:
    logging.error(e)
  
  return result