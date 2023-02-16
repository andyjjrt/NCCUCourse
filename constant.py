import os
from dotenv import load_dotenv
load_dotenv()

YEAR = os.getenv('YEAR')
SEM = os.getenv('SEM')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

SERVER_URL = "https://es.nccu.edu.tw/"
KEY = "angu1arjjlST@2019"
SEM_API = SERVER_URL + "semester/"
PERSON_API = SERVER_URL + "person/"
COURSE_API = SERVER_URL + "course/"
TRACE_API = SERVER_URL + "tracing/"

def URL(id, year_sem=YEAR + SEM):
    return "https://newdoc.nccu.edu.tw/teaschm/" + year_sem + "/statistic.jsp-tnum=" + id + ".htm"

def COURSE_RATE_URL(param, year_sem=YEAR + SEM):
    return "https://newdoc.nccu.edu.tw/teaschm/" + year_sem + "/" + param

YEAR_SEM = YEAR + SEM

def RATE_QRY():
    return str(os.getenv('RATE_QRY')).split(",")

COURSERESULT_YEARSEM = ["1102", "1111"]
def COURSERESULT_CSV(sem): return sem + "CourseResult.csv"