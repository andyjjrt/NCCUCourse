import os
from dotenv import load_dotenv
load_dotenv()

YEAR = "111"
SEM = "1"
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
COURSELIST_CSV = "1111CoursesList.csv"

SERVER_URL = "https://es.nccu.edu.tw/"
KEY = "angu1arjjlST@2019"
SEM_API = SERVER_URL + "semester/"
PERSON_API = SERVER_URL + "person/"
COURSE_API = SERVER_URL + "course/"
TRACE_API = SERVER_URL + "tracing/"

def URL(id):
    return "https://newdoc.nccu.edu.tw/teaschm/" + YEAR + SEM + "/statistic.jsp-tnum=" + id + ".htm"

def COURSE_RATE_URL(param):
    return "https://newdoc.nccu.edu.tw/teaschm/" + YEAR + SEM + "/" + param

YEAR_SEM = YEAR + SEM
