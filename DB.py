import sqlite3

class DB:
  con: sqlite3.Connection
  
  def __init__(self, location: str) -> None:
    self.con = sqlite3.connect(location)
    cur = self.con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS COURSE ( id TEXT, core TEXT, far TEXT, gdeTpe TEXT, gdeTpeMsg TEXT, info TEXT, isTrace TEXT, langTpe TEXT, lmtKind TEXT, note TEXT, pay TEXT, s TEXT, smtQty TEXT, subClassroom TEXT, subGde TEXT, subKind TEXT, subLocUrl TEXT, subNam TEXT, subNum TEXT, subOdr TEXT, subPoint TEXT, subRemainUrl TEXT, subSetUrl TEXT, subTime TEXT, subUnitRuleUrl TEXT, teaExpUrl TEXT, teaNam TEXT, teaSchmUrl TEXT, tranTpe TEXT, y TEXT, syllabus TEXT, objective TEXT, PRIMARY KEY ( id ) );")
    cur.execute("CREATE TABLE IF NOT EXISTS TEACHER ( id TEXT, name TEXT, UNIQUE( id, name ) )")
    cur.execute("CREATE TABLE IF NOT EXISTS RATE ( courseId TEXT, teacherId TEXT, content TEXT )")
    
  def addRate(self, courseId: str, teacherId: str, content: str):
    cur = self.con.cursor()
    cur.execute("INSERT OR REPLACE INTO RATE (courseId, teacherId, content) VALUES (?, ?, ?)", (courseId, teacherId, content))
    self.con.commit()
  
  def addTeacher(self, id: str, name: str):
    cur = self.con.cursor()
    cur.execute("INSERT OR REPLACE INTO TEACHER (id, name) VALUES (?, ?)", (id, name))
    self.con.commit()
  
  def addCourse(self, courseData: dict, syllabus: str, description: str):
    cur = self.con.cursor()
    cur.execute(
      '''INSERT OR REPLACE INTO COURSE ( id, core, far, gdeTpe, gdeTpeMsg, info, isTrace, langTpe, lmtKind, note, pay, s, smtQty, subClassroom, subGde, subKind, subLocUrl, subNam, subNum, subOdr, subPoint, subRemainUrl, subSetUrl, subTime, subUnitRuleUrl, teaExpUrl, teaNam, teaSchmUrl, tranTpe, y, syllabus, objective) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
      (
        "{}{}{}".format(courseData["y"], courseData["s"], courseData["subNum"]), courseData["core"], courseData["far"],
        courseData["gdeTpe"], courseData["gdeTpeMsg"], courseData["info"], courseData["isTrace"], courseData["langTpe"],
        courseData["lmtKind"], courseData["note"], courseData["pay"], 
        courseData["s"], courseData["smtQty"], courseData["subClassroom"], courseData["subGde"], courseData["subKind"],
        courseData["subLocUrl"], courseData["subNam"], courseData["subNum"], courseData["subOdr"], courseData["subPoint"],
        courseData["subRemainUrl"], courseData["subSetUrl"], courseData["subTime"], courseData["subUnitRuleUrl"], 
        courseData["teaExpUrl"], courseData["teaNam"], courseData["teaSchmUrl"], courseData["tranTpe"], courseData["y"],
        syllabus, description
      )
    )
    self.con.commit()
    

if __name__ == "__main__":
  db = DB("test.db")