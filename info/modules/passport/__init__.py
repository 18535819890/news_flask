from flask import Blueprint
#1.创建蓝图对象
passport_blue=Blueprint("passport",__name__)

#把蓝图创建的文件导入到蓝图对象的下边
from . import views

