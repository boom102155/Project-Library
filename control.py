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

@app.route('/projcontent' , methods = ['GET','POST'])
def projcontent():
    return render_template("projContent.html")

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

@app.route('/newsupdate' , methods = ['GET' , 'POST'])
def newsupdate():
    return  render_template("newsUpdate.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
