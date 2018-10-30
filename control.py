from time import strftime, gmtime
from flask import Flask, jsonify, render_template, request, json, redirect, url_for, session
from sqlalchemy import create_engine
import os

os.environ["NLS_LANG"] = ".UTF8"
db_connect = create_engine('oracle://ADBOOM:boom125478@127.0.0.1:1521/xe')

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/index' , methods = ['GET','POST'])
def index():
    conn = db_connect.connect()
    query = conn.execute("SELECT * "
                         "FROM (SELECT pb.TOPIC, p.NAME, TO_CHAR(pb.PUB_DATE,'dd-mm-yyyy') as pubdate, pb.PIN_STATUS, pb.PUB_ID "
                                "FROM PUBLISH pb, PERSON p "
                                "WHERE pb.PERSON_ID = p.PERSON_ID "
                                "ORDER BY pb.PIN_STATUS DESC, pb.PUB_ID DESC) supplier2 "
                         "WHERE ROWNUM <= 7")
    rows = query.fetchall()

    return render_template("index.html", rows=rows)

@app.route('/projlist/<projtypeid>' , methods = ['GET','POST'])
def projlist(projtypeid):
    conn = db_connect.connect()
    data = request.get_json()

    if projtypeid == '1':
        query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , PJTYPE_ID , KEYWORD "
                              "FROM PROJECT "
                              "WHERE PJTYPE_ID = 'โปรแกรมเพื่อความบันเทิง'")
    elif projtypeid == '2':
        query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , PJTYPE_ID , KEYWORD "
                              "FROM PROJECT "
                              "WHERE PJTYPE_ID = 'โปรแกรมเพื่อส่งเสริมการเรียนรู้'")
    elif projtypeid == '3':
        query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , PJTYPE_ID , KEYWORD "
                              "FROM PROJECT "
                              "WHERE PJTYPE_ID = 'โปรแกรมเพื่อช่วยคนพิการ/ผู้สูงอายุ/สัตว์เลี้ยง'")
    elif projtypeid == '4':
        query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , PJTYPE_ID , KEYWORD "
                              "FROM PROJECT "
                              "WHERE PJTYPE_ID = 'โปรแกรมระบบสารสนเทศสำหรับองค์กร'")
    elif projtypeid == '5':
        query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , PJTYPE_ID , KEYWORD "
                              "FROM PROJECT "
                              "WHERE PJTYPE_ID = 'โปรแกรมด้าน Internet of Things'")
    elif projtypeid == '6':
        query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , PJTYPE_ID , KEYWORD "
                              "FROM PROJECT "
                              "WHERE PJTYPE_ID = 'Computational Intelligence'")
    elif projtypeid == '7':
        query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , PJTYPE_ID , KEYWORD "
                              "FROM PROJECT "
                              "WHERE PJTYPE_ID = 'โปรแกรมเพื่องานการพัฒนาด้านวิทยาศาสตร์และเทคโนโลยี'")
    else:
        query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , PJTYPE_ID , KEYWORD "
                             "FROM PROJECT")

    rows = query.fetchall()
    return render_template("projList.html", rows=rows)


@app.route('/projcontent/<projid>' , methods = ['GET','POST'])
def projcontent(projid):
    conn = db_connect.connect()
    query = conn.execute("SELECT pr.PJ_NAME, pr.PJ_YEAR, pr.PJTYPE_ID, pr.S_NAME1, pr.S_ID1, pr.S_NAME2, pr.S_ID2, "
                         "(pe.NAME || ' ' || pe.SURNAME) AS PERSON1, (pe2.NAME || ' ' || pe2.SURNAME) AS PERSON2, pr.KEYWORD, pf.NAME "
                         "FROM PROJECT pr , PERSON pe , PERSON pe2, PROJECT_FILE pf "
                         "WHERE pr.PJ_ID = " + projid +
                         " AND pr.PERSON_ID1 = pe.PERSON_ID AND pr.PERSON_ID2 = pe2.PERSON_ID AND pr.PJ_ID = pf.PJ_ID")
    rows = query.fetchall()

    return render_template("projContent.html" , rows=rows)

@app.route('/projupload' , methods = ['GET' , 'POST'])
def projupload():
    conn = db_connect.connect()
    query = conn.execute("SELECT PERSON_ID, (NAME || ' ' || SURNAME) as perfessorname "
                          "FROM PERSON "
                          "WHERE PERSON_ID BETWEEN 1001 and 1999")

    query2 = conn.execute("SELECT PJTYPE_ID "
                          "FROM PROJECT_TYPE")

    rows = query.fetchall()
    rows2 = query2.fetchall()
    return  render_template("projUpload.html" , rows=rows , rows2=rows2)

@app.route('/uploader', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST':
      # f = request.files['file']
      # f.save(secure_filename(f.filename))
      # return 'file uploaded successfully'
      target = os.path.join(APP_ROOT, 'static/UPLOAD')
      print(target)
      file = request.files['file']
      if file.filename == '':
          return 'no file selected'

      if not os.path.isdir(target):
          os.mkdir(target)

      st = strftime("%d%m%Y", gmtime())
      t1 = strftime("%H", gmtime())
      t2 = strftime("%M", gmtime())
      t3 = strftime("%S", gmtime())

      for file in request.files.getlist("file"):
          print(file)
          filename = file.filename
          destination = "/".join([target, st + '_' + t1 + t2 + t3 + '.'+ filename.split('.')[1]])
          print("Accept incoming file:", filename.split('.')[1])
          print(destination)
          file.save(destination)
      return redirect("/projupload")

@app.route('/addproj' , methods = ['GET' , 'POST'])
def addproj():
    conn = db_connect.connect()
    data = request.get_json()
    st = strftime("%d%m%Y", gmtime())
    t1 = strftime("%H", gmtime())
    t2 = strftime("%M", gmtime())
    t3 = strftime("%S", gmtime())

    try:
        constrname = st + '_' + t1 + t2 + t3 + '.' + (data['pathpic'])
        conn.execute("INSERT INTO PROJECT "
                     "(PJ_ID, "
                     "PJ_NAME, "
                     "PJ_YEAR, "
                     "PJTYPE_ID, "
                     "S_NAME1, "
                     "S_ID1, "
                     "S_NAME2, "
                     "S_ID2, "
                     "PERSON_ID1, "
                     "PERSON_ID2, "
                     "KEYWORD) "
                     "VALUES (PROJECT_SEQ.NEXTVAL, :2, :3, :4, :5, :6, NVL(:7, 'ไม่มี'), NVL(:8, 'ไม่มี'), :9, NVL(:10, 0), :11)",
                     (data["pName"], data["pYear"], data["pType"], data["sNameF"], data["sIdF"], data["sNameS"], data["sIdS"], data["profPrimary"], data["profSub"], data["keyword"]))

        conn.execute("INSERT INTO PROJECT_FILE "
                     "(PATH, "
                     "NAME, "
                     "PJ_ID) "
                     "(SELECT '"+ constrname +"', '"+ constrname +"', MAX(PJ_ID) FROM PROJECT)")
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()
    return json.dumps(data)

@app.route('/newsupdate' , methods = ['GET' , 'POST'])
def newsupdate():
    conn = db_connect.connect()
    query = conn.execute("SELECT pb.PUB_ID, pb.TOPIC, p.NAME , TO_CHAR(pb.PUB_DATE,'dd-mm-yyyy') as pubdate, pb.PIN_STATUS,"
                         "(CASE pb.PIN_STATUS WHEN '1' THEN 'ประกาศสำคัญ' ELSE 'ประกาศทั่วไป' END) as pinstatus "
                         "FROM PUBLISH pb, PERSON p "
                         "WHERE pb.PERSON_ID = p.PERSON_ID "
                         "ORDER BY PIN_STATUS DESC")

    rows = query.fetchall()

    return render_template("newsUpdate.html", rows=rows)

@app.route('/addnews' , methods = ['GET' , 'POST'])
def addnews():
    data = request.get_json()
    conn = db_connect.connect()
    conn.execute("INSERT INTO PUBLISH "
                 "(TOPIC, "
                 "DESCRIPTION, "
                 "PIN_STATUS, "
                 "PUB_DATE, "
                 "PERSON_ID) "
                 "VALUES (:1, :2, :3, TO_DATE(:4, 'yyyy-mm-dd'), :5)",
                 (data["vtopic"], data["vnewsupdate"], data["vpubstatus"], data["vdate"], data["vperson"]))

    return json.dumps(data)

@app.route('/newscontent/<newsid>' , methods = ['GET', 'POST'])
def newscontent(newsid):
    conn = db_connect.connect()
    query = conn.execute("SELECT pb.TOPIC, pb.DESCRIPTION, TO_CHAR(pb.PUB_DATE,'dd-mm-yyyy') as pubdate, (p.NAME || ' ' || p.SURNAME) as person "
                         "FROM PUBLISH pb, PERSON p "
                         "WHERE pb.PUB_ID = " + newsid +
                         " AND pb.PERSON_ID = p.PERSON_ID")
    rows = query.fetchall()
    return render_template("newsContent.html", rows=rows)

@app.route('/projsearch', methods = ['GET', 'POST'])
def filtersearch():
    conn = db_connect.connect()
    query1 = conn.execute("SELECT PERSON_ID, (NAME || ' ' || SURNAME) as perfessorname "
                         "FROM PERSON "
                         "WHERE PERSON_ID BETWEEN 1001 and 1999")
    query2 = conn.execute("SELECT PJTYPE_ID "
                          "FROM PROJECT_TYPE")

    rows1 = query1.fetchall()
    rows2 = query2.fetchall()

    return render_template("filterSearch.html", rows1=rows1, rows2=rows2)

name = ""
year = ""
type = ""
s1 = ""
s2 = ""
prof = ""

@app.route('/getdatafiltersearch', methods = ['GET', 'POST'])
def projlistfiltersearch():
    data = request.get_json()

    global name
    global year
    global type
    global s1
    global s2
    global prof

    name = data["dName"]
    year = data["dYear"]
    type = data["dType"]
    s1 = data["dNameF"]
    s2 = data["dNameS"]
    prof = data["dProfPrimary"]

    return json.dumps(data)


@app.route('/searchresult', methods = ['GET', 'POST'])
def showdataforsearch():
    try:
        conn = db_connect.connect()

        query = conn.execute("SELECT pr.PJ_ID , pr.PJ_NAME , pr.PJ_YEAR , pr.PJTYPE_ID , pr.KEYWORD "
                                "FROM PROJECT pr, PERSON pe "
                                "WHERE pr.PERSON_ID1 = pe.PERSON_ID "
                                "AND pr.PJ_NAME LIKE '%" + name + "%' "
                                "AND pr.PJ_YEAR LIKE '%" + year + "%' "
                                "AND pr.PJTYPE_ID LIKE '%" + type + "%' "
                                "AND pr.S_NAME1 LIKE '%" + s1 + "%' "
                                "AND pr.S_NAME2 LIKE '%" + s2 + "%' "
                                "AND pr.PERSON_ID1 LIKE '%" + prof + "%'")


        rows = query.fetchall()
    except Exception as e:
        return "เกิดความผิดพลาดในการค้นหา กรุณากรอกข้อมูลเพื่อค้นหาอีกครั้ง <a href = '/projsearch'></b>" + \
           "คลิกที่นี่เพื่อกรอกข้อมูลใหม่อีกครั้ง</b></a>"

    return render_template("projList.html", rows=rows)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
