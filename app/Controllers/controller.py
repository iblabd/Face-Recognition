from dotenv import load_dotenv
from termcolor import colored

from datetime import date
from datetime import datetime
from flask import request

import cv2, os, json, numpy as np
import face_recognition
import mysql.connector

class Controller:
    null_datetime = "0000-00-00 00:00:00"
    def __init__(self): 
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="facerec",
            buffered=True
        )
        self.mycursor = self.mydb.cursor()
    
    def datetime(self): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def insert(self, id, has_time_in=False):
        if not has_time_in:
            query = f"INSERT INTO `presensi` (`id`, `siswa_id`, `time_in`, `time_out`, `alasan`, `status`) VALUES (NULL, {id}, '{self.datetime()}', 'NULL', NULL, NULL);"
        else:
            today = self.datetime().split(" ")[0]
            query = f"UPDATE presensi SET time_out='{self.datetime()}' WHERE siswa_id={id} AND time_in LIKE '{today}%'"
            
        self.mycursor.execute(query)
        self.mydb.commit()
        
    def has_time_in(self, target):
        today = self.datetime().split(" ")[0]
        query = f"SELECT * FROM presensi WHERE presensi.siswa_id={target} AND presensi.time_in LIKE '{today}%' AND presensi.time_out = '{self.null_datetime}'"
        
        self.mycursor.execute(query)
        self.mydb.commit()
        
        return not self.mycursor.fetchall() == []
        
    def has_time_out(self, target):
        today = self.datetime().split(" ")[0]
        query = f"SELECT * FROM presensi WHERE presensi.siswa_id={target} AND presensi.time_in LIKE '{today}%' AND NOT presensi.time_out = '{self.null_datetime}'"
        
        self.mycursor.execute(query)
        self.mydb.commit()
        
        return not self.mycursor.fetchall() == []
        
    def gen_frames(self, target=None):
        
        load_dotenv()

        video_capture = cv2.VideoCapture(0)
        video_capture.open(1)

        if not video_capture.isOpened():
            EnvironmentError("Camera failed to open")

        with open(os.getenv("YAMORI_JSON")) as JSON:
            image_face_encoding = json.load(JSON)
            known_face_encodings = []
            
            for key, value in image_face_encoding.items():
                known_face_encodings.append(np.array(value))

        students = os.listdir(os.getenv("IMAGE_PATH"))
        known_face_names = [os.path.splitext(string)[0] for string in students if string != ".gitignore"]

        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            print(self.datetime().split(" ")[0])
            success, frame = video_capture.read()  # read the camera frame
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
                    print(f"Detected face: {face_names}")
                    
                    if target != None:
                        if target["nama"].upper() in face_names:
                            
                            has_time_in, has_time_out = self.has_time_in(target["id"]), self.has_time_out(target["id"])
                            
                            if has_time_in and has_time_out:
                                string = colored("^ This person had already made a presence", "blue")
                                print(string)
                            else:
                                if not has_time_in and not has_time_out:
                                    status = "time_in"
                                elif has_time_in and not has_time_out :
                                    status = "time_out"
                                
                                self.insert(target["id"], has_time_in=has_time_in)
                                
                                name = colored(target["nama"].upper(), "green")
                                
                                print(f"{self.datetime} {name} done {status}")
    
                            break
                    
                process_this_frame = not process_this_frame

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
               
             