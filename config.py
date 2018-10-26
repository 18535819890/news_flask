from redis import StrictRedis

class Config():
    # 调试信息
    DEBUG = None
    # 配置密钥
    SECRET_KEY = 'rMlmlHmW7p78UfuuiS6HJ3sGf9dS36lnCdUY6LIAyVt/TNnjL7bpWIctW'
    # 配置mysql的连接
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/news_info'
    # 动态追踪修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 设置session信息存储在redis中
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host='127.0.0.1', port=6379)
    SESSION_USE_SIGNER = True  # SESSION信息签名
    PERMANENT_SESSION_LIFETIME = 86400  # Flask框架自带的session有效期配置

# 定义开发模式下的配置
class DevelopmentConfig(Config):
    DEBUG = True

# 定义生产模式下的配置
class ProductionConfig(Config):
    DEBUG = False

# 定义字典映射不同环境下的配置类
config_dict={
    "development":DevelopmentConfig,
    "production":ProductionConfig,
}