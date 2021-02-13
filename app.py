##V9成功部屬
#載入LineBot所需要的套件
from __future__ import print_function
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
# import mongodb
import re
from pymongo import MongoClient
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json


app = Flask(__name__)


# 自己的 Line Channel Access Token
line_bot_api = LineBotApi('OC/2LXxWpqBrf+PiU4+ALXildS+3uZCvMbYnE7bfr3MvjNx4p9K7xGZwOQItMie9IFyCRHs79f7IXz2ffyLHK1fGgfTuM9IZn3KEuLCuL0Ovyx6k/HwAS9N1RxFi3GLiX5HUfM1K83aP/czfPW4zIAdB04t89/1O/w1cDnyilFU=')
# 自己的 Line Channel Secret
handler = WebhookHandler('fd79a035b81250a8acaf1bc99c0f4269')
#parameter1 Line uid
line_bot_api.push_message('U5594160c067df9c2d9b4ceb12b0d90ad', TextSendMessage(text='你可以開始了'))

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

###################################訊息傳遞區塊################################################
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id #使用者ID
    usespeak=str(event.message.text) #使用者講的話
##------------------鏡像回復------------------------------------
#     message = TextSendMessage(text=event.message.text)
#     line_bot_api.reply_message(event.reply_token,message)
#--------------------------------------------------------------
#     line_bot_api.reply_message(event.reply_token,TextSendMessage(str(uid)+usespeak))#抓取id測試回復  
    if re.match('[0-9]{4}[<>][0-9]',usespeak) is not None:
        stock=usespeak[0:4] 
        bs=usespeak[4:5] 
        price=usespeak[5:]
        client = MongoClient("mongodb+srv://Jerry:abcd1234@cluster0.3gbxu.mongodb.net/stockdb?retryWrites=true&w=majority")
        db = client['stockdb']
        collect = db['mystock']
        collect.insert({"stock": stock,
                        "data": 'care_stock',
                        "bs": bs,
                        "price": float(price),
                        "date_info": datetime.datetime.utcnow()
                       })
        line_bot_api.push_message(uid,TextSendMessage(usespeak[0:4]+'已經儲存成功'))
        return 0
    
    elif re.match('刪除[0-9]{4}',usespeak) is not None: # 刪除存在資料庫裡面的股票
        stock=usespeak[2:]
        client = MongoClient("mongodb+srv://Jerry:abcd1234@cluster0.3gbxu.mongodb.net/stockdb?retryWrites=true&w=majority")
        db = client['stockdb']    
        collect = db['mystock']
        collect.remove({"stock": stock})            
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'已經刪除成功'))
        return 0

    elif re.match('查詢',usespeak) is not None:
        client = MongoClient("mongodb+srv://Jerry:abcd1234@cluster0.3gbxu.mongodb.net/stockdb?retryWrites=true&w=majority")
        db = client['stockdb']    
        collect = db['mystock']
        cel=list(collect.find())
        for i in cel:
            stock=i['stock']
            bs=i['bs']
            price=i['price']
            
            url = 'https://tw.stock.yahoo.com/q/ts?s=' + stock 
            list_req = requests.get(url)
            soup = BeautifulSoup(list_req.content, "html.parser")
            table = soup.find_all('tbody')[2]
            sp = table.select('tr')[1].select('td')[13].text
            getstock = table.select('tr')[1].select('td')[12].text


            if sp[0] == '△':
                if float(sp[1:]) > price:              
                    line_bot_api.push_message(uid, TextSendMessage('股票代號{0}:{1}元:{2}元\n超過設定價格提醒!!'.format(stock,getstock,sp)))

                else:
                    line_bot_api.push_message(uid, TextSendMessage('股票代號{0}:{1}元:{2}元\n未超過設定價格!!'.format(stock,getstock,sp)))

            elif sp[0] == '▽':
                if float(sp[1:]) < price:
                    line_bot_api.push_message(uid, TextSendMessage('股票代號{0}:{1}元:{2}元\n低於設定價格提醒!!'.format(stock,getstock,sp)))
                    
                else:
                    line_bot_api.push_message(uid, TextSendMessage('股票代號{0}:{1}元:{2}元\n未低於設定價格提醒!!'.format(stock,getstock,sp)))

            else:
                if float(sp[1:]) > price:
                    line_bot_api.push_message(yourid, TextSendMessage('平盤'))
 
        return 0
#################################################test
    elif re.match('籌碼',usespeak) is not None::
        url = 'http://www.twse.com.tw/fund/BFI82U'
        list_req = requests.get(url)
        soup = BeautifulSoup(list_req.content, "html.parser")
        getjson=json.loads(soup.text)

        iilist=[]
        ### 判斷請求是否成功 ###
        if getjson['stat'] != '很抱歉，沒有符合條件的資料!':  #如果抓不到資料會顯示這個
            iilist=getjson['data'][4][1:] #直接取到三大法人最後加總的資料

        ### 判斷是否為空值 ###
        if len(iilist) != 0: 
        ### 顯示結果 ###
            content1 = '日期 ＝ ' + getjson['title']+'\n'+\'三大法人合計買進 ＝ {0}\n三大法人合計賣出 ＝ {1}\n三大法人合計相差 ＝ {2}'.format(str(iilist[0]),str(iilist[1]),str(iilist[2]))
            line_bot_api.push_message(uid, TextSendMessage(content1))
            return 0
        else:
            line_bot_api.push_message(uid, TextSendMessage('請求失敗，請檢查您的股票代號'))
            return 0

        
#################################################################    
    else:
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'輸入錯誤'))
        return 0

    
#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    
