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
 #載入LineBot所需要的套件
# import mongodb
import re
from pymongo import MongoClient
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)


# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('OC/2LXxWpqBrf+PiU4+ALXildS+3uZCvMbYnE7bfr3MvjNx4p9K7xGZwOQItMie9IFyCRHs79f7IXz2ffyLHK1fGgfTuM9IZn3KEuLCuL0Ovyx6k/HwAS9N1RxFi3GLiX5HUfM1K83aP/czfPW4zIAdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('fd79a035b81250a8acaf1bc99c0f4269')

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

#訊息傳遞區塊
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
        for i in data:
            stock=i['stock']
            bs=i['bs']
            price=i['price']
            
        url = 'https://tw.stock.yahoo.com/q/ts?s=' + stock 
        list_req = requests.get(url)
        soup = BeautifulSoup(list_req.content, "html.parser")
        table = soup.find_all('tbody')[2]
        sp = table.select('tr')[1].select('td')[13].text
        getstock = table.select('tr')[1].select('td')[12].text
        print(sp,getstock)
        price = 1.0
        bs = '>'     
        
        if sp[0] == '△':
            if float(sp[1:]) > price:              
                line_bot_api.push_message(uid, TextSendMessage('股票代號{0}:{1}元:{2}元\n超過設定價格提醒!!'.format(stock,getstock,sp))
                
            else:
                line_bot_api.push_message(uid, TextSendMessage('股票代號{0}:{1}元:{2}元\n未超過設定價格!!'.format(stock,getstock,sp))
                                          
        elif sp[0] == '▽':
            if float(sp[1:]) < price:
#                 line_bot_api.push_message(yourid, TextSendMessage(text=''))
                print(stock,":",sp,'\n低於設定價格提醒!!')
            else:
                print(stock,":",sp,'\n未低於設定價格')
#                 line_bot_api.push_message(yourid, TextSendMessage(text=''))
            
        else:
            if float(sp[1:]) > price:
                line_bot_api.push_message(yourid, TextSendMessage('平盤'))

        
        return 0
                                  
    else:
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'輸入錯誤'))
        return 0
############################################################################################
# ##### 資料庫連接 #####
# def constructor():
#     #client = MongoClient('你的連接指令')
#     CONNECTION_STRING = "mongodb+srv://Jerry:abcd1234@cluster0.3gbxu.mongodb.net/stockdb?retryWrites=true&w=majority"
#     client = pymongo.MongoClient(CONNECTION_STRING)
#     db = client.get_database('flask_mongodb_atlas')
#     return db

# def show_user_stock_fountion():  
#     client = MongoClient("mongodb+srv://Jerry:abcd1234@cluster0.3gbxu.mongodb.net/stockdb?retryWrites=true&w=majority")
#     db = client['stockdb']    
#     collect = db['mystock']
#     cel=list(collect.find())

#     return cel
############################################################################################
# def job():
#     data = show_user_stock_fountion()



        



# second_5_j = schedule.every(10).seconds.do(job)

# 無窮迴圈
# a=0
# while a<2: 
#     schedule.run_pending()
#     a+=1
#     time.sleep(2)
    
    
#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# if __name__ == '__main__':
#     app.run(debug=True)  
    
