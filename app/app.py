from glob import glob
from dotenv import load_dotenv
from termcolor import colored

import numpy as np
import cv2
import face_recognition
import os, json

from init import createApp

app = createApp()
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.app_context().push()

import routes

if __name__=='__main__':
    app.run(host="0.0.0.0", port="5000", debug=True)