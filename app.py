##V11成功部屬
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
from pandas_datareader import data  
import yfinance as yf # yahoo專用的拿來拉股票資訊   
import datetime
import matplotlib.pyplot as plt # 繪圖專用   
import mpl_finance as mpf # 專門用來畫蠟燭圖的
import talib


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
    # 查詢股票提醒價格
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
            # 發題醒

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

            ################以下請注意是否放回圈內
        # 本月至昨日標準差分析
        yes = datetime.datetime.now()- datetime.timedelta(days = 1)
        yes = yes.strftime("%Y%m%d")
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
       
            # 把json資料丟進DataFrame
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
            
            
        # 各種分析圖
        # 畫圖格式
        def make_plot(titlename, savename ):
            plt.title(titlename) # 標題設定
            plt.grid()
            plt.savefig(savename)
            CLIENT_ID = "ce83df37b51aba3"
            PATH = savename
            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(PATH, title="upload pic")
            return uploaded_image.link
            
        
        # K線圖
        def K_line(): 
            fig = plt.figure(figsize=(24, 14))
            ax = fig.add_subplot(1, 1, 1)
            ax.set_xticks(range(0, len(stock.index), 5))
            ax.set_xticklabels(stock.index[::5])
            plt.xticks(fontsize=10,rotation=90)
            mpf.candlestick2_ochl(ax, stock['Open'], stock['Close'], stock['High'], stock['Low'],
                                 width=0.5, colorup='r', colordown='green',
                                 alpha=0.6)
            return make_plot("Candlestick_chart",'kline.png') 

        # 股票KD圖
        def KD_plot(): 
            ret = pd.DataFrame(list(talib.STOCH(stock['High'].values, stock['Low'].values, stock['Close'].values))).transpose()
            ret.columns=['K','D']
            ret.index = stock['Close'].index
            ### 開始畫圖 ###
            ret.plot(color=['#5599FF','#66FF66'], linestyle='dashed')
            stock['Close'].plot(secondary_y=True,color='#FF0000')
            return make_plot("KD",'kd.png')  
        
        #移動平均成本
        # 股票MA圖        
        def moving_avg():
            ret = pd.DataFrame(talib.SMA(stock['Close'].values,10), columns= ['10-day average']) #10日移動平均線
            ret = pd.concat([ret,pd.DataFrame(talib.SMA(stock['Close'].values,20), columns= ['20-day average'])], axis=1) #10日移動平均線
            ret = pd.concat([ret,pd.DataFrame(talib.SMA(stock['Close'].values,60), columns= ['60-day average'])], axis=1) #10日移動平均線
            ret = ret.set_index(stock['Close'].index.values)
            ret.plot(color=['#5599FF','#66FF66','#FFBB66'], linestyle='dashed')
            stock['Close'].plot(secondary_y=True,color='#FF0000')
            return make_plot("Moving_Average",'mavg.png')
        
        # MACD
        def MACD():
            ret=pd.DataFrame()
            ret['MACD'],ret['MACDsignal'],ret['MACDhist'] = talib.MACD(stock['Close'].values,fastperiod=6, slowperiod=12, signalperiod=9)
            ret = ret.set_index(stock['Close'].index.values)
            ret.plot(color=['#5599FF','#66FF66','#FFBB66'], linestyle='dashed')
            stock['Close'].plot(secondary_y=True,color='#FF0000')
            return make_plot("Moving Average Convergence / Divergence",'macd.png')        
        
        # 量分析# 股票OBV圖
        def vol():       
            ret = pd.DataFrame(talib.OBV(stock['Close'].values, stock['Volume'].values.astype(float)), columns= ['OBV'])
            ret = ret.set_index(stock['Close'].index.values)
            ret.plot(color=['#5599FF'], linestyle='dashed')
            stock['Close'].plot(secondary_y=True,color='#FF0000')
            return make_plot("On_Balance_Volume",'vol.png')
        
        # 股票ATR圖
        def ATR(): 
            ret = pd.DataFrame(talib.ATR(stock['High'].values, stock['Low'].values, stock['Close'].values), columns= ['Average True Range'])
            ret = ret.set_index(stock['Close'].index.values)
            ret.plot(color=['#5599FF'], linestyle='dashed')
            stock['Close'].plot(secondary_y=True,color='#FF0000')
            return make_plot("Average_True_Range",'atr.png')

        # 股票RSI圖    
        def RST():
            ret = pd.DataFrame(talib.RSI(stock['Close'].values,24), columns= ['Relative Strength Index'])
            ret = ret.set_index(stock['Close'].index.values)
            ret.plot(color=['#5599FF'], linestyle='dashed')
            stock['Close'].plot(secondary_y=True,color='#FF0000')
            return make_plot("Relative_Strength_Index",'rst.png')
        
        # 資金流動,股票MFI圖
        def MFI():
            ret = pd.DataFrame(talib.MFI(stock['High'].values,stock['Low'].values,stock['Close'].values,stock['Volume'].values.astype(float), timeperiod=14), columns= ['Money Flow Index'])
            ret = ret.set_index(stock['Close'].index.values)
            ret.plot(color=['#5599FF'], linestyle='dashed')
            stock['Close'].plot(secondary_y=True,color='#FF0000')
            return make_plot("Money_Flow_Index",'mfi.png')
        
        # 股票ROC圖
        def ROC():
            ret = pd.DataFrame(talib.ROC(stock['Close'].values, timeperiod=10), columns= ['Receiver Operating Characteristic curve'])
            ret = ret.set_index(stock['Close'].index.values)
            ret.plot(color=['#5599FF'], linestyle='dashed')
            stock['Close'].plot(secondary_y=True,color='#FF0000')
            return make_plot("Receiver_Operating_Characteristic_Curve",'roc.png')

        userstock = stock
        start = datetime.datetime.now() - datetime.timedelta(days=365) #先設定要爬的時間
        end = datetime.date.today()

        # 與yahoo請求
        pd.core.common.is_list_like = pd.api.types.is_list_like
        yf.pdr_override()

        # 取得股票資料
        stock = data.get_data_yahoo(userstock+'.TW', start, end)
        # 劃出所有分析圖
        image_url1 = K_line()    
        image_url2 = KD_plot()    
        image_url3 = moving_avg()
        image_url4 = MACD()
        image_url5 = vol()
        image_url6 = ATR()
        image_url7 = RST()
        image_url8 = MFI()
        image_url9 = ROC()
        listurl = [image_url1, image_url2, image_url3, image_url4, image_url5, image_url6, image_url7, image_url8, image_url9]
        for url in listurl:
            line_bot_api.push_message(uid, ImageSendMessage(original_content_url=url, preview_image_url=url))

        return 0

# 爬籌碼 三大法人最後加總的資料
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
    
    elif re.match('法人',usespeak) is not None:
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
                glucose_graph()

            image_url = glucose_graph()     
            line_bot_api.push_message(uid, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
        return 0
    
#     elif re.match('買啥',usespeak) is not None:
#         elected='' # 最後可以買的股票放這裡
#         ########## 當短期5日線突破20日線 ##########
#         url = 'https://tw.screener.finance.yahoo.net/screener/ws?PickID=100205&PickCount=1700&f=j'
#         list_req = requests.get(url)
#         soup = BeautifulSoup(list_req.content, "html.parser")
#         getjson1=json.loads(soup.text)

#         ########## 股本大於20億 ##########
#         url = 'https://tw.screener.finance.yahoo.net/screener/ws?PickID=100538,100539,100540,100541&PickCount=1700&f=j&366'
#         list_req = requests.get(url)
#         soup = BeautifulSoup(list_req.content, "html.parser")
#         getjson2=json.loads(soup.text)

#         for i in getjson1['items']:
#             if i['symid'] in str(getjson2['items']):
#         ########## 週均量大於 1000 張 ##########   
#                 url = 'https://tw.stock.yahoo.com/q/q?s=' + i['symid']
#                 getjson3=pd.read_html(url,encoding='big5',header=0)

#                 if getjson3[2]['張數'].values[0] >1000 :
#                     elected = elected + i['symid'] +'\t' +i['symname']+'\t' +str(getjson3[2]['成交'].values[0])+'\n'

#         ########## 秀出結果 ##########            
#         if elected != '':# 判斷是不是空直
#             line_bot_api.push_message(uid, TextSendMessage(elected))
#             return 0

#         else:
#             line_bot_api.push_message(uid, TextSendMessage('沒有股票可以買'))
#             return 0
       
    else:
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'輸入錯誤'))
        return 0



    
#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    
