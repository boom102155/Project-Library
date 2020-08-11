from time import strftime, gmtime
from flask import Flask, jsonify, render_template, request, json, redirect, url_for, session, flash, make_response
from sqlalchemy import create_engine
import os, pdfkit

os.environ["NLS_LANG"] = ".UTF8"
db_connect = create_engine('oracle://ADBOOM:boom125478@127.0.0.1:1521/xe')

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.secret_key = os.urandom(24)

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

# ===================================================================
@app.route('/projsearch', methods = ['GET', 'POST'])
def projsearch():
    return render_template("projSearch.html")

@app.route('/projgetsearch', methods = ['GET', 'POST'])
def projgetsearch():
    if request.method == "POST":

        data = request.form
        conn = db_connect.connect()
        query1 = conn.execute("SELECT "
                              "pj.pj_year, "
                              "pj.pj_name, "
                              "pj.pj_name_eng, "
                              "pj.s_name1, "
                              "pj.s_id1, "
                              "pj.s_name2, "
                              "pj.s_id2, "
                              "ps.name || ' ' || ps.surname AS profName, "
                              "pr.progress_num, "
                              "pr.import_date, "
                              "pr.detail, "
                              "pr.issue, "
                              "pr.next_date "
                              "FROM "
                              "project pj inner join person ps on pj.person_id1 = ps.person_id "
                              "LEFT JOIN progress_report pr ON pj.pj_id = pr.pj_id "
                              "WHERE "
                              "pj.pj_id in (SELECT PJ_ID FROM sumproject WHERE SID = " + (data["SID"]) + ")")

        query2 = conn.execute("SELECT "
                              "pj.pj_id, "
                              "pj.pj_name,"
                              "pj.pj_name_eng "
                              "FROM sumproject pj "
                              "WHERE "
                              "SID = '"+ (data["SID"])+"' ")

        rows1 = query1.fetchall()
        rows2 = query2.fetchall()
        # for row in rows:
        #     list1 = ["PJ_YEAR", "PJ_NAME", "PJ_NAME_ENG", "S_NAME1", "S_ID1", "S_NAME2",
        #              "S_ID2", "NAME", "PROGRESS_NUM", "IMPORT_DATE", "DETAIL", "ISSUE", "NEXT_DATE"]
        #     list2 = [row["name"], row["surname"], row["type"], row["faculty"], row["class"]]
        #     data = zip(list1, list2)
        #     d = dict(data)
        #     print(d)
        if query1.rowcount == 0:
            flash("ไม่พบข้อมูลโครงงานในระบบ กรุณากรอกข้อมูลโครงงาน")
            return redirect(url_for('projfirsttimeupload'))
        else:
            return render_template("projProgress.html", rows1=rows1, rows2=rows2)


@app.route('/projprogress', methods = ['GET', 'POST'])
def projprogress():
    return render_template("projProgress.html")

@app.route('/projform', methods=['GET', 'POST'])
def projform():
    return render_template("projForm.html")

@app.route('/projfirsttimeupload', methods=['GET', 'POST'])
def projfirsttimeupload():
    conn = db_connect.connect()
    query = conn.execute("SELECT PERSON_ID, (NAME || ' ' || SURNAME) as perfessorname "
                         "FROM PERSON "
                         "WHERE PERSON_ID BETWEEN 1001 and 1999")

    query2 = conn.execute("SELECT PJTYPE_ID "
                          "FROM PROJECT_TYPE")

    rows = query.fetchall()
    rows2 = query2.fetchall()

    return render_template("projFirstTimeUpload.html", rows=rows, rows2=rows2)


# ===================================================================

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
    return render_template("projUpload.html", rows=rows, rows2=rows2)

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

# ===============================================================================

@app.route('/addfirstproj' , methods = ['GET' , 'POST'])
def addfirstproj():
    try:
        data = request.get_json()
        conn = db_connect.connect()
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
                     "PERSON_ID2,"
                     "PJ_NAME_ENG) "
                    
                     "VALUES (PROJECT_SEQ.NEXTVAL, :2, :3, :4, :5, :6, NVL(:7, 'ไม่มี'), NVL(:8, 'ไม่มี'), :9, NVL(:10, 0), :11)",
                     (data["pName"], data["pYear"], data["pType"], data["sNameF"], data["sIdF"], data["sNameS"], data["sIdS"], data["profPrimary"], data["profSub"], data["pNameEng"]))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()
        return redirect("/projprogress")


@app.route('/addprojmeetdetail', methods=['GET', 'POST'])
def addprojmeetdetail():
    if request.method == "POST":
        try:
            data = request.form
            conn = db_connect.connect()
            conn.execute("INSERT INTO PROGRESS_REPORT "                 
                         "(PJ_ID, "
                         "DETAIL, "
                         "ISSUE, "
                         "NEXT_DATE) "
                         "VALUES (:1, :2, :3, TO_DATE(:4, 'yyyy-mm-dd'))",
                         (data["pID"], data["pMeetDetail"], data["pIssue"], data["pNextMeet"]))
            conn.commit()


            # pdfform = render_template("projForm.html", rows=rows)
            # path_wkhtmltopdf = 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
            # config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
            # pdfkit.from_string(pdfform, "project_progress.pdf", configuration=config)

        except:
            conn.rollback()
        finally:
            query = conn.execute("SELECT pj.PJ_YEAR, pj.PJ_NAME, pj.PJ_NAME_ENG, pj.S_NAME1, pj.S_ID1, "
                                 "pj.S_NAME2, pj.S_ID2, ps.NAME || ' ' || ps.SURNAME as ProfName, lp.PROGRESS_NUM, lp.IMPORT_DATE, lp.DETAIL, lp.NEXT_DATE "
                                 "FROM "
                                 "lastprogress lp, "
                                 "project pj, "
                                 "person ps "
                                 "WHERE "
                                 "lp.pj_id = " + (data["pID"]) +
                                 " AND   pj.pj_id = lp.pj_id "
                                 "AND pj.PERSON_ID1 = ps.PERSON_ID")
            rows = query.fetchall()
            flash("บันทึกข้อมูลสำเร็จแล้ว")
            # return redirect(url_for('projfirsttimeupload'))
            return render_template("projForm.html", rows=rows)
            conn.close()

# ==============================================================================================


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

@app.route('/loginfornewsupload', methods = ['GET', 'POST'])
def loginfornewsupload():
    data = request.get_json()
    conn = db_connect.connect()
    query = conn.execute("SELECT PERSON_ID FROM PERSON "
                         "WHERE EMAIL = '" + (data["user"]) + "'" +
                         " AND PASSWORD = '" + (data["pass"]) + "'")
    rows = query.fetchall()
    for row in rows:
        list2 = [row["person_id"]]
        session['user'] = ', '.join(str(x) for x in list2)

    return jsonify(list2)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return 'Dropped'

@app.route('/newsupload' , methods = ['GET' , 'POST'])
def newsload():
    conn = db_connect.connect()
    if 'user' in session:
        username = session['user']

        query = conn.execute(
            "SELECT pb.PUB_ID, pb.TOPIC, p.NAME , TO_CHAR(pb.PUB_DATE,'dd-mm-yyyy') as pubdate, pb.PIN_STATUS,"
            "(CASE pb.PIN_STATUS WHEN '1' THEN 'ประกาศสำคัญ' ELSE 'ประกาศทั่วไป' END) as pinstatus "
            "FROM PUBLISH pb, PERSON p "
            "WHERE pb.PERSON_ID = p.PERSON_ID "
            "ORDER BY PIN_STATUS DESC")
        rows = query.fetchall()

        query2 = conn.execute("SELECT NAME FROM PERSON "
                              "WHERE PERSON_ID = " + username)
        rows2 = query2.fetchall()

        for row in rows2:
            uname = row["name"]
            return render_template("newsUpload.html", rows=rows, uname=uname, username=username)
    else:
        query = conn.execute(
            "SELECT pb.PUB_ID, pb.TOPIC, p.NAME , TO_CHAR(pb.PUB_DATE,'dd-mm-yyyy') as pubdate, pb.PIN_STATUS,"
            "(CASE pb.PIN_STATUS WHEN '1' THEN 'ประกาศสำคัญ' ELSE 'ประกาศทั่วไป' END) as pinstatus "
            "FROM PUBLISH pb, PERSON p "
            "WHERE pb.PERSON_ID = p.PERSON_ID "
            "ORDER BY PIN_STATUS DESC")
        rows = query.fetchall()

        return render_template("newsUpload.html", rows=rows)

@app.route('/updatenewspin' , methods = ['GET', 'POST'])
def updatenewspin():
    data = request.get_json()
    conn = db_connect.connect()

    conn.execute("UPDATE PUBLISH "
                         "SET PIN_STATUS = CASE "
                         "WHEN PIN_STATUS='0' THEN '1' "
                         "ELSE '0' "
                         "END WHERE PUB_ID = " + data["pid"])
    conn.commit()
    return json.dumps(data)


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
