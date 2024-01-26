from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import json
from flask import Response
import requests
import schedule
import threading

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    # """
    # :return:计数结果/清除结果
    # """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')

@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)

@app.route('/wxreply', methods=['GET'])
def get_wxreply():
    data = json.dumps({'code': 200, 'data': {}})
    return Response(data, mimetype='application/json')

@app.route('/wxreply', methods=['POST'])
def wxreply():
    params = request.get_json()
    if 'action' in params and params['action'] == 'CheckContainerPath':
        data = json.dumps({'code': 200, 'data': {}})
        return Response(data, mimetype='application/json')
    else:
        content_as_chinese = params['Content'] # 已是中文
        xwx_source = params['ToUserName']
        xwx_openid = params['FromUserName']
        info = {
            'ToUserName': xwx_openid,
            'FromUserName': xwx_source,
            'CreateTime': int(datetime.now().timestamp()),
            'MsgType': 'text',
            'Content': content_as_chinese
        }
        app.logger.info('\n\noutput=' + json.dumps(info))
        data = json.dumps(info, ensure_ascii=False).encode('utf-8')
        return Response(data, mimetype='application/json')

# 定时执行的任务逻辑
def noticeJob():
    print("定时任务执行中...")
    # 发送post请求
    sendMsg(content='定时任务')
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)
schedule.every(20).seconds.do(noticeJob)  # 每10秒执行一次job函数
t = threading.Thread(target=run_schedule)
t.start()

def sendMsg(content, openid='o7Fnt6ZwAZFjOukruDoOOgJXUeA8'):
    url = 'http://api.weixin.qq.com/cgi-bin/message/custom/send'
    headers = {'Content-Type': 'application/json'}
    data = {
        'touser': openid,
        'msgtype': 'text',
        'text': {
            'content': content
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print('接口返回内容', response.text)
    return json.loads(response.text)
