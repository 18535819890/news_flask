from flask import Flask
from flask_session import Session
#导入配置文件中的类
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


#使用session
Session(app)

#导入蓝图对象，注册蓝图
from info.news import api
app.register_blueprint(api)