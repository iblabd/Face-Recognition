import json
import os
import face_recognition

class Face:
    def __init__(self):
        pass
    
    def sync(self):
        IMAGEs = os.listdir("images/")
        SISWAs = [os.path.splitext(string)[0] for string in IMAGEs]
        
        with open("yamori.json") as JSON:
            JSON = json.load("yamori.json")
        
        differentiation = 0
        for name in SISWAs:
            if name not in JSON.keys():
                differentiation += 1
        
        if differentiation > 0:
            self.JSON.clear()
            self.JSON().write(faces.encode(path="images/"))
            
        
    def __encoding__(self, image):
        return face_recognition.face_encodings(image)[0].tolist()
    
    def encode(self, path=0, spesific=0):
        JSON = self.JSON().load()
        
        if path != 0 :
            SISWAs = os.listdir(path)
            SISWAs = [os.path.splitext(string)[0] for string in SISWAs]

        if spesific != 0:
            SISWAs = spesific
            
        images = {}
        image_face_encoding = {}

        print("initializing image_face_encoding . . .")        
        
        for nama_siswa in SISWAs:
            images[nama_siswa] = face_recognition.load_image_file(f"images/{nama_siswa}.jpg")
            print(f"{nama_siswa} loaded")
            
            print(f"encoding ... {nama_siswa} . . . this may take a while")

            if JSON != 0: # JSON NOT empty
                exist = nama_siswa in JSON.keys()
                
                if exist:
                    kirchoff = json.load(JSON)[nama_siswa]
                    print(f"{nama_siswa} passed due to already exist.")
                else:
                    kirchoff = self.__encoding__(images[nama_siswa])
                    print(f"face encoding on {nama_siswa}, completed")
            else:
                kirchoff = self.__encoding__(images[nama_siswa])
                print(f"face encoding on {nama_siswa}, completed")

        image_face_encoding[nama_siswa] = kirchoff
        return image_face_encoding
    
    class JSON:
        def __init__(self):
            pass
        def __intersection__(self):
            JSON = self.load().keys()
            DIR = os.listdir("images/")
            DIR = [os.path.splitext(string)[0] for string in DIR]
            
            changes = []
            
            if self.checkUpdates() == -1:
                # something deleted on DIR
                for each in JSON:
                    if each not in DIR:
                        changes.append(each)
            elif self.checkUpdates() == 1:
                # new element on DIR
                for each in DIR:
                    if each not in JSON:
                        changes.append(each)
                
            return changes
            
        def load(self):
            isEmpty = os.stat("yamori.json").st_size == 0
            
            if isEmpty:
                return 0
            else:
                with open("yamori.json") as JSON:
                    return json.load(JSON)
        
        def write(self, image_face_encoding):
            yamoriJSON = json.dumps(image_face_encoding)
            jsonFile = open("./yamori.json", "w")
            jsonFile.write(yamoriJSON)
            
            print("JSON writed")
            jsonFile.close()
            
        def clear(self):
            jsonFile = open("./yamori.json", "w").truncate(0)
            print("yamori.JSON successfully cleared")
            
        def checkUpdates(self):
            JSON = self.load().keys()
            JSON = list(JSON)
            JSON = len(JSON)
            
            DIR = os.listdir("images/")
            DIR = [os.path.splitext(string)[0] for string in DIR]
            DIR = len(DIR)
            
            changes = DIR-JSON
            
            if changes >= 1:
                return 1
            elif changes == 0:
                return 0
            else:
                return -1
            
        def update(self):
            if self.checkUpdates() == 0:
                print("No changes found")
            else:
                JSON = self.load()
                intersection = self.__intersection__()
                
                message = "-"
                
                if self.checkUpdates() == -1:
                    for each in intersection:
                        JSON.pop(each)
                    message = "Some elements were successfully deleted"
                elif self.checkUpdates() == 1:
                    for each in intersection:
                        JSON[each] = Face().encode(spesific=[each])[each]
                    message = "Inserted new elements to JSON"
                
                self.clear()
                JSON = dict( sorted(JSON.items(), key=lambda x: x[0].lower()) )
                self.write(JSON)
                
                print(message)
        
            
def main():
    faces = Face()

    while True:
        options = input(">>> What? [ encode , update, clear ]  ")
        if options == "encode":
            face_encode = faces.encode(path="images/")
            faces.JSON().write(face_encode)
        elif options == "update":
            faces.JSON().update()
            # print(faces.JSON().__intersection__())
            # for each in faces.JSON().__intersection__():
            #     print(type(each))
        elif options == "clear":
            faces.JSON().clear()
        elif options == "q":
            break

main()