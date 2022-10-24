from glob import glob
from flask import Flask, render_template, Response
from dotenv import load_dotenv
from termcolor import colored

import cv2
import face_recognition
import numpy as np
import os
import json

app = Flask(__name__, template_folder='../resources/views')

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

def gen_frames():
    global process_this_frame  
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
            process_this_frame = not process_this_frame


            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (40, 167, 69), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (40, 167, 69), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__=='__main__':
    app.run(debug=True)