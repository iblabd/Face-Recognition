from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
app = db.create_engine("mysql://admin:131004@localhost:3306/db_presensi")
    

try:
    app.connect()
    print("success")
except Exception as e:
    print('Encountered error while generating connection string for MySQL!')
    print(e)