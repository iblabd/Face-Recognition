from termcolor import colored
from datetime import date, datetime
from dotenv import load_dotenv
from flask import request, redirect, url_for, abort, Response
from PIL import Image
import pendulum
import pyttsx3
import sys
import os
import json
import cv2
import face_recognition
import urllib
import numpy as np

from pathlib import Path
sys.path.insert(0, str(Path(f"{os.getcwd()}\\app")).replace("\\", "/"))
from Database.firebase import Firebase

class Controller:
    null_datetime = "0000-00-00 00:00:00"

    def __init__(self): 
        self.app = Firebase()
        self.currentdir  = os.getcwd()
    
    def datetime(self): 
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def say(self, say):
        tts = pyttsx3.init()
        tts.setProperty('voice', 'id-ID')
        tts.say(say)
        return tts.runAndWait()
    
    def insertIntoPresence(self, id):
        # - - - Status - - -
        # 0 -> No changes applied, most likely because had already made a presence
        # 1 -> Created new presence record with time_in today and null datetime for time_out
        # 2 -> Updated presence record with student_id = id on column time_out setted to current datetime
        has_time_in = self.has_time_in(id)
        has_time_out = self.has_time_out(id)

        timenow = self.datetime()
        today = timenow.split(" ")[0]
        latetime = today + " 07:01:00"

        reference_time = pendulum.parse(timenow)
        compare_time = pendulum.parse (latetime)
        
        
        if not has_time_in:
            self.app.ref = self.app.reference("gate_presence")
            
            if reference_time < compare_time:
                self.app.push({
                    "student_id": id,
                    "time_in": timenow,
                    "time_out": self.null_datetime,
                    "reason": "",
                    "status": 1
                })

            else:
                self.app.push({
                    "student_id": id,
                    "time_in": self.datetime(),
                    "time_out": self.null_datetime,
                    "reason": "",
                    "status": 7
                })
            print("Present has been stored to database.")
            return 1
            
        else: 
            message = "You had already made a presence today"
            self.say(message)
            print(message)
            return None
            
    def has_time_in(self, target):
        today = self.datetime().split(" ")[0]
        
        self.app.ref = self.app.reference("gate_presence")
        snap = self.app.select_from("gate_presence", [
            ["student_id", target]
        ])
        
        # Intersection method
        records = [each for each in snap if today in each.get("time_in")]
        return len(records) > 0
        
    def has_time_out(self, target):
        today = self.datetime().split(" ")[0]
        
        self.app.ref = self.app.reference("gate_presence")
        snap = self.app.select_from("gate_presence", [
            ["student_id", target]
        ])
        
        # Intersection method
        records = [each for each in snap if self.null_datetime not in each.get("time_out") and today in each.get("time_in")]
        
        return len(records) > 0
    
    def gen_frames(self, session, target=None):
        load_dotenv()

        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            raise EnvironmentError("Camera failed to open")
        
        video_capture.open(os.getenv("CAMERA_ADDRESS"))

        with open(os.getenv("YAMORI_JSON")) as JSON:
            image_face_encoding = json.load(JSON)
            known_face_encodings = []
            
            for key, value in image_face_encoding.items():
                known_face_encodings.append(np.array(value))

        students = os.listdir(os.getenv("IMAGE_PATH"))
        known_face_names = [os.path.splitext(string)[0] for string in students if string != ".gitignore"]
        print(f"Total student images: {len(known_face_names)}")

        face_locations = []
        face_encodings = []
        face_names = []
        students_face = []
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
                    for each in face_names:
                        if each != "Unknown":
                            person = self.app.select_from("users", [
                                ["id", int(each)]
                            ])[0]
                            students_face.append(each)
                            n = person.get("name").lower()
                            print(f"Detected face: {n}")
                        
                            if students_face.count(each) > 5:
                                print(students_face)
                                print(f"{n} face appear more than 5 times in list")
                                self.say(f"{n}, thank you for make presence today.")
                                self.insertIntoPresence(int(each))
                                students_face.clear()
                            
                process_this_frame = not process_this_frame

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
    def predict(self, expected, data_url=None):
        
        with open(os.getenv("YAMORI_JSON")) as jsonfile:
            image_face_encodings = json.load(jsonfile)
        
        predict_image = face_recognition.load_image_file(self.filename)
        
        expected_face_encoding = image_face_encodings[expected]
        
        # Convert it from type list to type ndarray, same as face_recognition.face_encodings(expected)[0]
        expected_face_encoding = [np.array(expected_face_encoding)]
        
        face_locations = face_recognition.face_locations(predict_image)

        print("Founded {} face(s).".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(predict_image, face_locations)
        
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(expected_face_encoding, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(expected_face_encoding, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = expected

            face_names.append(name)
        
        return expected in face_names