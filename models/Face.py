import json
import os
import face_recognition
from termcolor import colored

class Face:
    def __init__(self):
        pass
        
    def __encoding__(self, image):
        return face_recognition.face_encodings(image)[0].tolist()
    
    def encode(self, path=0, spesific=0):
        JSON = self.JSON().load()
        
        if path != 0 :
            students = os.listdir(path)
            
            if(".gitignore" in students):
                students.remove(".gitignore")
                
            students = [os.path.splitext(string)[0] for string in students]

        if spesific != 0:
            students = spesific
            
        images = {}
        image_face_encoding = {}

        print(colored("INITIALIZING ", "cyan"), "image_face_encoding ...")        
        
        for student_name in students:
            images[student_name] = face_recognition.load_image_file(f"images/{student_name}.jpg")
            print(f"{student_name} loaded")
            
            print(colored("ENCODING ", "blue"), f"{student_name} ...")

            if JSON != 0: # JSON NOT empty
                exist = student_name in JSON.keys()
                
                if exist:
                    kirchoff = self.JSON().load()[student_name]
                    print(colored("PASSED ( already exist )", "green"))
                else:
                    kirchoff = self.__encoding__(images[student_name])
                    print(colored("SUCCESSFULLY ENCODED", "green"))
            else:
                kirchoff = self.__encoding__(images[student_name])
                print(colored("SUCCESSFULLY ENCODED", "green"))

            image_face_encoding[student_name] = kirchoff
        
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
            yamoriJSON = json.dumps(image_face_encoding, indent=4)
            jsonFile = open("./yamori.json", "w")
            jsonFile.write(yamoriJSON)
            jsonFile.close()
            print("YAMORI.JSON", colored("changes has been written", "green"))
            
        def clear(self):
            jsonFile = open("./yamori.json", "w").truncate(0)
            print("YAMORI.JSON ", colored("clearly truncated", "red"))
            
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
                count = len(intersection)
                
                message = "-"
                
                if self.checkUpdates() == -1:
                    for each in intersection:
                        JSON.pop(each)
                    message = f"JSON updated. {count} element(s) were successfully deleted."
                elif self.checkUpdates() == 1:
                    for each in intersection:
                        JSON[each] = Face().encode(spesific=[each])[each]   
                    message = f"JSON Updated. Inserted {count} element(s)."
                
                self.clear()
                JSON = dict( sorted(JSON.items(), key=lambda x: x[0].lower()) )
                self.write(JSON)
                
                print(colored("MESSAGE:", "cyan"), message)