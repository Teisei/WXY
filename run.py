# 创建应用实例
import sys

from wxcloudrun import app

# 启动Flask Web服务
if __name__ == '__main__':
    # app.config['JSON_AS_ASCII'] = False
    app.json.ensure_ascii = False
    app.run(host=sys.argv[1], port=sys.argv[2])
