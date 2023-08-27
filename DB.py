import sqlite3

class DB:
  con: sqlite3.Connection
  
  def __init__(self, location: str) -> None:
    self.con = sqlite3.connect(location)
    cur = self.con.cursor()
    # subNam => name 科目名稱
    # lmtKind 通識類別
    # core 是否為核心通識
    # langTpe => lang 語言
    # smtQty N學期科目
    # subClassroom => classroom 教室
    # subGde => unit 開課單位
    # subKind => kind 必選群
    # subPoint => point 學分
    # subTime => time 時間
    
    cur.execute("""
      CREATE TABLE IF NOT EXISTS COURSE ( 
        id TEXT NOT NULL,
        y TEXT,
        s TEXT,
        subNum TEXT,
        name TEXT,
        nameEn TEXT,
        teacher TEXT,
        teacherEn TEXT,
        kind INTEGER,
        time TEXT,
        timeEn TEXT,
        lmtKind TEXT,
        lmtKindEn TEXT,
        core INTEGER,
        lang TEXT,
        langEn TEXT,
        smtQty INTEGER,
        classroom TEXT,
        classroomId TEXT,
        unit TEXT,
        unitEn TEXT,
        dp1 TEXT NOT NULL,
        dp2 TEXT NOT NULL,
        dp3 TEXT NOT NULL,
        point REAL,
        subRemainUrl TEXT,
        subSetUrl TEXT,
        subUnitRuleUrl TEXT,
        teaExpUrl TEXT,
        teaSchmUrl TEXT,
        tranTpe TEXT,
        tranTpeEn TEXT,
        info TEXT,
        infoEn TEXT,
        note TEXT,
        noteEn TEXT,
        syllabus TEXT,
        objective TEXT,
        PRIMARY KEY ( id, dp1, dp2, dp3 )
      );
    """)
    cur.execute("CREATE TABLE IF NOT EXISTS TEACHER ( id TEXT, name TEXT, PRIMARY KEY ( id, name ) )")
    cur.execute("CREATE TABLE IF NOT EXISTS RATE ( courseId TEXT NOT NULL, rowId TEXT NOT NULL, teacherId TEXT, content TEXT, contentEn TEXT, PRIMARY KEY (courseId, rowId) )")
    cur.execute("CREATE TABLE IF NOT EXISTS RESULT ( courseId TEXT, yearsem TEXT, name TEXT, teacher TEXT, time TEXT, studentLimit INTEGER, studentCount INTEGER, lastEnroll INTEGER, PRIMARY KEY (courseId))")
    
  def addRate(self, rowId: str, courseId: str, teacherId: str, content: str, contentEn: str):
    cur = self.con.cursor()
    cur.execute("INSERT OR REPLACE INTO RATE (rowId, courseId, teacherId, content, contentEn) VALUES (?, ?, ?, ?, ?)", (rowId, courseId, teacherId, content, contentEn))
    self.con.commit()
  
  def addTeacher(self, id: str, name: str):
    cur = self.con.cursor()
    cur.execute("INSERT OR REPLACE INTO TEACHER (id, name) VALUES (?, ?)", (id, name))
    self.con.commit()
  
  def addResult(self, yearsem: str, courseId: str, name: str, teacher: str, time: str, studentLimit: int, studentCount: int, lastEnroll: int):
    cur = self.con.cursor()
    cur.execute("INSERT OR REPLACE INTO RESULT (courseId, yearsem, name, teacher, time, studentLimit, studentCount, lastEnroll) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (yearsem + courseId, yearsem, name, teacher, time, studentLimit, studentCount, lastEnroll))
    self.con.commit()
    
  def getTeachers(self):
    cur = self.con.cursor()
    request = cur.execute("SELECT * FROM TEACHER")
    response = request.fetchall()
    
    res = dict()
    for x in response:
      res[x[1]] = x[0]
    
    return res
  
  def addCourse(self, courseData: dict, courseDataEn: dict, dp1: str, dp2: str, dp3: str, syllabus: str, description: str):
    if courseData["subKind"] == "必修":
      kind = 1
    elif courseData["subKind"] == "選修":
      kind = 2
    elif courseData["subKind"] == "群修":
      kind = 3
    elif "通識" in courseData["lmtKind"]:
      kind = 4
    else:
      kind = 0
        
    cur = self.con.cursor()
    cur.execute(
      '''INSERT OR REPLACE INTO COURSE ( id, y, s,  subNum, name, nameEn, teacher, teacherEn, kind, time, timeEn, lmtKind, lmtKindEn, core, lang, langEn, smtQty, classroom, classroomId, unit, unitEn, dp1, dp2, dp3, point, subRemainUrl, subSetUrl, subUnitRuleUrl, teaExpUrl, teaSchmUrl, tranTpe, tranTpeEn, info, infoEn, note, noteEn, syllabus, objective ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
      (
        "{}{}{}".format(courseData["y"], courseData["s"], courseData["subNum"]),
        courseData["y"],
        courseData["s"],
        courseData["subNum"],
        courseData["subNam"],
        courseDataEn["subNam"],
        courseData["teaNam"],
        courseDataEn["teaNam"],
        kind,
        courseData["subTime"],
        courseDataEn["subTime"],
        courseData["lmtKind"],
        courseDataEn["lmtKind"],
        (lambda x:1 if x == "是" else 0)(courseData["core"]),
        courseData["langTpe"],
        courseDataEn["langTpe"],
        courseData["smtQty"],
        courseData["subClassroom"],
        courseDataEn["subClassroom"],
        courseData["subGde"],
        courseDataEn["subGde"],
        dp1,
        dp2,
        dp3,
        float(courseData["subPoint"]),
        courseData["subRemainUrl"],
        courseData["subSetUrl"],
        courseData["subUnitRuleUrl"],
        courseData["teaExpUrl"],
        courseData["teaSchmUrl"],
        courseData["tranTpe"],
        courseDataEn["tranTpe"],
        courseData["info"],
        courseDataEn["info"],
        courseData["note"],
        courseDataEn["note"],
        syllabus, description
      )
    )
    self.con.commit()
  
  def getCourse(self, y: str, s: str):
    cur = self.con.cursor()
    request = cur.execute('SELECT teaNam FROM COURSE WHERE y = 111 AND s = 2')
    response = request.fetchall()
    
    return [str(x[0]) for x in response]
  
  def getThisSemesterCourse(self, y: str, s: str):
    cur = self.con.cursor()
    request = cur.execute('SELECT DISTINCT subNum FROM COURSE WHERE y = ? AND s = ?', [y, s])
    response = request.fetchall()
    
    return [str(x[0]) for x in response]

  def isCourseExist(self, courseId: str, dp: dict):
    cur = self.con.cursor()
    request = cur.execute('SELECT COUNT(*) FROM COURSE WHERE id = ? AND dp1 = ? AND dp2 = ? AND dp3 = ?', [courseId, dp["dp1"], dp["dp2"], dp["dp3"]])
    response = request.fetchone()
    return response[0] > 0
  
  def isRateExist(self, courseId: str):
    cur = self.con.cursor()
    request = cur.execute('SELECT COUNT( DISTINCT courseId) FROM RATE WHERE courseId = ?', [courseId])
    response = request.fetchone()
    return response[0] > 0

if __name__ == "__main__":
  db = DB("test.db")
  print(db.getThisSemesterCourse("111", "2"))