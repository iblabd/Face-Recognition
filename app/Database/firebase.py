import os, json, re
import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv
from termcolor import colored
from datetime import datetime
from hashlib import sha256

# TODO:
# Create validation if class_id in "user" docs is exist in id in "class" docs, etc.
# Create validation if any duplicate entry for primary key, (id, nis, id (presence) )
# Remove string colored when everything's done
# Update from "id" not randomized id

class Record:
    def __init__(self, value):
        self.value = value
        
    def get(self, field=None):
        id = list(self.value.keys())[0]
        
        if field != None:
            r = self.value[id][field]
        else:
            r = self.value[id]
            
        return r
    
    def id(self):
        return list(self.value.keys())[0]
    
    def show(self):
        print(self.value)

    def set(self, key, val):
        self.value[self.id()][key] = val

class Firebase:
    ref = None
    def __init_app(self, cred_object): 
        return firebase_admin.initialize_app(cred_object, {
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
        })
    
    def __init__(self):
        load_dotenv()
        cred_obj = firebase_admin.credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        self.default_app = self.__init_app(cred_obj)
    
    def __get(self, docname):
        return self.reference(docname).get()
    
    def reference(self, ref):
        return db.reference(ref)
    
    def push(self, contents):
        self.ref.push().set(contents)
            
    def update(self, path, contents):
        self.ref.child(path).update(contents)
    
    def delete(self, path):
        self.ref.child(path).delete()
        
    def select_from(self, _from, condition):
        # AND only
        temp = self.__get(_from)
        
        result, count = [], {}
        
        condition_count = len(condition)
        
        for k, v in temp.items():
            expected = condition_count
            satisfied = 0
            
            for con in condition:
                str_con = str(con[1])
                if re.search("like|LIKE", str_con):
                    if con[2] in temp[k][con[0]]:
                        satisfied += 1
                elif re.search("not|NOT", str_con):
                    if con[2] != temp[k][con[0]]:
                        satisfied += 1
                else:
                    if temp[k][con[0]] == con[1]:
                        satisfied += 1
            
            if satisfied == expected:
                res = {k: temp[k]}
                res = Record(res)
                result.append(res)
        
        return result
    
    def hash(self, string):
        return sha256(string.encode('utf-8')).hexdigest()
    
# firebase = Firebase()
# firebase.ref = firebase.reference("users")
# firebase.update("users", {
#     "password": firebase.hash("12345678")
# })