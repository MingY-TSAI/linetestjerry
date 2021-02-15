##V10成功部屬
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
import time
import pyimgur
from PIL import Image
# import schedule
import matplotlib.pyplot as plt
import matplotlib.image as iming
from io import StringIO

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
###查詢股票提醒價格
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
#######本月至昨日標準差分析
        yes = datetime.datetime.now()- datetime.timedelta(days = 1)
        print(yes.strftime("%Y%m%d"))
        yes = '20210205'######################################################################################################################記得改
        url='https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={0}&stockNo=2330'.format(yes)

        list_req = requests.get(url)
        soup = BeautifulSoup(list_req.content, "html.parser")
        getjson=json.loads(soup.text)
        
            # 判斷請求是否成功
        if getjson['stat'] != '很抱歉，沒有符合條件的資料!':
            stocklist = getjson['data']
        else:
            pass


        if len(stocklist) != 0:
       
        #     把json資料丟進DataFrame
            stockdf = pd.DataFrame(stocklist[0:],columns=["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"])
            stockAverage = pd.to_numeric(stockdf['收盤價']).mean() #計算平均數
            stockSTD = pd.to_numeric(stockdf['收盤價']).std() #計算標準差
            # 看看這隻股票現在是否便宜（平均-兩倍標準差）

            if pd.to_numeric(stockdf['收盤價'][-1:]).values[0] < stockAverage - (2*stockSTD):
                buy = '這隻股票平均線大於兩倍標準差\n有機會進場！！'
                # 顯示結果
                get='收盤價 ＝ ' + stockdf['收盤價'][-1:].values[0]
                get=get+'\n中間價 ＝ ' + str(stockAverage)
                get=get+'\n線距 ＝ ' + str(stockSTD)
                buy=buy+'\n'+get
                line_bot_api.push_message(uid, TextSendMessage(text=buy))
            else:
                buy = '未達兩倍標準差\n很貴不要買'
                # 顯示結果
                get='收盤價 ＝ ' + stockdf['收盤價'][-1:].values[0]
                get=get+'\n中間價 ＝ ' + str(stockAverage)
                get=get+'\n線距 ＝ ' + str(stockSTD)
                buy=buy+'\n'+get
                line_bot_api.push_message(uid, TextSendMessage(text=buy))
        else:
            get='請求失敗，請檢查您的股票代號'
            line_bot_api.push_message(uid, TextSendMessage(text=get))

        return 0
############爬籌碼 三大法人最後加總的資料
    elif re.match('籌碼',usespeak) is not None:
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
            content1 = '日期 ＝ ' + getjson['title']+'\n'+\
            '三大法人合計買進 ＝ {0}\n三大法人合計賣出 ＝ {1}\n三大法人合計相差 ＝ {2}'.format(str(iilist[0]),str(iilist[1]),str(iilist[2]))
            line_bot_api.push_message(uid, TextSendMessage(content1))
            return 0
        else:
            line_bot_api.push_message(uid, TextSendMessage('請求失敗，請檢查您的股票代號'))
            return 0
##########################################################################################################################################
#############################################################################################################
    
    elif re.match('買賣',usespeak) is not None:
        def glucose_graph():
            plt.bar(stockdate, sumstock) 
            plt.xticks(fontsize=10,rotation=90)
            plt.axhline(0, color='c', linewidth=1) # 繪製0的那條線
            plt.title(stocknumber+'買賣超分析', fontsize=20,fontproperties="SimSun")
            plt.xlabel("Day", fontsize=15)
            plt.ylabel("Quantity", fontsize=15)
            plt.savefig('send.png')
            CLIENT_ID = "ce83df37b51aba3"
            PATH = "send.png"
            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")
            return uploaded_image.link

        stocknumber='2330'
        # https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20180801&stockNo=2330
        sumstock=[]
        stockdate=[]
        for i in range(11,0,-1):
            date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=i),'%Y%m%d') #先設定要爬的時間
            r = requests.get('http://www.tse.com.tw/fund/T86?response=csv&date='+date+'&selectType=ALLBUT0999') #要爬的網站
            if r.text != '\r\n': #有可能會沒有爬到東西，有可能是六日
                get = pd.read_csv(StringIO(r.text), header=1).dropna(how='all', axis=1).dropna(how='any') # 把交易所的csv資料載下來
                get=get[get['證券代號']==stocknumber] # 找到我們要搜尋的股票
                if len(get) >0:
                    get['三大法人買賣超股數'] = get['三大法人買賣超股數'].str.replace(',','').astype(float) # 去掉','這個符號把它轉成數字
                    stockdate.append(date)
                    sumstock.append(get['三大法人買賣超股數'].values[0])

        if len(stockdate) >0:
        ### 開始畫圖 ###
            glucose_graph()

        image_url = glucose_graph()     
        line_bot_api.push_message(uid, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
        return 0
#############################################################################################################   
##########################################################################################################################################           
    else:
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'輸入錯誤'))
        return 0

    
#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    
