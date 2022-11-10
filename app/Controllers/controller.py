from dotenv import load_dotenv
from termcolor import colored

from datetime import date
from datetime import datetime
from flask import request

import sys, cv2, os, json, numpy as np
import face_recognition
import mysql.connector

from pathlib import Path
path = str(Path(f"{os.getcwd()}\\app")).replace("\\", "/")
sys.path.insert(0, path)
from Databases.firebase import Firebase

class Controller:
    null_datetime = "0000-00-00 00:00:00"
    def __init__(self): 
        self.app = Firebase()
    
    def datetime(self): 
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def insert(self, id, has_time_in, has_time_out):
        if has_time_in:
            if has_time_out:
                string = colored("^ This person had already made a presence", "blue")
                print(string)
            else:
                today = self.datetime().split(" ")[0]
            
                self.app.ref = self.app.reference("presence")
                presence = self.app.select_from("presence", [
                    ["time_in", "like", today],
                    ["student_id", id]
                ])[0]
                
                self.app.update(presence.id(), {
                    "time_out": self.datetime()
                })
                
        elif not has_time_out:
            self.app.ref = self.app.reference("presence")
            self.app.push({
                "student_id": id,
                "time_in": self.datetime(),
                "time_out": self.null_datetime,
                "reason": "",
                "status": ""
            })
            
    def has_time_in(self, target):
        today = self.datetime().split(" ")[0]
        
        self.app.ref = self.app.reference("presence")
        snap = self.app.select_from("presence", condition=[
            ["student_id", target],
            ["time_in", "LIKE", today],
            ["time_out", self.null_datetime]
        ])
        
        return len(snap) > 0
        
    def has_time_out(self, target):
        today = self.datetime().split(" ")[0]
        
        self.app.ref = self.app.reference("presensi")
        snap = self.app.select_from("presence", condition=[
            ["student_id", target],
            ["time_in", "LIKE", today],
            ["time_out", "NOT", self.null_datetime]    
        ])
        
        return len(snap) > 0
        
    def gen_frames(self, target=None):
        load_dotenv()

        video_capture = cv2.VideoCapture(0)
        video_capture.open(1)

        if not video_capture.isOpened():
            raise EnvironmentError("Camera failed to open")

        with open("yamori.json") as JSON:
            image_face_encoding = json.load(JSON)
            known_face_encodings = []
            
            for key, value in image_face_encoding.items():
                known_face_encodings.append(np.array(value))

        students = os.listdir("images/")
        known_face_names = [os.path.splitext(string)[0] for string in students if string != ".gitignore"]

        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            success, frame = video_capture.read()
            if not success:
                break
            else:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                rgb_small_frame = frame

                if process_this_frame:
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"

                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                        face_names.append(name)

                if len(face_names) != 0:
                    person = self.app.select_from("users", [
                        ["id", target["id"]]
                    ])[0]
                    
                    n = person.get('name')
                    print(f"Detected face: {face_names}, expected at least {n} in detected faces")
                    
                    if target != None:
                        if target["name"].upper() in face_names:
                        
                            has_time_in = self.has_time_in(target["id"])
                            has_time_out = self.has_time_out(target["id"])
                            
                            print(has_time_in, has_time_out)
                            self.insert(target["id"], has_time_in, has_time_out)
    
                            break
                    
                process_this_frame = not process_this_frame

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
               
             