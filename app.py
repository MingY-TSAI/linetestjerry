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
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data   ###########新套件
import yfinance as yf # yahoo專用的拿來拉股票資訊   ###########新套件
import datetime
import matplotlib.pyplot as plt # 繪圖專用   
import mpl_finance as mpf # 專門用來畫蠟燭圖的  ###########新套件

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
##-------------------------------------------------------------------------------------------------------------------------------------------------
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
            ############發題醒

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
            ############
#######本月至昨日標準差分析
        yes = datetime.datetime.now()- datetime.timedelta(days = 1)
        print(yes.strftime("%Y%m%d"))
        yes = '20210205'######################################################################################################################記得改
        url='https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={0}&stockNo={1}'.format(yes,stock)

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
##-------------------------------------------------------------------------------------------------------------------------------------------------
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
        
        client = MongoClient("mongodb+srv://Jerry:abcd1234@cluster0.3gbxu.mongodb.net/stockdb?retryWrites=true&w=majority")
        db = client['stockdb']    
        collect = db['mystock']
        cel=list(collect.find())
        stocknum = []
        for i in cel:
            stock=i['stock']
            stocknum.append(stock)
            
#    stocknumber = '2330'######################################################################################################################記得改         
        for stock in stocknum:
            stocknumber = stock
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

##########################################################################################################################################           
    else:
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'輸入錯誤'))
        return 0
'''
##8   8-1,8-2,8-3 8-4 ,8-5 ,8-9,8-10,8-11
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 14:35:26 2019

@author: aaaaa
"""

import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data   ###########新套件
import yfinance as yf # yahoo專用的拿來拉股票資訊   ###########新套件
import datetime
import matplotlib.pyplot as plt # 繪圖專用   
import mpl_finance as mpf # 專門用來畫蠟燭圖的  ###########新套件

userstock='2331'
start = datetime.datetime.now() - datetime.timedelta(days=365) #先設定要爬的時間
end = datetime.date.today()

# 與yahoo請求
pd.core.common.is_list_like = pd.api.types.is_list_like
yf.pdr_override()

# 取得股票資料
stock = data.get_data_yahoo(userstock+'.TW', start, end)

#####################################8-1 股票K線圖
fig = plt.figure(figsize=(24, 8))
ax = fig.add_subplot(1, 1, 1)
ax.set_xticks(range(0, len(stock.index), 5))
ax.set_xticklabels(stock.index[::5])
plt.xticks(fontsize=10,rotation=90)
mpf.candlestick2_ochl(ax, stock['Open'], stock['Close'], stock['High'], stock['Low'],
                     width=0.5, colorup='r', colordown='green',
                     alpha=0.6)
plt.title("Candlestick_chart") # 標題設定
plt.grid()
# plt.savefig('Candlestick_chart.png') #存檔

# 股票KD圖#################################################KD圖
##8-2 Stochastic Oscillator KD指標圖
'''
KD指標 的主要假設：
股價有上漲趨勢時，當日收盤價會接近近期一段時間內最高價；
股價有下跌趨勢時，當日收盤價會接近近期一段時間內最低價。
'''
ret = pd.DataFrame(list(talib.STOCH(stock['High'].values, stock['Low'].values, stock['Close'].values))).transpose()
ret.columns=['K','D']
ret.index = stock['Close'].index

### 開始畫圖 ###
ret.plot(color=['#5599FF','#66FF66'], linestyle='dashed')

stock['Close'].plot(secondary_y=True,color='#FF0000')
plt.title("KD") # 標題設定

#8-3 移動平均成本
# 股票MA圖
ret = pd.DataFrame(talib.SMA(stock['Close'].values,10), columns= ['10-day average']) #10日移動平均線
ret = pd.concat([ret,pd.DataFrame(talib.SMA(stock['Close'].values,20), columns= ['20-day average'])], axis=1) #10日移動平均線
ret = pd.concat([ret,pd.DataFrame(talib.SMA(stock['Close'].values,60), columns= ['60-day average'])], axis=1) #10日移動平均線
ret = ret.set_index(stock['Close'].index.values)

### 開始畫圖 ###
ret.plot(color=['#5599FF','#66FF66','#FFBB66'], linestyle='dashed')
stock['Close'].plot(secondary_y=True,color='#FF0000')
plt.title("Moving_Average") # 標題設定

##8-4 MACD
'''
應用兩條速度不同的平滑移動平均線(EMA)，計算兩者之間的差離狀態(DIF)，並且對差離值(DIF)做指數平滑移動平均，即為MACD線。

簡單來說MACD就是，長期與短期的移動平均線即將要收斂或發散的徵兆，是用來判斷買賣股票的時機與訊號。
MACDsignal 為短期線 突破為買點
'''
ret=pd.DataFrame()
ret['MACD'],ret['MACDsignal'],ret['MACDhist'] = talib.MACD(stock['Close'].values,fastperiod=6, slowperiod=12, signalperiod=9)
ret = ret.set_index(stock['Close'].index.values)

### 開始畫圖 ###
ret.plot(color=['#5599FF','#66FF66','#FFBB66'], linestyle='dashed')
stock['Close'].plot(secondary_y=True,color='#FF0000')
plt.title("Moving Average Convergence / Divergence") # 標題設定

#8-5量分析
# 股票OBV圖
ret = pd.DataFrame(talib.OBV(stock['Close'].values, stock['Volume'].values.astype(float)), columns= ['OBV'])
ret = ret.set_index(stock['Close'].index.values)

### 開始畫圖 ###
ret.plot(color=['#5599FF'], linestyle='dashed')
stock['Close'].plot(secondary_y=True,color='#FF0000')
plt.title("On_Balance_Volume") # 標題設定


##############################8-8真實趨勢
# 股票ATR圖
ret = pd.DataFrame(talib.ATR(stock['High'].values, stock['Low'].values, stock['Close'].values), columns= ['Average True Range'])
ret = ret.set_index(stock['Close'].index.values)

### 開始畫圖 ###
ret.plot(color=['#5599FF'], linestyle='dashed')
stock['Close'].plot(secondary_y=True,color='#FF0000')
plt.title("Average_True_Range") # 標題設定

##########################8-9相對強度
# 股票RSI圖
ret = pd.DataFrame(talib.RSI(stock['Close'].values,24), columns= ['Relative Strength Index'])
ret = ret.set_index(stock['Close'].index.values)

### 開始畫圖 ###
ret.plot(color=['#5599FF'], linestyle='dashed')
stock['Close'].plot(secondary_y=True,color='#FF0000')
plt.title("Relative_Strength_Index") # 標題設定

###############################################8-10資金流動
# 股票MFI圖
ret = pd.DataFrame(talib.MFI(stock['High'].values,stock['Low'].values,stock['Close'].values,stock['Volume'].values.astype(float), timeperiod=14), columns= ['Money Flow Index'])
ret = ret.set_index(stock['Close'].index.values)

### 開始畫圖 ###
ret.plot(color=['#5599FF'], linestyle='dashed')
stock['Close'].plot(secondary_y=True,color='#FF0000')
plt.title("Money_Flow_Index") # 標題設定

##############################8-11
# 股票ROC圖
ret = pd.DataFrame(talib.ROC(stock['Close'].values, timeperiod=10), columns= ['Receiver Operating Characteristic curve'])
ret = ret.set_index(stock['Close'].index.values)

### 開始畫圖 ###
ret.plot(color=['#5599FF'], linestyle='dashed')
stock['Close'].plot(secondary_y=True,color='#FF0000')
plt.title("Receiver_Operating_Characteristic_Curve") # 標題設定

plt.show()

# plt. close() # 殺掉記憶體中的圖片

'''    
#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    
