from glob import glob
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from termcolor import colored
from datetime import date

from Controllers.controller import Controller

import numpy as np, cv2, face_recognition, os, json, MySQLdb.cursors

app = Flask(__name__, template_folder='../resources/views', static_folder='../resources/static')
app.secret_key = 'JFIREOJGOTJFIODJBOIERPOYIERP'

controller = Controller()

config = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DB"]

for each in config:
    app.config[each] = os.getenv(each)

mysql = MySQL(app)

@app.route('/')
def dashboard():
    if "loggedin" in session:
        return render_template('dashboard.html', id=session['id'])
    
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if "loggedin" in session:
        return render_template('index.html', id=session['id'])
    
    return redirect(url_for('login'))

@app.route('/video_feed')
def video_feed():
    def find_user_by_id(id, limit=1):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = f"SELECT * FROM siswa WHERE siswa.id={id} LIMIT 1"
        cursor.execute(query)
        return cursor.fetchone()
    
    target = find_user_by_id(session['id'])

    return Response(controller.gen_frames(target=target), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = f"SELECT * FROM siswa WHERE (siswa.nama='{username}' OR siswa.id='{username}') AND siswa.password='{password}' LIMIT 1"
        cursor.execute(query)
        account = cursor.fetchone()
        
        if account:
            session['loggedin'], session['id'] = True, account['id']
            print('Logged in successfully!')
            return redirect(url_for("index"))
        else:
            print("Incorrect Username/Password")
    return render_template('login.html')

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   
   return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)