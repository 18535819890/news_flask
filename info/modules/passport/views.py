from . import passport_blue
from flask import request,jsonify,current_app,make_response
# 导入自定义的状态码
from info.utils.response_code import RET
# 导入captcha扩展，生成图片验证码
from info.utils.captcha.captcha import captcha
#导入redis实例对象
from info import redis_instance,constants
#用蓝图路由映射
@passport_blue.route("/image_code")
def generate_image_code():
    """
    生成图片验证码
    1、获取参数，uuid，使用request.args查询字符串参数
    2、判断参数是否存在，如果不存在，直接return
    3、调用captcha工具，生成图片验证码
    name,text,image
    4、在redis数据库中存储图片验证码的text内容
    5、返回图片给前端
    """
    # 获取查询字符串形式的参数
    image_code_id=request.args.get("image_code_id")
    # 如果参数不存在，直接return
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR,errmsg="参数缺失")
    # 调用captcha生成图片验证码
    name,text,image=captcha.generate_captcha()
    # 存储图片验证码的text到redis数据库中
    try:
        redis_instance.setex('ImageCode'+image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
        # 返回图片
    response=make_response(image)
    # 设置响应的类型为image/jpg
    response.headers['Content-Type'] = 'image/jpg'
    return response
        