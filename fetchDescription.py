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
    response = requests.get("http://es.nccu.edu.tw/course/zh-TW/{} /".format(courseId))
    response.raise_for_status()
    if len(response.json()) != 1:
      raise Exception("No matched course")
    result["qrysub"] = response.json()[0]
    response = requests.get("http://es.nccu.edu.tw/course/en/{} /".format(courseId))
    response.raise_for_status()
    if len(response.json()) != 1:
      raise Exception("No matched course")
    result["qrysubEn"] = response.json()[0]
    location = str(result["qrysub"]["teaSchmUrl"]).replace("https://", "http://")
    
    # fetching content
    res = requests.get(location)
    soap = BeautifulSoup(res.content, "html.parser")
    isOld = soap.find("title").text == "教師資訊整合系統"
    
    if isOld:
      contents = soap.find("div", {"class": "accordionPart"}).find_all("span")
      for objective in contents[0].find("div", {"class": "qa_content"}):
        for line in [x for x in re.split(r'[\n\r]+', objective.get_text(strip=True)) if len(x) > 0 and x != " "]:
          result["description"].append(line)
      for objective in contents[1].find("div", {"class": "qa_content"}):
        for line in [x for x in re.split(r'[\n\r]+', objective.get_text(strip=True)) if len(x) > 0 and x != " "]:
          result["objectives"].append(line)  
    else:
      # get syllabus description
      descriptionTitle = soap.find("div", {"class": "col-sm-7 sylview--mtop col-p-6"}).find("h2", {"class": "text-primary"})
      descriptions = descriptionTitle.find_next_siblings(True)
      for description in descriptions:
        if description.attrs and description.attrs.get("class") and ["row", "sylview-mtop", "fa-border"] == description.attrs["class"]:
          break
        for line in [x for x in re.split(r'[\n\r]+', description.get_text(strip=True)) if len(x) > 0 and x != " "]:
          result["description"].append(line)    
      
      # get syllabus objectives
      objectives = soap.find("div", {"class": "container sylview-section"}).select_one(".col-p-8")
      for objective in objectives:
        for line in [x for x in re.split(r'[\n\r]+', objective.get_text(strip=True)) if len(x) > 0 and x != " "]:
          result["objectives"].append(line)
    
  except Exception as e:
    logging.error(courseId)
    logging.error(e)
  
  return result

if __name__ == "__main__":
  print(fetchDescription("1131000219521"))