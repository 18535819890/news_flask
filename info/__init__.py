from flask import Flask
from flask_session import Session
#导入配置文件中的类
from config import Config,config_dict

#定义工厂函数，接收参数，改变生产和开发模式
def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config_dict[config_name])


    #使用session
    Session(app)

    #导入蓝图对象，注册蓝图
    from info.news import api
    app.register_blueprint(api)

    return app