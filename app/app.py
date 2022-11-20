from glob import glob
from dotenv import load_dotenv
from termcolor import colored
from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
from Controllers.controller import Controller

import os, json
import numpy as np
import cv2
import face_recognition
import datetime

load_dotenv()

app = Flask(__name__, template_folder='../resources/views', static_folder='../resources/static')
app.secret_key = os.getenv("FLASK_SECRET_KEY")

controller = Controller()

@app.route("/")
def main():
    return redirect(url_for("index"))

@app.route('/index')
def index():
    if "loggedin" in session:
        if session['status'] == 0 or session['status'] == 1:
            return render_template('index.html', id=session['id'])
        else:
            return redirect(f"{url_for('after')}?s=2")
    
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and 'id' in request.args and 'w' in request.args:
        username = request.args['id']
        password = request.args['w']
        
        u_int = int(username)
        account = controller.app.select_from("users", condition=[
            ["id", u_int],
            ["password", password]
        ])
        
        if len(account) > 0:
            session['loggedin'] = True
            session['id'] = account[0].get("id")
            
            val = {
                "hasTimeIn" : controller.has_time_in(session['id']),
                "hasTimeOut" : controller.has_time_out(session['id'])
            }
            
            now = datetime.datetime.now()
            
            if val["hasTimeIn"] == 1 and val["hasTimeOut"] == 0:
                if now.hour >= 14 and now.hour <= 16:
                    status = session['status'] = 0
                else:
                    status = session['status'] = 1
            elif val["hasTimeOut"] == 1:
                status = session['status'] = 2
            else:
                status = session['status'] = 0
            
            _hashed = controller.app.hash(account[0].get("name"))
            controller.tempSession(_hashed, status)
        
            
            return redirect(url_for("index"))
        else:
            print("Incorrect Username/Password")
    return render_template("blank.html")

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('status', None)
   
   controller.tempSessionClear()
   
   return redirect(url_for('login'))

@app.route('/after', methods=["GET"])
def after():
    if request.args["s"] != "0":
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        session.pop('status', None)
    
    return render_template("after.html")

@app.route('/tempsession')
def tempsession():
    with open("tempSession.json") as tempSession:
        tempSession = json.load(tempSession)
        return jsonify(tempSession)

if __name__=='__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)