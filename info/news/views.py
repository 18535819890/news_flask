from flask import session

from . import api
@api.route('/')
def hello_world():
    #状态保持
    session["name"]="2018"
    return 'Hello World!'
