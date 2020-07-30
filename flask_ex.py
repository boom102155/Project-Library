import os
from flask import Flask, render_template, jsonify, request, json , redirect, url_for, session, flash,send_from_directory
from datetime import datetime
from flask_cors import CORS
from werkzeug import utils
import cx_Oracle
from werkzeug.utils import secure_filename
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
from email.mime.base import MIMEBase
from email import encoders
import pdfkit
import glob
from zipfile import ZipFile

os.environ["NLS_LANG"] = ".UTF8"

sender_email = "karnkung@gmail.com"
password = "tongrule76"

FLASH = flash

UPLOAD_FOLDER = './PO'
app = Flask(__name__,
            static_folder = "./static",
            template_folder = "./templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '1234'
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

USER = 'meenple'
PASS = 'meenple'
DB_URL = '10.10.100.65:1521/usfm'
# DB_URL = '203.158.131.65:1521/usfm'


@app.route('/hello')
def hello():
    try:
        con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
        return (con.version)
    finally:
        con.close()

@app.route('/test')
def hello2():
    return render_template('blank.html')

@app.route('/vendor')
def vendor():
    if (session['UserType'] == 'HQ'):
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "select v.vendor_id, v.vendor_fname, v.vendor_lname, v.vendor_phone, "\
                  "v.vendor_address, v.vendor_province, v.vendor_postcode "\
                  "from vendor v"
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('tables-vendor.html', rows=rows, Username = session['Username'], UserType = session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/store')
def store():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "select s.store_id, s.store_fname, s.store_lname, s.store_phone, "\
                  "s.store_address, s.store_province, s.store_postcode "\
                  "from store s"
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('tables-store.html', rows=rows, Username = session['Username'], UserType = session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/product')
def product():
    if (session['UserType']=='HQ')| (session['UserType']=='STORE'):
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "SELECT p.prod_id, p.prod_name, p.prod_details, p.prod_grouping "\
                  "from product p"
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('tables-product.html', rows=rows, Username = session['Username'], UserType = session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/inpo')
def inpo():
    if (session['UserType'] == 'STORE') | (session['UserType'] == 'DIS'):
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "SELECT p.prod_id, p.prod_name, p.prod_details, p.prod_grouping "\
                  "from product p"
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('insert-PO.html', rows=rows, Username = session['Username'], UserType = session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/NOorder')
def NO_Order():
    if (session['UserType'] == 'HQ'):
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "select count(*) from purchase_order_Detail where vendor_id is null"
            cur.execute(sql)
            rows = cur.fetchall()
            check = 0
            for row in rows:
                check = row[0]
            if(check>0):
                flash("Select Vendors before send email")
                return redirect(url_for('Main_List'))

            sql = "SELECT id_po,store_id,date_po FROM no_order"

            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('table-NOorder.html', rows=rows, Username=session['Username'],UserType=session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/Email')
def email_btn():
    if (session['UserType'] == 'HQ'):
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = " select id_po , store_id , vendor_id,address,store_phone,vendor_email,vendor_address, " \
                  " store_name,vendor_name,total,date_po from emailtovendor "
            cur.execute(sql)
            rows = cur.fetchall()
            for head in rows:
                id_po = head[0]
                store_id = head[1]
                vendor_id = head[2]
                store_address = head[3]
                store_tel = head[4]
                vendor_email = head[5]
                vendor_address = head[6]
                store_name = head[7]
                vendor_name = head[8]
                total = head[9]
                date_po = head[10]
                sql = "select  prod_id , prod_name,amount,price,amount*price from prod_order_tovendor " \
                      "where id_po = '" + id_po + "' and vendor_id = '" + vendor_id + "' "
                cur.execute(sql)
                items = cur.fetchall()
                pdf_email = render_template('testemail.html', id_po=id_po, store_name=store_name, vendor_name=vendor_name,
                                            store_address=store_address, vendor_address=vendor_address, items=items,total=total
                                            ,date_po=date_po)
                pdf_name = id_po + '_' + vendor_id + '.pdf'
                pdf_path = os.path.join(UPLOAD_FOLDER,pdf_name)

                pdfkit.from_string(pdf_email, pdf_path)
                message = MIMEMultipart("alternative")
                # เขียน email
                message["Subject"] = "PURCHASE ORDER " + pdf_name
                message["From"] = sender_email
                message["To"] = vendor_email

                msg_detail = "เรียน ผู้ที่เกี่ยวข้องการจัดส่งใบสั่งซื้อสินค้า"
                part1 = MIMEText(msg_detail, "plain")
                message.attach(part1)

                # add file
                with open(pdf_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {pdf_name}",
                )

                message.attach(part)
                text = message.as_string()

                # ต่อ email และส่ง email
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(
                        sender_email, vendor_email, message.as_string()
                    )
                    server.quit()
            sql = "insert into receipt (receipt_id, store_id, date_get, id_po) " \
                  "select replace(id_po,'PO','R'), store_id, date_po +1, id_po " \
                  "from purchase_order " \
                  "where id_po in (select id_po from no_order) "
            print(sql)
            cur.execute(sql)

            sql = "insert into receipt_detail (receipt_id, prod_id) " \
                  "select replace(id_po, 'PO', 'R'), prod_id " \
                  "from purchase_order_detail " \
                  "where id_po in (select id_po from no_order)"
            print(sql)
            cur.execute(sql)
            sql = "UPDATE purchase_order SET order_status = 'Y'"
            print(sql)
            cur.execute(sql)
            con.commit()
            flash("Send EMAIL complete")
            return redirect(url_for('NO_Order'))
        except cx_Oracle.DatabaseError as e:
            return print('error')
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/restatus')
def status():
    if (session['UserType'] == 'STORE')| (session['UserType'] == 'HQ'):
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "SELECT receipt_id, date_get, re_status FROM re_status"
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('table-ReStatus.html', rows=rows, Username=session['Username'],UserType=session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/POlist')
def POlist():
    if (session['UserType'] == 'STORE')| (session['UserType'] == 'HQ'):
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "SELECT po.id_po, po.store_id, po.date_po, s.store_fname,order_status "\
                  "from purchase_order po "\
                  "inner join store s "\
                  "on po.store_id = s.store_id order by po.date_po desc"

            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('table-POlist.html', rows=rows, Username=session['Username'],UserType=session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/download_po/<id_po>')
def down_po(id_po):
    if (session['UserType'] == 'STORE')| (session['UserType'] == 'HQ'):
        listfiles = glob.glob('./PO/' + id_po + '*'+'.pdf')
        file_name = id_po + ".zip"
        file_path = os.path.join(UPLOAD_FOLDER,file_name)
        with ZipFile(file_path, "w") as newzip:
            for i in listfiles:
                newzip.write(i)
        return send_from_directory(directory=UPLOAD_FOLDER, filename=file_name)
    else:
        return redirect(url_for('error'))

@app.route('/receiptlist')
def receiptlist():
    if (session['UserType'] == 'DIS'):
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "select r.receipt_id, r.store_id, s.store_fname, r.date_get, r.id_po "\
                  "from receipt r "\
                  "inner join store s "\
                  "on r.store_id = s.store_id "
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('tables-receiptlist.html', rows=rows, Username=session['Username'],UserType=session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/shop')
def shop():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "select v.vendor_id, v.vendor_fname, v.vendor_lname, v.vendor_phone, "\
                  "p.prod_id, p.prod_name, sp.prod_price "\
                  "from vendor v "\
                  "inner join sale_product sp "\
                  "on v.vendor_id = sp.vendor_id "\
                  "inner join product p "\
                  "on p.prod_id = sp.prod_id"
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('tables-shop.html', rows=rows, Username = session['Username'], UserType = session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/receipt')
def receipt():
    if session['UserType'] == 'DIS':
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "select r.receipt_id, r.store_id, r.date_get, "\
                  "po.id_po, po.date_po "\
                  "from receipt r "\
                  "inner join purchase_order po "\
                  "on r.id_po = po.id_po "
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('tables-receipt.html', rows=rows, Username = session['Username'], UserType = session['UserType'])

        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/inrepo/<receiptID>')
def inrepo(receiptID):
    if session['UserType'] == 'DIS':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "select p.prod_id, p.prod_name, rd.receipt_id, pd.amount, rd.amount_receipt, rownum "\
                  "from purchase_order_detail pd "\
                  "inner join receipt_detail rd "\
                  "on pd.prod_id = rd.prod_id "\
                  "inner join purchase_order po "\
                  "on po.id_po = pd.id_po "\
                  "inner join receipt r "\
                  "on r.receipt_id = rd.receipt_id "\
                  "inner join product p "\
                  "on p.prod_id = rd.prod_id "\
                  "where po.id_po = r.id_po "\
                  "and rd.receipt_id = '"+receiptID+"'"
            print(sql)
            cur.execute(sql)
            rows = cur.fetchall()

            sql = "select r.receipt_id, r.store_id, to_char(r.date_get,'yyyy-mm-dd'), r.id_po,s.store_fname "\
                  " from receipt r INNER JOIN store  s ON r.store_id = s.store_id"\
                  " where r.receipt_id = '"+receiptID+"'"
            cur.execute(sql)
            rows2 = cur.fetchall()

            result = {}
            for row in rows2:
                result['ReceiptID'] = row[0]
                result['StoreID'] = row[1]
                result['DateGet'] = row[2]
                result['IDPO'] = row[3]
                result['store_fname'] = row[4]
            return render_template('insert-REPO.html', rows=rows,data=result, Username = session['Username'], UserType = session['UserType'])

        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/order/<ID>')
def order(ID):
    if (session['UserType'] == 'HQ')|(session['UserType'] == 'STORE'):
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "SELECT p.prod_id, p.prod_name, p.prod_details, p.prod_grouping, pd.amount "\
                  "from  purchase_order_detail pd "\
                  "inner join product p "\
                  "on pd.prod_id = p.prod_id "\
                  "where pd.id_po = '"+ID+"' "
            cur.execute(sql)
            rows = cur.fetchall()

            return render_template('tables-order.html', rows=rows, Username = session['Username'], UserType = session['UserType'])

        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/invendor')
def vendor2():
    return render_template('insert-vendor.html', Username = session['Username'], UserType = session['UserType'])

@app.route('/invendor/post', methods=['POST'])
def vendor2_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "INSERT INTO vendor ("\
                  "vendor_fname, "\
                  "vendor_lname, "\
                  "vendor_phone, "\
                  "vendor_address, "\
                  "vendor_province,"\
                  "vendor_postcode "\
                  ")VALUES ( "\
                  "'"+request.form['InputFirstName']+"', "\
                  "'"+request.form['InputLastName']+"', "\
                  "'"+request.form['InputPhone']+"', "\
                  "'"+request.form['InputAddress']+"', "\
                  "'"+request.form['InputProvince']+"', "\
                  "'"+request.form['InputPostcode']+"' "\
                  ")"
            print(sql)
            cur.execute(sql)
            con.commit()

            # return render_template('insert-vendor.html', Username = session['Username'], UserType = session['UserType'])
            return redirect(url_for('vendor'))
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upvendor/<ID>')
def vendor4(ID):
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "SELECT  "\
                  "v.vendor_id, " \
                  "v.vendor_fname," \
                  "v.vendor_lname," \
                  "v.vendor_phone," \
                  "v.vendor_address," \
                  "v.vendor_province," \
                  "v.vendor_postcode "\
                  "from  vendor v "\
                  "WHERE vendor_id = '"+ID+"' "
            cur.execute(sql)
            rows = cur.fetchall()
            result = {}
            for row in rows:
                result['vendor_id'] = row[0]
                result['vendor_fname'] = row[1]
                result['vendor_lname'] = row[2]
                result['vendor_phone'] = row[3]
                result['vendor_address'] = row[4]
                result['vendor_province'] = row[5]
                result['vendor_postcode'] = row[6]
            return render_template('update-vendor.html',data=result, Username = session['Username'], UserType = session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upvendor')
def vendor3():
    return render_template('insert-vendor.html')

@app.route('/upvendor/post', methods=['POST'])
def vendor3_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "UPDATE vendor " \
                  "SET " \
                  "vendor_fname = '"+request.form['InputFirstName']+"', " \
                  "vendor_lname = '"+request.form['InputLastName']+"', " \
                  "vendor_phone = '"+request.form['InputPhone']+"', " \
                  "vendor_address = '"+request.form['InputAddress']+"', " \
                  "vendor_province = '"+request.form['InputProvince']+"', " \
                  "vendor_postcode = '"+request.form['InputPostcode']+"' " \
                  "WHERE " \
                  "vendor_id = '"+request.form['InputID']+"' "
            print(sql)
            cur.execute(sql)
            con.commit()

            # return render_template('insert-vendor.html', Username = session['Username'], UserType = session['UserType'])
            return redirect(url_for('vendor'))
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/instore')
def store2():
    return render_template('insert-store.html', Username = session['Username'], UserType = session['UserType'])

@app.route('/instore/post', methods=['POST'])
def store2_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "INSERT INTO store (" \
                  "store_id ," \
                  "store_fname ," \
                  "store_lname , " \
                  "store_phone , " \
                  "store_address ," \
                  "store_province ," \
                  "store_postcode" \
                  ")VALUES (" \
                  "'"+request.form['InputID']+"', "\
                  "'"+request.form['InputFirstName']+"', "\
                  "'"+request.form['InputLastName']+"', "\
                  "'"+request.form['InputPhone']+"', "\
                  "'"+request.form['InputAddress']+"', "\
                  "'"+request.form['InputProvince']+"', "\
                  "'"+request.form['InputPostcode']+"' "\
                  ")"
            print(sql)
            cur.execute(sql)
            con.commit()

            # return render_template('insert-store.html', Username = session['Username'], UserType = session['UserType'])
            return redirect(url_for('store'))
        except cx_Oracle.DatabaseError as e:
           con.rollback()
        finally:
          cur.close()
          con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upstore/<ID>')
def store4(ID):
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "SELECT  "\
                  "s.store_id, " \
                  "s.store_fname," \
                  " s.store_lname," \
                  " s.store_phone," \
                  " s.store_address," \
                  " s.store_province," \
                  " s.store_postcode "\
                  "from store s "\
                  "WHERE store_id = '"+ID+"' "
            cur.execute(sql)
            rows = cur.fetchall()
            result = {}
            for row in rows:
                result['store_id'] = row[0]
                result['store_fname'] = row[1]
                result['store_lname'] = row[2]
                result['store_phone'] = row[3]
                result['store_address'] = row[4]
                result['store_province'] = row[5]
                result['store_postcode'] = row[6]
            return render_template('update-store.html',data=result, Username = session['Username'], UserType = session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upstore/post', methods=['POST'])
def store3_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "UPDATE store "\
                  "SET "\
                  "store_fname = '"+request.form['InputFirstName']+"',  "\
                  "store_lname = '"+request.form['InputLastName']+"', "\
                  "store_phone = '"+request.form['InputPhone']+"', "\
                  "store_address = '"+request.form['InputAddress']+"', "\
                  "store_province = '"+request.form['InputProvince']+"', "\
                  "store_postcode = '"+request.form['InputPostcode']+"' "\
                  "WHERE "\
                  "store_id = '"+request.form['InputID']+"' "
            print(sql)
            cur.execute(sql)
            con.commit()

            # return render_template('insert-store.html', Username = session['Username'], UserType = session['UserType'])
            return redirect(url_for('store'))
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
          cur.close()
          con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upmainlist/<ID>')
def upmainlist1(ID):
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "select v.vendor_id,v.vendor_id|| ' ' || v.vendor_lname || ' ราคา ' || S.prod_price" \
                  " from sale_product S inner JOIN vendor V on S.vendor_id = V.vendor_id" \
                  " where prod_id = '"+ID+"'"
            cur.execute(sql)
            vens = cur.fetchall()

            sql = "SELECT prod_id, prod_name, prod_weight, prod_details, prod_grouping, amount, vendor_id" \
                  " from con_vendor " \
                  " where prod_id = '"+ID+"' "
            cur.execute(sql)
            rows = cur.fetchall()
            result = {}
            for row in rows:
                result['prod_id'] = row[0]
                result['prod_name'] = row[1]
                result['prod_weight'] = row[2]
                result['prod_details'] = row[3]
                result['prod_grouping'] = row[4]
                result['amount'] = row[5]
                result['vendor_id'] = row[6]
        finally:
            cur.close()
            con.close()

        return render_template('update-Mainlist.html', data=result , vens=vens, Username = session['Username'], UserType = session['UserType'])
    else:
        return redirect(url_for('error'))

@app.route('/upmainlist/post', methods=['POST'])
def upmainlist2_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "update purchase_order_detail set vendor_id = '"+request.form['vendor_id']+"' " \
                  " where prod_id = '"+request.form['prod_id']+"' and id_po in (select id_po from no_order)"

            print(sql)
            cur.execute(sql)
            con.commit()

            return redirect(url_for('Main_List'))
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
          cur.close()
          con.close()
    else:
        return redirect(url_for('error'))

@app.route('/inproduct')
def product2():
    return render_template('insert-product.html', Username = session['Username'], UserType = session['UserType'])

@app.route('/inproduct/post', methods=['POST'])
def product2_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "INSERT INTO product ( "\
                  "prod_id, " \
                  "prod_name, " \
                  "prod_details, " \
                  "prod_grouping" \
                  ")VALUES ( "\
                  "'"+request.form['InputID']+"', "\
                  "'"+request.form['InputName']+"', "\
                  "'"+request.form['InputDetail']+"', "\
                  "'"+request.form['InputGrouping']+"' "\
                  ")"
            print(sql)
            cur.execute(sql)
            con.commit()

            # return render_template('insert-product.html', Username = session['Username'], UserType = session['UserType'])
            return redirect(url_for('product'))
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upproduct/<ID>')
def product4(ID):
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            sql = "SELECT  "\
                  "p.prod_id, " \
                  "p.prod_name," \
                  "p.prod_weight," \
                  "p.prod_details," \
                  "p.prod_grouping "\
                  "from product p "\
                  "WHERE prod_id = '"+ID+"' "
            print(sql)
            cur.execute(sql)
            rows = cur.fetchall()
            result = {}
            for row in rows:
                result['prod_id'] = row[0]
                result['prod_name'] = row[1]
                result['prod_weight'] = row[2]
                result['prod_details'] = row[3]
                result['prod_grouping'] = row[4]
            return render_template('update-product.html',data=result, Username = session['Username'], UserType = session['UserType'])
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upproduct')
def product3():
    return render_template('insert-product.html')

@app.route('/upproduct/post', methods=['POST'])
def product3_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "UPDATE product "\
                  "SET "\
                  "prod_name = '"+request.form['InputName']+"', "\
                  "prod_weight = '"+request.form['InputLastWeight']+"', "\
                  "prod_details = '"+request.form['InputDetail']+"', "\
                  "prod_grouping = '"+request.form['InputGrouping']+"' "\
                  "WHERE "\
                  "prod_id = '"+request.form['InputID']+"' "
            print(sql)
            cur.execute(sql)
            con.commit()

            # return render_template('insert-product.html', Username = session['Username'], UserType = session['UserType'])
            return redirect(url_for('product'))
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/inshop')
def shop2():
    return render_template('insert-shop.html', Username = session['Username'], UserType = session['UserType'])

@app.route('/inshop/post', methods=['POST'])
def shop2_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "INSERT INTO vendor (" \
                  "vendor_id, "\
                  "vendor_fname, "\
                  "vendor_lname, "\
                  "vendor_phone, "\
                  "vendor_province, "\
                  "prod_id, "\
                  "prod_price, "\
                  "prod_name, "\
                  "prod_weight, "\
                  "prod_details, "\
                  "prod_grouping "\
                  ")VALUES ( "\
                  "'"+request.form['InputVendorID']+"', "\
                  "'"+request.form['InputFirstName']+"', "\
                  "'"+request.form['InputLastName']+"', "\
                  "'"+request.form['InputPhone']+"', "\
                  "'"+request.form['InputProvince']+"', "\
                  "'"+request.form['InputProdID']+"', "\
                  "'"+request.form['InputProdPrice']+"', "\
                  "'"+request.form['InputProdName']+"', "\
                  "'"+request.form['InputProdWeight']+"', "\
                  "'"+request.form['InputProdDetail']+"', "\
                  "'"+request.form['InputProdGrouping']+"' "\
                  ")"
            print(sql)
            cur.execute(sql)
            con.commit()

            # return render_template('insert-shop.html', Username = session['Username'], UserType = session['UserType'])
            return redirect(url_for('shop'))
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upshop')
def shop3():
    return render_template('insert-shop.html')

@app.route('/upshop/post', methods=['POST'])
def shop3_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "UPDATE vendor " \
                  "SET "\
                  "vendor_fname = '"+request.form['InputFirstName']+"', "\
                  "vendor_lname = '"+request.form['InputLastName']+"', "\
                  "vendor_phone = '"+request.form['InputPhone']+"', "\
                  "vendor_province = '"+request.form['InputProvince']+"', "\
                  "prod_id = '"+request.form['InputProdID']+"', "\
                  "prod_price = '"+request.form['InputProdPrice']+"', "\
                  "prod_name = '"+request.form['InputProdName']+"', "\
                  "prod_weight = '"+request.form['InputProdWeight']+"', "\
                  "prod_details = '"+request.form['InputProdDetail']+"', "\
                  "prod_grouping = '"+request.form['InputProdGrouping']+"' "\
                  "WHERE "\
                  "vendor_id = '"+request.form['InputVendorID']+"' "
            print(sql)
            cur.execute(sql)
            con.commit()

            return render_template('insert-shop.html', Username = session['Username'], UserType = session['UserType'])
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/inreceipt')
def receipt2():
    return render_template('insert-receipt.html')

@app.route('/inreceipt/post', methods=['POST'])
def receipt2_post():
    if session['UserType'] == 'DIS':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            result = request.get_json()
            print(result[0])
            for detail in result[1]['detail']:
                qty = '0'
                if (detail['QTY']):
                    qty = '1'
                else:
                    qty = '0'
                sql = "UPDATE receipt_detail "\
                  "set amount_receipt = '"+qty+"' "\
                  "WHERE "\
                  "receipt_id = '"+result[0]+"' "\
                  "and prod_id = '"+detail['ItemID']+"' "
                print(sql)
                cur.execute(sql)

            sql = "UPDATE receipt set s_alert = 'Y', HQ_alert ='Y' " \
                  "where receipt_id = '" + result[0] + "' "
            print(sql)
            cur.execute(sql)

            print(result)
            con.commit()

            return redirect(url_for('receiptlist'))
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/upreceipt')
def receipt3():
    return render_template('insert-receipt.html')


@app.route('/upreceipt/post', methods=['POST'])
def receipt3_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "UPDATE receipt "\
                  "SET "\
                  "store_id = '"+request.form['InputStoreID']+"', "\
                  "date_po  = '"+request.form['InputDatePO']+"', "\
                  "date_get = '"+request.form['InputDateGet']+"', "\
                  "id_po = '"+request.form['InputIDPO']+"', "\
                  "prod_id = '"+request.form['InputProdID']+"', "\
                  "amount_receipt = '"+request.form['InputAmountReceipt']+"' "\
                  "WHERE "\
                  "receipt_id = '"+request.form['InputReceiptID']+"' "
            print(sql)
            cur.execute(sql)
            con.commit()

            return render_template('insert-receipt.html', Username = session['Username'], UserType = session['UserType'])
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/inorder')
def order2():
    return render_template('insert-order.html', Username = session['Username'], UserType = session['UserType'])

@app.route('/inorder/post', methods=['POST'])
def order2_post():
    if (session['UserType'] == 'HQ')|( session['UserType'] == 'STORE'):
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            now = datetime.now()
            #dd/mm/YY H:M:S
            dt_string = now.strftime("%d%m%Y%H%M%S")
            po_no ='PO'+str(dt_string)
            sql = "INSERT INTO purchase_order ("\
                  "store_id, "\
                  "date_po "\
                  ")values( "\
                  "'"+session['Detail']+"', "\
                  "sysdate "\
                  ")"
            print(sql)
            cur.execute(sql)
            result = request.get_json()
            for detail in result[1]['detail']:
                sql = "INSERT INTO purchase_order_detail ( "\
                  "prod_id, "\
                  "amount "\
                  ")values( "\
                  "'"+detail['ItemID']+"', "\
                  "'"+detail['QTY']+"' "\
                  ")"
                print(sql)
                cur.execute(sql)
            print(result)
            con.commit()

            return render_template('insert-order.html', Username = session['Username'], UserType = session['UserType'])
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/uporder')
def order3():
    return render_template('insert-order.html')

@app.route('/uporder/post', methods=['POST'])
def order3_post():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "UPDATE purchase_order  "\
                  "SET "\
                  "store_id = '"+request.form['InputStoreID']+"', "\
                  "date_po = '"+request.form['InputDatePO']+"', "\
                  "prod_id = '"+request.form['InputProdID']+"', "\
                  "amount = '"+request.form['InputAmount']+"', "\
                  "prod_name = '"+request.form['InputProdName']+"', "\
                  "prod_weight = '"+request.form['InputProdWeight']+"', "\
                  "prod_details = '"+request.form['InputProdDetail']+"', "\
                  "prod_grouping = '"+request.form['InputProdGrouping']+"', "\
                  "store_fname = '"+request.form['InputStoreFirstName']+"', "\
                  "store_lname =  '"+request.form['InputStoreLastName']+"', "\
                  "store_phone =  '"+request.form['InputStorePhone']+"', "\
                  "store_province = '"+request.form['InputStoreProvince']+"' "\
                  "WHERE "\
                  "id_po = '"+request.form['InputIDPO']+"', "
            print(sql)
            cur.execute(sql)
            con.commit()

            return render_template('insert-order.html', Username = session['Username'], UserType = session['UserType'])
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/select')
def select():
    try:
        con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
        cur = con.cursor()
        sql = "select * from test1"
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print (row)
        return (con.version)
    finally:
        cur.close()
        con.close()

@app.route('/insert')
def insert():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER+'/'+PASS+'@'+DB_URL)
            cur = con.cursor()
            data = {'ID':'01','NAME':'TEST'}
            sql = "insert into test1"   \
                  "     (ID,"           \
                  "     NAME)"          \
                  "     values (       "\
                  "'"+data['ID']+"',   "\
                  "'"+data['NAME']+"'"  \
                  ")"
            print(sql)
            cur.execute(sql)
            con.commit()
            return('True')
        except cx_Oracle.DatabaseError as e:
            con.rollback()
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/Mainlist')
def Main_List():
    if session['UserType'] == 'HQ':
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "SELECT prod_id, prod_name, prod_details, prod_grouping, amount, vendor_id from con_vendor"
            cur.execute(sql)
            rows = cur.fetchall()
            return render_template('/Mainlist.html', rows=rows, Username = session['Username'], UserType = session['UserType'])
            for row in rows:
                print(row)
                return (con.version)
        finally:
            cur.close()
            con.close()
    else:
        return redirect(url_for('error'))

@app.route('/')
def home():
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
        password = request.form['password']
        username = request.form['username']
        result = {}
        try:
            con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
            cur = con.cursor()
            sql = "select USERTYPE, USERNAME, Detail " \
                  "from (" \
                  "select USERTYPE, USERNAME , Detail " \
                  "from USERTABLE " \
                  "where USERNAME = '"+username+"'and PASS = '"+password+"'" \
                  "union SELECT 'x','Not login','' " \
                  "from dual)" \
                  "where rownum = 1"
            print(sql)
            cur.execute(sql)
            rows = cur.fetchall()

            for row in rows:
                result['UserType'] = row[0]
                result['Username'] = row[1]
                result['Detail'] = row[2]
        finally:
            cur.close()
            con.close()
        if result['Username'] == username:
            session['UserType'] = result['UserType']
            session['Username'] = result['Username']
            session['Detail'] = result['Detail']
            if  session['UserType'] == 'HQ':
                return redirect(url_for('MainHQ'))
            elif session['UserType'] == 'STORE':
                return redirect(url_for('MainSTORE'))
            elif session['UserType'] == 'DIS':
                return redirect(url_for('MainDIS'))

        else:
            flash("Username or Password incorrect")
            return redirect(url_for('home'))


@app.route('/MainHQ')
def MainHQ() :
    try:
        con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
        cur = con.cursor()
        sql = "select receipt_id ||' '|| re_status as text from re_status where receipt_id in ( select receipt_id from receipt where HQ_alert ='Y')"
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        sql = "update receipt set HQ_alert='N' where receipt_id in ( select receipt_id from receipt where HQ_alert ='Y')"
        cur.execute(sql)
        # ใช้จริงค่อยเอาcommnet ออก
        con.commit()
    finally:
        cur.close()
        con.close()
    if(len(rows)!=0):
        flash("text")
    return render_template('MainHQ.html', Username=session['Username'], UserType=session['UserType'],rows=rows)

@app.route('/MainSTORE')
def MainSTORE() :
    try:
        con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
        cur = con.cursor()
        #  แก้ query ตรงนี้
        sql = " select receipt_id ||' '|| re_status ||' '|| date_get  as text from re_status where receipt_id in ( select receipt_id from receipt where HQ_alert ='Y')"
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        sql = "update receipt set s_alert='N' where receipt_id in ( select receipt_id from receipt where s_alert ='Y')"
        cur.execute(sql)
        con.commit()
    finally:
        cur.close()
        con.close()
    if(len(rows)!=0):
        flash("text")
    return render_template('MainSTORE.html', Username=session['Username'], UserType=session['UserType'],rows=rows)

# @app.route('/MainSTORE')
# def MainSTORE() :
#     return render_template('MainSTORE.html', Username=session['Username'], UserType=session['UserType'])

@app.route('/MainDIS')
def MainDIS() :
    return render_template('MainDIS.html', Username=session['Username'], UserType=session['UserType'])

@app.route('/logout')
def logout() :
    session.clear()
    return redirect(url_for('home'))

@app.route('/404')
def page():
    return render_template('/404.html')

@app.route('/error')
def error():
    return render_template('/404.html',Username=session['Username'])

@app.route('/uploader', methods = ['POST'])
def upload_file():
   if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        with open(f.filename) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                try:
                    con = cx_Oracle.connect(USER + '/' + PASS + '@' + DB_URL)
                    cur = con.cursor()
                    sql = "UPDATE sale_product " \
                          "SET " \
                          "vendor_id = '"+row[0]+"', " \
                          "prod_price = '"+row[2]+"' " \
                          "WHERE " \
                          "prod_id = '"+row[1]+"' "
                    print(sql)
                    cur.execute(sql)
                    con.commit()
                except cx_Oracle.DatabaseError as e:
                    con.rollback()

        return redirect(url_for('shop'))

if __name__ == "__main__":
    # reload(sys)
    # sys.setdefaultencoding('utf-8')
    app.run(debug=True)
    # app.run(host = '0.0.0.0',port=5000)