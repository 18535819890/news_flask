from flask import session,render_template,current_app

from . import api
@api.route('/')
def hello_world():
    #状态保持
    # session["name"]="2018"
    # return 'Hello World!'
    return render_template("news/index.html")

# 项目logo图标加载，浏览器会默认请求。,.ico的图片浏览器默认请求
# 如果图标加载不出来？？
# 1、清除浏览器缓存
# 2、浏览器彻底退出重启
# http://127.0.0.1:5000/favicon.ico
@api.route("/favicon.ico")
def favicon():
    # 通过应用上下文对象，调用发送静态文件给浏览器
    return current_app.send_static_file("news/favicon.ico")
