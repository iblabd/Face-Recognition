from glob import glob
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from termcolor import colored
from datetime import datetime
import locale

from Controllers.controller import Controller
from Database.firebase import Record, Firebase

import numpy as np, cv2, face_recognition, os, json, MySQLdb.cursors

app = Flask(__name__, template_folder='../resources/views', static_folder='../resources/static')
app.secret_key = os.getenv("FLASK_SECRET_KEY")

controller = Controller()


@app.route('/', methods=["POST", "GET"])
def dashboard():
    if "loggedin" in session:
        # val["user_name"] = session['user']['name']
              
        def getStudentById(on_id):   
            return controller.app.select_from("users", [
                ["id", on_id]
            ])[0]
        def getStudentByName(on_name):
            return controller.app.select_from("users", [
                ["name", "LIKE", on_name]
            ])[0]
        def getStudentClass(on_id):
            return controller.app.select_from("class", [
                ["id", on_id]
            ])[0].get("name")

        result = []
        result_total = 0
        if request.method == 'POST' and 'studentSearch' in request.form:
            search_query  = request.form['studentSearch'].upper()
            
            if (search_query.isnumeric()):
                snap = controller.app.select_from("gate_presence", [
                ["student_id", int(search_query)]
            ])
            else:
                search_query = getStudentByName(search_query).get("id")

                snap = controller.app.select_from("gate_presence", [
                    ["student_id", int(search_query)]   
                ])

            for each in snap:
                student_id = each.get("student_id")
                student = getStudentById(student_id)
                try:
                    each.set("student_name", student.get("name"))
                    each.set("student_class", getStudentClass(student.get("class_id")))
                except:
                    print("Nothing while searching by id.")
                
                result.insert(0, each)
                result_total = len(result)

        else:
            snap = controller.app.reference("gate_presence").get()

            for key, val in snap.items():
                student_id = val["student_id"]
                val["student_name"] = getStudentById(student_id).get("name")
                val["student_class"] = getStudentClass(getStudentById(student_id).get("class_id"))
                res = {key: val}
                res = Record(res)
                result.insert(0, res)
                result_total = len(result)
        
        locale.setlocale(locale.LC_TIME, "id_ID")
        datenow = datetime.now()
        date = datenow.strftime("%d %B %Y")
        
        return render_template('dashboard.html', id=session['id'], result=result, user=session['user'], date=date, result_total=result_total)
    return redirect(url_for('login'))


    

@app.route('/index')
def index():
    if "loggedin" in session:
        return render_template('recog/index.html', id=session['id'])
    
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

@app.route('/add-siswa', methods=['GET', 'POST'])
def addSiswa():
    if request.method == 'POST':
        nis = request.form['nis']
        nama = request.form['name']
        email = request.form['email']
        kelas = request.form['kelas']
        password = request.form['password']
        telp = request.form['telp']

        try:
            controller.app.ref = controller.app.reference("users")
            controller.app.push({
                    "id": nis,
                    "name": nama,
                    "email": email,
                    "class_id": kelas,
                    "password": password,
                    "telp": telp
                })
            print("Done")
        except:
            print("Unknown error")

    kelas = controller.app.reference("class").get()
    result = []

    for key, val in kelas.items():
        val["id_kelas"] = val["id"]
        val["nama_kelas"] = val["name"]

        res = {key: val}
        res = Record(res)
        
        result.insert(0, res)

    return render_template('siswa/create_siswa.html', kelas=result)

@app.route('/list-siswa',  methods=['GET', 'POST'])
def listSiswa():
    
    def getStudentClass(on_id):
            return controller.app.select_from("class", [
                ["id", on_id]
            ])[0].get("name")
    
    result = []
    result_total = 0
    # if request.method == 'POST' and 'studentSearch' in request.form:
    #     search_query  = request.form['studentSearch'].upper()
            
    #     if (search_query.isnumeric()):
    #         snap = controller.app.select_from("users", [
    #         ["student_id", int(search_query)]
    #         ])
    #     else:
    #         search_query = getStudentByName(search_query).get("id")

    #         snap = controller.app.select_from("users", [
    #         ["student_id", int(search_query)]   
    #         ])

    #     for each in snap:
    #         id = each.get("id")
    #         student = getStudentsById(id)
    #         try:
    #             each.set("student_name", student.get("name"))
    #             each.set("student_class", getStudentClass(student.get("class_id")))
    #         except:
    #             print("Nothing while searching by id.")
                
    #         result.insert(0, each)
   
        
    
  
    snap = controller.app.reference("users").get()
    
    for key, val in snap.items():
            val["uid"] = key
            val["student_name"] = val["name"]
            val["student_class"] = getStudentClass(int(val["class_id"]))
            result.insert(0, val)
            result_total = len(result)

    return render_template('siswa/list_siswa.html', id=session['id'], result={0:result}, result_total=result_total, user=session['user'])

@app.route('/delete-siswa', methods=['POST'])
def deleteSiswa():
    uid = request.form.get("uid")
    try:
        controller.app.reference(f"users/{uid}").delete()
        return redirect("list-siswa")
    except:
        return "ERRRORRRRRRR"

@app.route('/add-kelas', methods=['GET', 'POST'])
def addKelas():
    if request.method == 'POST':
        nama = request.form['name']
        grade = request.form['grade']
        jurusan = request.form['jurusan']

        class_array = []
        snap = controller.app.reference("class").get()
        for key, val in snap.items():
            class_array.append(val)
        id = len(class_array) + 1

        try:
            controller.app.ref = controller.app.reference("class")
            controller.app.push({
                    "id": id,
                    "name": nama,
                    "grade": int(grade),
                    "field": jurusan
                })
            print("Done")
        except Exception:
            print("Error while storing to firebase.")

    return render_template('kelas/create_kelas.html')

@app.route('/list-kelas', methods=['GET', 'POST'])
def listKelas():
    
    result = []
    snap = controller.app.reference("class").get()

    result_total = 0
    
    for key, val in snap.items():
            val["uid"] = key
            result.insert(0, val)
            result_total = len(result)

    return render_template('kelas/list_kelas.html', result={0:result}, result_total=result_total)

@app.route('/delete-kelas', methods=['POST'])
def deleteKelas():
    uid = request.form.get("uid")
    try:
        controller.app.reference(f"class/{uid}").delete()
        return redirect("list-kelas")
    except:
        return "Error"

@app.route("/class/<uid>/edit", methods=["GET"])
def editKelas(uid):

    temp = controller.app.reference(f"class/{uid}").get()

    return render_template('kelas/edit_kelas.html', kelas=temp, uid=uid)

@app.route('/edit-kelas', methods=['POST'])
def pushEditKelas():
    uid = request.form.get("uid")

    id = request.form['id']
    nama = request.form['name']
    grade = request.form['grade']
    jurusan = request.form['jurusan']

    try:
        controller.app.ref = controller.app.reference("class")
        controller.app.update(uid, {
                "id": id,
                "name": nama,
                "grade": int(grade),
                "field": jurusan
            })
        return redirect(url_for('listKelas'))
    except Exception:
        return uid

@app.route("/students/<uid>/edit", methods=["GET"])
def editSiswa(uid):
    def getStudentClass(on_id):
            return controller.app.select_from("class", [
                ["id", on_id]
            ])[0].get("name")
    
    # if request.method == 'POST':
    #     nis = request.form.get('nis')
    #     nama = request.form.get('name')
    #     email = request.form.get('email')
    #     kelas = request.form.get('kelas')
    #     password = request.form.get('password')
    #     telp = request.form.get('telp')

    #     try:
    #         controller.app.ref = controller.app.reference("users")
    #         controller.app.update({
    #                 "id": nis,
    #                 "name": nama,
    #                 "email": email,
    #                 "class_id": kelas,
    #                 "password": password,
    #                 "telp": telp
    #             })
    #         print("Done")
    #     except:
    #         print("Unknown error")

    temp = controller.app.reference(f"users/{uid}").get()
    kelas = controller.app.reference("class").get()
    siswa = controller.app.reference("users").get()
    result = []

    for key, val in kelas.items():
        val["id_kelas"] = val["id"]
        val["nama_kelas"] = val["name"]

        res = {key: val}
        res = Record(res)
        
        result.insert(0, res)
    # return temp
    return render_template('siswa/edit_siswa.html', kelas=result, siswa=temp, uid=uid)

@app.route('/edit-siswa', methods=['POST'])
def pushEditSiswa():
    uid = request.form.get("uid")

    nis = request.form.get('nis')
    nama = request.form.get('name')
    email = request.form.get('email')
    kelas = request.form.get('kelas')
    password = request.form.get('password')
    telp = request.form.get('telp')

    try:
        controller.app.ref = controller.app.reference("users")
        controller.app.update(uid, {
                "id": nis,
                "name": nama,
                "email": email,
                "class_id": kelas,
                "password": password,
                "telp": telp
            })
        return redirect(url_for('listSiswa'))
    except:
        return "ERORRRRRRzzz"


    # for key, val in kelas.items():
    #     val["id_kelas"] = val["id"]
    #     val["nama_kelas"] = val["name"]

    #     res = {key: val}
    #     res = Record(res)
        
    #     result.insert(0, res)

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = 0
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        _hashed = controller.app.hash(password)
        
        account = controller.app.select_from("teacher", condition=[
            ["email", email],
            ["password", _hashed]
        ])
        
        if len(account) > 0:
            session['loggedin'] = True
            session['id'] = account[0].get("id")
            session["user"] = {
                                "name": account[0].get("name"),
                                "email": account[0].get("email")}
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