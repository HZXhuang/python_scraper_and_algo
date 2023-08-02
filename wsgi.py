from app import app
from gevent import pywsgi


if __name__ == "__main__":
    # app.run(debug=True, host="127.0.0.1")
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)  # 使用WSGI服务器启动
    server.serve_forever()
