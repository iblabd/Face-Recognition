from flask import Flask
def createApp():
    return Flask(__name__, template_folder='../resources/views', static_folder='../resources/static')