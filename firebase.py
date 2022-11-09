import os, json
import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv
from termcolor import colored

class Firebase:
    def __init_app__(self, cred_object): 
        return firebase_admin.initialize_app(cred_object, {
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
        })
    
    def __init__(self):
        load_dotenv()
        cred_obj = firebase_admin.credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        self.default_app = self.__init_app__(cred_obj)
    
    def ref(self, ref): 
        self.ref = db.reference(ref)
    
    def push(self, contents):
        self.ref.push().set(contents)
        print(colored("query: push", "green"))
            
    def update(self, path, contents):
        self.ref.child(path).update(contents)
        print(colored("query: update", "green"))
    
    def delete(self, path):
        self.ref.child(path).delete()
        print(colored("query: delete", "red"))
    
    def __get__(self, docname):
        return db.reference(docname).get()
        
    def select_from(self, _from, condition):
        temp = self.__get__(_from)
        
        result = []
        
        for k, v in temp.items():
            for con in condition:
                if con[1] in ["like", "LIKE"]:
                    if con[2] in temp[k][con[0]]:
                        result.append({k: temp[k]})
                else:
                    if temp[k][con[0]] == con[1]:
                        result.append({k: temp[k]})
        
        return result