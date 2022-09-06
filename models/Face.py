import json
import os
import face_recognition

class Face:
    def __init__(self):
        pass
        
    def encode(self):
        SISWAs = os.listdir("images/")
        SISWAs = [os.path.splitext(string)[0] for string in SISWAs]
        images = {}
        image_face_encoding = {}

        print("initializing image_face_encoding . . .")

        for nama_siswa in SISWAs:
            images[nama_siswa] = face_recognition.load_image_file(f"images/{nama_siswa}.jpg")
            print(f"{nama_siswa} loaded")
            
            print(f"encoding ... {nama_siswa} . . . this may take a while")
            
            #if
            image_face_encoding[nama_siswa] = face_recognition.face_encodings(images[nama_siswa])[0].tolist()
            print(f"face_encoding on {nama_siswa}, completed")
    
        return image_face_encoding
    
    def JSONwrite(self,image_face_encoding):
        yamoriJSON = json.dumps(image_face_encoding)
        jsonFile = open("./yamori.json", "w")
        jsonFile.write(yamoriJSON)
        jsonFile.close()
    def clearJSON(self):
        jsonFile = open("./yamori.json", "w").truncate(0)
        print("yamori.JSON successfully cleared")

faces = Face()

while True:
    options = input(">>> What? (encode,clear):")
    if options == "encode":
        faces.JSONwrite(faces.encode())
    elif options == "clear":
        faces.clearJSON()
    elif options == "q":
        break