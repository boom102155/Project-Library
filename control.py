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
    return render_template("index.html")

@app.route('/projlist' , methods = ['GET','POST'])
def projlist():
    conn = db_connect.connect()
    query = conn.execute("SELECT PJ_ID , PJ_NAME , PJ_YEAR , KEYWORD "
                         "FROM PROJECT")
    rows = query.fetchall()
    return render_template("projList.html", rows=rows)

# @app.route('/getsessionprojid' , methods = ['GET' , 'POST'])
# def getsessionprojid():
#     data = request.get_json()
#     conn = db_connect.connect()
#     query = conn.execute("SELECT PROJ_ID FROM PROJECT WHERE PROJ_ID = '" + (data["projid"]) + "'")
#     rows = query.fetchall()
#     for row in rows:
#         list1 = ["PROJ_ID"]
#         list2 = [row["proj_id"]]
#         data = zip(list1, list2)
#         d = dict(data)
#         session['projectid'] = ''.join(list2)
#     return jsonify()

@app.route('/projcontent/<projid>' , methods = ['GET','POST'])
def projcontent(projid):
    conn = db_connect.connect()
    query = conn.execute("SELECT "
                         "pr.PJ_NAME, "
                         "pr.PJ_YEAR , "
                         "pr.PJTYPE_ID , "
                         "pr.S_NAME1 , "
                         "pr.S_ID1 , "
                         "pr.S_NAME2 , "
                         "pr.S_ID2 , "
                         "(pe.NAME || ' ' || pe.SURNAME) AS PERSON1 , "
                         "(pe2.NAME || ' ' || pe2.SURNAME) AS PERSON2 , "
                         "pr.KEYWORD "
                         "FROM PROJECT pr , PERSON pe , PERSON pe2 "
                         "WHERE pr.PJ_ID = " + projid +
                         " AND pr.PERSON_ID1 = pe.PERSON_ID AND pr.PERSON_ID2 = pe2.PERSON_ID")
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
      return redirect("/addproj")

@app.route('/addproj' , methods = ['GET' , 'POST'])
def addproj():
    try:
        data = request.get_json()
        st = strftime("%d%m%Y", gmtime())
        t1 = strftime("%H", gmtime())
        t2 = strftime("%M", gmtime())
        t3 = strftime("%S", gmtime())

        constrname = st + '_' + t1 + t2 + t3 + '.' + (data['pathpic'])

        conn = db_connect.connect()
        conn.execute("INSERT INTO PROJECT "
                     "(PJ_ID, "
                     "PJ_NAME, "
                     "PJ_YEAR, "
                     "PJTYPE_ID, "
                     "S_NAME1, "
                     "S_ID1, "
                     "S_NAME2,"
                     "S_ID2,"
                     "PERSON_ID1,"
                     "PERSON_ID2,"
                     "KEYWORD) "
                     "VALUES (PROJECT_SEQ.NEXTVAL, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11)",
                     (data["pName"], data["pYear"], data["pType"], data["sNameF"], data["sIdF"], data["sNameS"], data["sIdS"], data["profPrimary"], data["profSub"], data["keyword"]))

        conn.execute("INSERT INTO PROJECT_FILE "
                     "(PATH, "
                     "NAME, "
                     "PJ_ID) "
                     "(SELECT "+ constrname +", "+ constrname +", MAX(PJ_ID) FROM PROJECT)")

    except:
        conn.rollback()
    finally:
        conn.commit()
        conn.close()
        return json.dumps(data)



@app.route('/newsupdate' , methods = ['GET' , 'POST'])
def newsupdate():
    return  render_template("newsUpdate.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
