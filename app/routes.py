from __main__ import app
from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
from Controllers.controller import Controller
import os, json

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
            ["password", controller.app.hash(password)]
        ])
        
        if len(account) > 0:
            session['loggedin'] = True
            session['id'] = account[0].get("id")
            val = {
                "hasTimeIn" : controller.has_time_in(session['id']),
                "hasTimeOut" : controller.has_time_out(session['id'])
            }
            
            if val["hasTimeIn"] and val["hasTimeOut"] == 0:
                status = session['status'] = 1
            elif val["hasTimeIn"] and val["hasTimeOut"] == 1:
                status = session['status'] = 2
            else:
                status = session['status'] = 0

            controller.tempSession(controller.app.hash(account[0].get("name")), status)
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
   
   return redirect(url_for('login'))

@app.route('/after', methods=["GET"])
def after():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('status', None)
    
    controller.tempSessionClear()
    
    return render_template("after.html")

@app.route('/tempsession')
def tempsession():
    with open("tempSession.json") as tempSession:
        tempSession = json.load(tempSession)
        return jsonify(tempSession)