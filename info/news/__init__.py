
from flask import Blueprint
#创建蓝图对象,去注册蓝图
api=Blueprint("api",__name__)

#把蓝图创建的文件导入到蓝图对象的下边
from . import views