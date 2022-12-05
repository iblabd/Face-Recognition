from glob import glob
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from termcolor import colored
from datetime import date

from Controllers.controller import Controller

import numpy as np, cv2, face_recognition, os, json, MySQLdb.cursors

app = Flask(__name__, template_folder='../resources/views', static_folder='../resources/static')
app.secret_key = os.getenv("FLASK_SECRET_KEY")

controller = Controller()

@app.route('/')
def dashboard():
    if "loggedin" in session:
        # presence_history = controller.app.reference("gate_presence").get()
        # x = controller.app.select_from("gate_presence")
        # student_id = x.get("student_id")  
        def getStudentName(on_id):
            return app.select_from("users", [
                ["id", on_id]
            ])[0].get("name")
            
        snap = controller.app.reference("gate_presence").get()

        result = []
        for key, val in snap.items():
            student_id = val["student_id"]
            val["student_name"] = getStudentName(student_id)
            
            res = {key: val}
            res = Record(res)
            result.append(res)
            
        def getStudentClass(on_id):
            return app.select_from("class", [
                ["id", on_id]
            ])[0].get("name")
                
        snap = controller.app.reference("users").get()

        result = []
        for key, val in snap.items():
            class_id = val["class_id"]
            val["class_name"] = getStudentClass(class_id)
                
            res = {key: val}
            res = Record(res)
            result.append(res)
        return render_template('dashboard.html', id=session['id'], student=result)
    return redirect(url_for('login'))

for each in result:
    each.show()
    

@app.route('/index')
def index():
    if "loggedin" in session:
        return render_template('index.html', id=session['id'])
    
    return redirect(url_for('login'))

@app.route('/video_feed')
def video_feed():

    def userOnId(id):
        snap = controller.app.select_from("users", [
            ["id", id]
        ])

        return snap[0].get()
    
    target = userOnId(session['id'])
    
    return Response(
        controller.gen_frames(session=session, target=target), 
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/verif')
def verif():
    if "loggedin" in session:
        return render_template('verification.html', id=session['id'])
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = 0
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        account = controller.app.select_from("teacher", condition=[
            ["email", email],
            ["password", password]
        ])
        
        if len(account) > 0:
            session['loggedin'] = True
            session['id'] = account[0].get("id")
            print('Logged in successfully!')
            return redirect(url_for("dashboard"))
        else:
            msg = "Incorrect username or password"
            print(msg)
            return render_template('login.html', msg = msg)
        
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   
   return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)