from datetime import datetime

from . import passport_blue
from flask import request,jsonify,current_app,make_response,session
# 导入自定义的状态码
from info.utils.response_code import RET
# 导入captcha扩展，生成图片验证码
from info.utils.captcha.captcha import captcha
#导入redis实例对象
from info import redis_instance,constants,db
import re,random
from info.libs.yuntongxun import sms
from info.models import User

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
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整2')
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
    print(sms_code)
    # 存储在redis中，key可以拼接手机号
    try:
        redis_instance.setex('SMSCode_' + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    # 调用云通讯发送短信
    # try:
    #     ccp = sms.CCP()
    #     result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES], 1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')
    # # 判断result是否成功
    # if result == 0:
    #
    return jsonify(errno=RET.OK, errmsg='发送成功')
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送失败')



@passport_blue.route("/register",methods=["POST"])
def register():
    """
    用户注册
    获取参数---检查参数---业务处理---返回结果
    1、获取前端ajax发送的post请求的三个参数，mobile，sms_code,password
    2.检查参数完整性
    3.检查手机格式，如果只验证手机号就知道用户是否被注册不合适，容易被恶意，所以用户手机是否被注册放在验证码对比以后
    4、尝试从redis数据库中获取真实的短信验证码
    5、判断获取结果是否过期
    6、比较短信验证码是否正确，因为短信验证码可以比较多次，图片验证码只能比较一次
    7、删除redis数据库中存储的短信验证码
    用户是否注册？
    8、构造模型类对象,准备保存用户信息
    user = User()
    user.password = password
    9、提交数据到mysql数据库中，如果发生异常，需要进行回滚
    10、缓存用户信息，使用session对象到redis数据库中；
    11、返回结果
    """
    # 获取前端传入的参数
    mobile = request.json.get('mobile')
    sms_code = request.json.get('sms_code')
    password = request.json.get('password')
    print(password,sms_code,mobile)
    #2.检查参数完整性
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmag="参数不完整3")
    # 校验手机号
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 4、尝试从redis数据库中获取真实的短信验证码
    try:
        r_sms_code=redis_instance.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据库错误")
    # 5、判断获取结果是否过期
    if not r_sms_code:
        return jsonify(errno=RET.DATAERR,errmsg="短信验证码过期")
    # 6、比较短信验证码是否正确
    if r_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码不一致")
    # 7、删除redis数据库中存储的短信验证码
    try:
        redis_instance.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="删除redis中短信验证码失败")
    # 检查手机号是否注册过
    try:
        user=User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询用户失败")
    if user:
        return jsonify(errno=RET.DATAEXIST,errmsg="用户已经被注册")
    # 8、如果用户未注册,构造模型类对象,准备保存用户信息
    user=User()
    user.nick_name=mobile
    user.password=password
    user.mobile=mobile
    # 9、提交数据到mysql数据库中，如果发生异常，需要进行回滚
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="存储用户信息出错")
    # 10、缓存用户信息，使用session对象到redis数据库中；
    session["user_id"]=user.id
    session["nick_name"]=user.nick_name
    session["mobile"]=user.mobile
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK')

@passport_blue.route("/login",methods=["POST"])
def login():
    """
    用户登录
    1、获取参数，post请求，json数据，mobile，password
    2、检查参数的完整性
    3、检查手机号的格式
    4、根据手机号查询mysql，确认用户已注册
    5、判断查询结果
    6、判断密码是否正确
    7、保存用户登录时间，当前时间
    8、提交数据到mysql数据库
    9、缓存用户信息，注意：登录可以执行多次，用户有可能修改昵称，也有可能不改。
    session['nick_name'] = user.nick_name
    10、返回结果"""
    #获取参数
    mobile=request.json.get("mobile")
    password=request.json.get("password")
    #检查参数
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整4")
    # 校验手机号
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 根据手机号查询mysql，确认用户已注册
    try:
        user=User.query.filter_by(mobile=mobile).first()
        # user=User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="用户查询失败")
    # 判断用户是否存在
    # if not user:
    #     return jsonify(errno=RET.NODATA,errmsg='用户未注册')
    # import hashlib
    # hashlib.sha1
    # 判断密码是否正确
    # if not user.check_password(password):
    #     return jsonify(errno=RET.PWDERR,errmsg='密码错误')
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')
    # 保存用户的登录时间
    user.last_login=datetime.now()
    # 提交数据到mysql数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    # 缓存用户信息
    session["user_id"]=user.id
    session["mobile"]=mobile
    session["nick_name"]=user.mobile
    return jsonify(errno=RET.OK,errmsg="OK")