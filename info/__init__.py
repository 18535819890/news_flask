from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
#导入配置文件中的类
from config import Config,config_dict
# 导入标准日志模块
import logging
from logging.handlers import RotatingFileHandler

# 实例化sqlalchemy对象
db = SQLAlchemy()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("Desktop/news_flask/logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


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