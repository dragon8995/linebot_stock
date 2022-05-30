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

line_bot_api = LineBotApi(
    'ywbkuyYgIVQGdHTuiHbtdn5tLmKWzhG5VFxvHXHxmLOElHvHxjxOhPeteqf9QaY5UkjTR1XUBZq2X6zof0uLTYktZME3wEoxJaPtrsn+PGhAst0YXk+ts88MFv6J9FlOr5XuB/Da5WBrNvXg7reR+gdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5623f00a9894da7ed8bb303953a1fd2b')
line_bot_api.push_message(
    'Ub29322afc6722cd88bfe24c786320c7a', TextSendMessage(text='開始測試'))
usr_id = 'Ub29322afc6722cd88bfe24c786320c7a'
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
# def echo(event):

    # if event.source.user_id != "Ub29322afc6722cd88bfe24c786320c7a":
#    line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(text=event.message.text)
#    )


# 主程式
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

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


def decision(latest_price, aver_5day_high, aver_5day_low, moving_average_20day, moving_average_5day, moving_average_5min, moving_average_10min, moving_average_20min, tick3_average_5):

    up = False
    sign = 0

    if latest_price > aver_5day_high:
        up = True

    if moving_average_5min > moving_average_10min and moving_average_10min > moving_average_20min:
        sign = 1
        return(up, sign)

    if moving_average_5min < moving_average_10min and moving_average_10min < moving_average_20min:
        sign = 2
        return(up, sign)

    if latest_price <= moving_average_20day:
        if latest_price <= aver_5day_low:
            sign = 3
            return(up, sign)
        else:
            sign = 4
            return(up, sign)
    else:
        if latest_price > moving_average_5day:
            if latest_price > tick3_average_5:
                sign = 5
                return(up, sign)
            else:
                sign = 6
                return(up, sign)

    return(up, sign)


# 發送訊息
def message(up, sign, tmpSign, upTime):
    if up == True and upTime < 10:
	    line_bot_api.push_message(usr_id, TextSendMessage(text="衝啊！今天就是做多的好日子啊"))
        # print("衝啊！今天就是做多的好日子啊")
        upTime += 1

    if sign != 1 and sign != 5 and sign != 6:
        if tmpSign == 1:
		    line_bot_api.push_message(usr_id, TextSendMessage(text="多頭排列！快進場！準備大漲了！"))
		    # print("多頭排列！快進場！準備大漲了！")

        elif tmpSign == 6:
		    line_bot_api.push_message(usr_id, TextSendMessage(text="狀態不錯，準備進場！"))
            # print("狀態不錯，準備進場！")

        elif tmpSign == 5:
		    line_bot_api.push_message(usr_id, TextSendMessage(text="強勢股阿！加碼了加碼了！"))
        	# print("強勢股阿！加碼了加碼了！")

    else:
        if tmpSign == 2:
		    line_bot_api.push_message(usr_id, TextSendMessage(text="空頭排列！手上有股票的塊陶！"))
        	# print("空頭排列！手上有股票的塊陶！")

        elif tmpSign == 3:
		    line_bot_api.push_message(usr_id, TextSendMessage(text="今天放空囉！"))
        	# print("今天放空囉！")

        elif tmpSign == 4:
		    line_bot_api.push_message(usr_id, TextSendMessage(text="不想賠錢的趕快賣..."))
           	# print("不想賠錢的趕快賣...")

    return upTime


# 一連串的變數初始化
sign = None
tmpSign = None
up = None
upTime = 0

aver_5day_high = None
aver_5day_low = None

moving_average_20day = None
moving_average_5day = None

close = None
latest_price = None

moving_average_20min = None
moving_average_10min = None
moving_average_5min = None

# 存「移動平均線」的平均的list
average_5_Lst = []
tick3_average_5 = None

# 存現價的List
priceLst = []
priceLst_num = 0


# 匯入歷史價格
historicalData = historical_data('1907')

# 計算歷史均價
moving_average_5day = sum(historicalData.price[-5:])/5
moving_average_20day = sum(historicalData.price)/20
aver_5day_high = sum(historicalData.high)/5
aver_5day_low = sum(historicalData.low)/5


while True:

    # 取得現價
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_1907.tw&json=1&delay=0&_=1653874012981"
    req = requests.get(url)
    data = req.json()
    close = data["msgArray"][0]["z"]

    # 輸出更新價格(測試用，正式上線可以拿掉)
    print(close)

    # 不是空價才執行
    if close != '-':

        # 把格式轉成float
        latest_price = float(close)

        # 更新priceLst_num(更新前須檢查priceLst_num是否已累積20筆)
        if priceLst_num >= 20:
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

        # priceLst_num已累積20筆
        if priceLst_num >= 20:
            moving_average_20min = sum(priceLst)/20
            moving_average_10min = sum(priceLst[-10:])/10
            tick3_average_5 = sum(average_5_Lst)/3

            up, tmpSign = decision(latest_price, aver_5day_high, aver_5day_low, moving_average_20day,
                                   moving_average_5day, moving_average_5min, moving_average_10min, moving_average_20min, tick3_average_5)

            upTime = message(up, sign, tmpSign, upTime)

            sign = tmpSign
            print()

    time.sleep(10)
