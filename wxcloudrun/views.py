from datetime import datetime
import time
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


# --------------------------------------------------
# 获取所有关注者openid
# --------------------------------------------------
@app.route('/testGetAllOpenIds', methods=['GET'])
def testGetAllOpenIds():
    data = _getAllOpenIds()
    res = json.dumps({'code': 200, 'data': data})
    return Response(res, mimetype='application/json')


# --------------------------------------------------
# 主动发送消息
# --------------------------------------------------
@app.route('/testSendMsgToOneUser', methods=['POST'])
def testSendMsgToOneUser():
    params = request.get_json()
    openid = params['OpenId']
    content = params['Content'] # 已是中文
    text = _sendMsg(content, openid)
    data = json.dumps({'code': 200, 'data': {'text': text}})
    return Response(data, mimetype='application/json')
@app.route('/testSendMsgToAllUsers', methods=['POST'])
def testSendMsgToAllUsers():
    params = request.get_json()
    content = params['Content'] # 已是中文
    data = _getAllOpenIds()
    openid_list = data['data']['openid']
    for openid in openid_list:
        _sendMsgTry3(content, openid)
    data = json.dumps({'code': 200, 'data': {'text': "success"}})
    return Response(data, mimetype='application/json')

# --------------------------------------------------
# 定时执行
# --------------------------------------------------
# 每12小时执行一次job函数
def job():
    return _sendMsgTry3("定时执行任务......")
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)
# schedule.every(12).hours.do(job)
schedule.every().day.at("08:30:20").do(job)
schedule.every().day.at("12:30:20").do(job)
schedule.every().day.at("20:30:20").do(job)
t = threading.Thread(target=run_schedule)
t.start()


# --------------------------------------------------
# 内部方法
# --------------------------------------------------
def _getAllOpenIds():
    # url = 'http://api.weixin.qq.com/cgi-bin/message/custom/send'
    url = 'http://api.weixin.qq.com/cgi-bin/user/get'
    response = requests.get(url)
    data = response.json()  # 获取响应的JSON数据
    return data

def _sendMsgTry3(content, openid='o7Fnt6ZwAZFjOukruDoOOgJXUeA8'):
    try:
        return _sendMsg(content, openid)
    except Exception as e:
        app.logger.info('call _sendMsg error......')
    return "success"
def _sendMsg(content, openid='o7Fnt6ZwAZFjOukruDoOOgJXUeA8'):
    url = 'http://api.weixin.qq.com/cgi-bin/message/custom/send'
    headers = {'Content-Type': 'application/json'}
    info = {
        'touser': openid,
        'msgtype': 'text',
        'text': {
            'content': content
        }
    }
    request_body = json.dumps(info, ensure_ascii=False).encode('utf-8')
    response = requests.post(url, headers=headers, data=request_body)
    app.logger.info('接口返回内容:' + response.text)
    return response.text
