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

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
