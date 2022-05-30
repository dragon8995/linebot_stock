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
#line_bot_api.push_message('Ub29322afc6722cd88bfe24c786320c7a' , TextSendMessage(text='開始測試'))

# 回報串接
# 監聽所有來自 /callback 的 Post Request


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


@handler.add(MessageEvent, message=TextMessage)
def echo(event):

    # if event.source.user_id != "Ub29322afc6722cd88bfe24c786320c7a":
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )


# 主程式
if __name__ == "__main__":
    app.run()
