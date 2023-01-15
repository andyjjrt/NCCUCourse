import os, json

from fetchClass import fetchClass
from fetchTeacherId import fetchTeacherId
from fetchRate import fetchRate

dir_path = os.path.dirname(os.path.realpath(__file__))

def useOldClasses():
  with open(os.path.join(dir_path, "_data", "classes.json"), "r") as f:
    return json.loads(f.read())

def useOldTeachers():
  with open(os.path.join(dir_path, "_data", "teachers.json"), "r") as f:
    return json.loads(f.read())

if not os.path.exists(os.path.join(dir_path, "_data")):
  os.makedirs(os.path.join(dir_path, "_data"))

# classes = fetchClass()
# TeacherId = fetchTeacherId(classes)
fetchRate(useOldTeachers())