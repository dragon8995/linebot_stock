import time
import pandas
import requests
import twstock
from cgitb import handler
from typing import Text
import os
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# 股票id
stock_id = '2731'

line_bot_api = LineBotApi(
    '你的Channel access token')
handler = WebhookHandler('你的channel secret')
line_bot_api.broadcast(TextSendMessage(text=f'開始測試{stock_id}'))
usr_id = '你的id'
# 回報串接
# 監聽所有來自 /callback 的 Post Request


@app.route("/", methods=['GET'])
def hello():
    return 'OK'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# @handler.add(MessageEvent, message=TextMessage)
# def stock(event):

def linePushMessage(msg):
    line_bot_api.broadcast(TextSendMessage(text=msg))

######################################
######以下為股票程式####################


# 連接歷史

# 定義歷史價類別


class historical_data:
    def __init__(self, id):
        self.id = str(id)
        self.stock = twstock.Stock(id)
        self.price = self.stock.price[-20:]
        self.high = self.stock.high[-5:]
        self.low = self.stock.low[-5:]

# 判定並回傳目前行情狀態


def decision(latest_price, aver_5day_high, aver_5day_low, moving_average_20day, moving_average_5day, moving_average_5min, moving_average_10min, tick3_average_5):

    up = False
    sign = 0

    if latest_price > aver_5day_high:
        up = True

    if latest_price <= moving_average_20day:
        if latest_price <= aver_5day_low:
            sign = 3
            return(up, sign)
        else:
            sign = 4
            return(up, sign)
    else:
        if latest_price > moving_average_5day and moving_average_5day > moving_average_20day:
            if latest_price > tick3_average_5:
                if moving_average_5min > moving_average_10min:
                    sign = 1
                    return(up, sign)

            else:
                if latest_price > moving_average_10min:
                    sign = 2
                    return(up, sign)

        elif latest_price < moving_average_5day:
            sign = 5
            return(up, sign)

    return(up, sign)


# 發送訊息
def message(up, sign, tmpSign, upTime):

    if up == True and upTime < 3:
        linePushMessage(f"衝啊！今天就是做多[{stock_id}]的好日子啊")
        upTime += 1

    if tmpSign == 1 and sign != 1:
        linePushMessage(f"[{stock_id}]盤中極強勢！建議進場買入！")

    elif tmpSign == 2 and sign != 2 and sign != 3 and sign != 4 and sign != 5:
        linePushMessage(f"警告！[{stock_id}]盤中轉弱！")

    elif tmpSign == 3 and sign != 3:
        linePushMessage(f"[{stock_id}]快點賣出停損！")

    elif tmpSign == 4 and sign != 3 and sign != 4:
        linePushMessage(f"[{stock_id}]該停損了")

    elif tmpSign == 5 and sign != 5 and sign != 3 and sign != 4:
        linePushMessage(f"[{stock_id}]表現弱勢！")

    return upTime


# 一連串的變數初始化
sign = None    # last signal be send
tmpSign = None  # from function decision

up = None
upTime = 0

aver_5day_high = None
aver_5day_low = None

moving_average_20day = None
moving_average_5day = None

close = None
latest_price = None


moving_average_10min = None
moving_average_5min = None

# 存「移動平均線」的平均的list
average_5_Lst = []
tick3_average_5 = None

# 存現價的List
priceLst = []
priceLst_num = 0


# 匯入歷史價格
historicalData = historical_data(stock_id)

# 計算歷史均價
moving_average_5day = sum(historicalData.price[-5:])/5
moving_average_20day = sum(historicalData.price)/20
aver_5day_high = sum(historicalData.high)/5
aver_5day_low = sum(historicalData.low)/5


while True:

    # 取得現價
    #url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_6235.tw&json=1&delay=0&_=1653874012981"
    #req = requests.get(url)
    #data = req.json()
    #close = data["msgArray"][0]["z"]

    # Yahoo現價
    res = requests.get(
        f'https://tw.stock.yahoo.com/_td-stock/api/resource/FinanceChartService.ApacLibraCharts;symbols=%5B%22{stock_id}.TW%22%5D;type=tick?bkt=%5B%22tw-qsp-exp-no2-1%22%2C%22test-es-module-production%22%2C%22test-portfolio-stream%22%5D&device=desktop&ecma=modern&feature=ecmaModern%2CshowPortfolioStream&intl=tw&lang=zh-Hant-TW&partner=none&prid=2h3pnulg7tklc&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.902&returnMeta=true')

    jd = res.json()['data']
    q = jd[0]['chart']['indicators']['quote'][0]['close']

    close = q[-1]

    # 輸出更新價格(測試用，正式上線可以拿掉)
    #line_bot_api.push_message(usr_id, TextSendMessage(text=close))
    # print(close)

    # 不是空價才執行
    if close != None:

        # 把格式轉成float
        latest_price = close

        # 更新priceLst_num(更新前須檢查priceLst_num是否已累積20筆)
        if priceLst_num >= 10:
            priceLst.pop(0)
            priceLst.append(latest_price)
        else:
            priceLst.append(latest_price)
            priceLst_num += 1

        if priceLst_num > 5:
            moving_average_5min = sum(priceLst[-5:])/5

            if len(average_5_Lst) < 3:
                average_5_Lst.append(moving_average_5min)
            else:
                average_5_Lst.pop(0)
                average_5_Lst.append(moving_average_5min)

        # priceLst_num已累積10筆
        if priceLst_num >= 10:

            moving_average_10min = sum(priceLst[-10:])/10
            tick3_average_5 = sum(average_5_Lst)/3

            up, tmpSign = decision(latest_price, aver_5day_high, aver_5day_low, moving_average_20day,
                                   moving_average_5day, moving_average_5min, moving_average_10min, tick3_average_5)

            upTime = message(up, sign, tmpSign, upTime)

            if tmpSign != 0:
                sign = tmpSign

    time.sleep(60)

# 主程式

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
