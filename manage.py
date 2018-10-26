from flask import Flask,session
from flask_session import Session
from redis import StrictRedis

app = Flask(__name__)

#调试信息
app.config["DEBUG"]=True
#密钥
app.config["SECRET_KEY"]="TJT6ePtHptd2C6a/3fxulg2r7smlM6OiXPVTnh22Ao4="
# 设置session信息存储在redis中
app.config["SESSION_TYPE"]= 'redis'
app.config["SESSION_REDIS"] = StrictRedis(host='127.0.0.1', port=6379,db=3)
app.config["SESSION_USE_SIGNER"] = True  # SESSION信息签名
app.config["PERMANENT_SESSION_LIFETIME"] = 86400  # Flask框架自带的session有效期配置
#数据库配置
# 配置mysql的连接
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:mysql@localhost/news_info'
# 动态追踪修改
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#使用session
Session(app)

@app.route('/')
def hello_world():
    #状态保持
    session["name"]="2018"
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
