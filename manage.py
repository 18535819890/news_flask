from flask import Flask,session
from flask_session import Session
#导入配置文件中的类
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


#使用session
Session(app)

@app.route('/')
def hello_world():
    #状态保持
    session["name"]="2018"
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
