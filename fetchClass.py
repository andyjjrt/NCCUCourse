import requests, os, json
from dotenv import load_dotenv
from tqdm import tqdm
from time import time, sleep
load_dotenv()

year = os.getenv("YEAR")
semester = os.getenv("SEM")

dir_path = os.path.dirname(os.path.realpath(__file__))

timeHold = 0.2

def fetchClass():
  print("Fetching class, YEAR=" + year + " SEM=" + semester)
  classes = list()
  categories = list()
  units = requests.get("https://qrysub.nccu.edu.tw/assets/api/unit.json").json()
  for dp1 in units:
    if dp1["utCodL1"] == "0": continue
    for dp2 in dp1["utL2"]:
      if dp2["utCodL2"] == "0": continue
      for dp3 in dp2["utL3"]:
        if dp3["utCodL3"] == "0": continue
        categories.append({"dp1": dp1["utCodL1"], "dp2": dp2["utCodL2"], "dp3": dp3["utCodL3"]})

  st = time()
  reader = tqdm(categories, leave=False)
  for _cat in reader:
    try:
      while time() - st < timeHold:
        sleep(0.01)
      st = time()
      res = requests.get("https://es.nccu.edu.tw/course/zh-TW/:sem=" + year + semester + " :dp1=" + _cat["dp1"] + " :dp2=" + _cat["dp2"] + " :dp3=" + _cat["dp3"])
      jsonRes = res.json()
      if len(jsonRes) >= 500:
        raise Exception(_cat + "too large.")
      dpReader = tqdm(jsonRes, leave=False)
      for course in dpReader:
        courseId = course["subNum"]
        classes.append(courseId)
    except Exception as e:
      with open(os.path.join(dir_path, "_data", "log.txt"), "a") as f:
        f.write(str(e))
        f.close()

  with open(os.path.join(dir_path, "_data", "classes.json"), "w+") as f:
    json.dump(classes, f)
    f.close()
  print("Fetching class done at " + str(time()))
  
  return classes