from info import create_app

#调用函数获取app
app=create_app("development")
# app=create_app("production")

if __name__ == '__main__':
    print(app.url_map)
    app.run()
