from dotenv import load_dotenv
from termcolor import colored

from datetime import date
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
            database="facerec"
        )
        
        self.today = date.today()
        self.datetime = self.today.strftime("%Y-%m-%d %H:%M:%S")
        
        self.mycursor = self.mydb.cursor()
    
    def has_time_in(self, target):
        today = self.datetime.split(" ")[0]
        query = f"SELECT * FROM presensi WHERE presensi.siswa_id={target}"
        query += f"AND presensi.time_in LIKE '{today}%'"
        
        self.mycursor.execute(query)
        self.mydb.commit()
        
        return mycursor.fetchall() == []
        
    def has_time_out(self, target):
        today = self.datetime.split(" ")[0]
        query = f"SELECT * FROM presensi WHERE presensi.siswa_id={target}"
        query += f"AND presensi.time_in LIKE '{today}%'"
        query += f"AND presensi.time_out = '{self.null_datetime}'"
        
        self.mycursor.execute(query)
        self.mydb.commit()
        
        return mycursor.fetchall() == []
        
    def gen_frames(self, target=None):
        load_dotenv()

        video_capture = cv2.VideoCapture(0)
        video_capture.open(os.getenv("CAMERA_ADDRESS"))

        if not video_capture.isOpened():
            print(colored("ERROR", "red", "Camera failed to open"))

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
                            
                            if self.has_time_out(target["id"]):
                                query = f"INSERT INTO `presensi` (`id`, `siswa_id`, `time_in`, `time_out`, `alasan`, `status`) VALUES (NULL, {target['id']}, '{datetime}', 'NULL', NULL, NULL);"
                                self.mycursor.execute(query)
                                self.mydb.commit()
                            
                            break
                    
                process_this_frame = not process_this_frame


                # # Display the results
                # for (top, right, bottom, left), name in zip(face_locations, face_names):
                #     # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                #     top *= 4
                #     right *= 4
                #     bottom *= 4
                #     left *= 4

                #     # Draw a box around the face
                #     cv2.rectangle(frame, (left, top), (right, bottom), (40, 167, 69), 2)

                #     # Draw a label with a name below the face
                #     cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (40, 167, 69), cv2.FILLED)
                #     font = cv2.FONT_HERSHEY_DUPLEX
                #     cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
               
             