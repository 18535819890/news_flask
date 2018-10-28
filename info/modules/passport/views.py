from . import passport_blue
from flask import request,jsonify,current_app,make_response
# 导入自定义的状态码
from info.utils.response_code import RET
# 导入captcha扩展，生成图片验证码
from info.utils.captcha.captcha import captcha
#导入redis实例对象
from info import redis_instance,constants
import re,random
from info.libs.yuntongxun import sms
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

@passport_blue.route('/sms_code',methods=['POST'])
def send_sms_code():
    """
    发送短信
    获取参数---检查参数---业务处理---返回结果
    1、获取参数，mobile(用户的手机号)，image_code(用户输入的图片验证码),image_code_id(UUID)
    2、检查参数的完整性
    3、检查手机号格式，正则
    4、尝试从redis中获取真实的图片验证码
    5、判断获取结果，如果不存在图片验证码已经过期
    6、需要删除redis中存储的图片验证码,图片验证码只能比较一次，本质是只能对redis数据库get一次。
    7、比较图片验证码是否正确
    8、生成短信验证码，六位数
    9、存储在redis数据库中
    10、调用云通讯，发送短信
    11、保存发送结果，判断发送是否成功
    12、返回结果

    :return:
    """
    # 获取前端传入的参数
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    # 检查参数的完整性
    # if not mobile and image_code and image_code_id:
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 校验手机号131123456789
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 尝试从redis中获取真实的图片验证码
    try:
        real_image_code = redis_instance.get('ImageCode' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取数据失败')
    # 判断获取结果是否存在
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    # 删除redis中存储的图片验证码，因为图片验证码只能get一次，只能比较一次
    try:
        redis_instance.delete('ImageCode' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 比较图片验证码是否正确
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码不一致')
    # 生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    # 存储在redis中，key可以拼接手机号
    try:
        redis_instance.setex('SMSCode_' + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    # 调用云通讯发送短信
    try:
        ccp = sms.CCP()
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')
    # 判断result是否成功
    if result == 0:
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')

    pass
