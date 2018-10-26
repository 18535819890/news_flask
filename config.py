from redis import StrictRedis

class Config():
    # 调试信息
    DEBUG = True
    # 配置密钥
    SECRET_KEY = 'rMlmlHmW7p78UfuuiS6HJ3sGf9dS36lnCdUY6LIAyVt/TNnjL7bpWIctW'
    # 配置mysql的连接
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/info33'
    # 动态追踪修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 设置session信息存储在redis中
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host='127.0.0.1', port=6379)
    SESSION_USE_SIGNER = True  # SESSION信息签名
    PERMANENT_SESSION_LIFETIME = 86400  # Flask框架自带的session有效期配置