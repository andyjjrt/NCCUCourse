from dotenv import load_dotenv
from os import getenv
import requests
from util import get_login_url, get_addtrack_url, get_deltrack_url, get_track_url
load_dotenv()

class User:
  _username: str
  _password: str
  _token: str
  
  def __init__(self) -> None:
    self._username = getenv("USERNAME") or ""
    self._password = getenv("PASSWORD") or ""
    res = requests.get(get_login_url(self._username, self._password)).json()
    try:
      self._token = res[0]["encstu"]
    except:
      raise Exception("token error")
  
  def addTrack(self, courseId: str):
    addres = requests.post(get_addtrack_url(self._token, courseId)).json()
    if(addres[0]["procid"] != "1"): raise Exception("Add fail: " + courseId)
  
  def deleteTrack(self, courseId: str):
    deleteres = requests.delete(get_deltrack_url(self._token, courseId)).json()
    if(deleteres[0]["procid"] != "9"): raise Exception("Delete fail: " + courseId)
    
  def getTrack(self):
    courseres = requests.get(get_track_url(self._token)).json()
    return courseres