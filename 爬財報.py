##抓財報
import datetime
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import time
from io import StringIO
import random

now = datetime.datetime.now() 
M = now.month
D = now.day

candidate=[2330,2331] #改自己要得
candidate = pd.DataFrame(candidate,columns = ['證券代號'] )
'''
●第一季(Q1)財報：5/15前

●第二季(Q2)財報：8/14前

●第三季(Q3)財報：11/14前

●第四季(Q4)財報及年報：隔年3/31前
'''
if M<=4:
    ##得去年3季財報與前年財報
    y1 = now.year-1
    r1 = range(3,0,-1)
    y2 = now.year-2
    r2 = range(4,3,-1)


elif M<=5:
    if D >15:
        ##得去年4季財報
        y1 = now.year-1
        r1 = range(4,0,-1)
        r2 = None

    else:
        ##得去年3季財報與前年財報
        y1 = now.year-1
        r1 = range(3,0,-1)
        y2 = now.year-2
        r2 = range(4,3,-1)

elif M<=8:
    if D>14:
        ##得去年3季財報與今年第一季
        y1 = now.year
        r1 = range(1,0,-1)
        y2 = now.year-1
        r2 = range(4,1,-1)

    else:
        ##得去年4季財報
        y1 = now.year-1
        r1 = range(4,0,-1)
        r2 = None

        
elif M<=11:
    if D>14:
        ##得去年2季財報與今年第1,2季
        y1 = now.year
        r1 = range(2,0,-1)
        y2= now.year-1
        r2 = range(4,2,-1)

    else:
       ##得去年3季財報與今年第一季
        y1 = now.year
        r1 = range(1,0,-1)
        y2 = now.year-1
        r2 = range(4,1,-1)

list1 = [] #綜合損益表
list2 = [] #資產負債表
list3 = [] #現金流量表
for stock in candidate['證券代號'].values:
    for season in r1:
        ### 先與網站請求抓到每天的報價資料 ###
        url = 'https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID=' + str(stock) + '&SYEAR=' + str(y1) + '&SSEASON=' + str(season) + '&REPORT_ID=C'
        time.sleep(10)
           # 偽瀏覽器
        headers = {
                        'Host': 'mops.twse.com.tw',
                        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'         
                        }
        # 下載該年月的網站，並用pandas轉換成 dataframe
        r = requests.get(url, headers=headers)
        r.encoding = 'big5'
        getdata = pd.read_html(StringIO(r.text), encoding='big-5')
        #------------優化表格------------#        
        Integrated_table = getdata[1]['綜合損益表Statement of Comprehensive Income']
        Integrated_table = Integrated_table.drop('代號Code', axis = 1)
        Integrated_table.index = Integrated_table['會計項目Accounting Title'] 
        Integrated_table = Integrated_table.drop('會計項目Accounting Title',axis = 1)

               
        Balance_table = getdata[0]['資產負債表Balance Sheet']
        Balance_table = Balance_table.drop('代號Code', axis = 1)
        Balance_table.index = Balance_table['會計項目Accounting Title'] 
        Balance_table = Balance_table.drop('會計項目Accounting Title',axis = 1)
        
        money_table = getdata[2]['現金流量表Statements of Cash Flows']
        money_table = money_table.drop('代號Code', axis = 1)
        money_table.index = money_table['會計項目Accounting Title'] 
        money_table = money_table.drop('會計項目Accounting Title',axis = 1)

        list1.append(Integrated_table)
        list2.append(Balance_table)
        list3.append(money_table)
        #-------------------------------#
    if r2 is None : 
        pass
    else:
        for season in r2:
            ### 先與網站請求抓到每天的報價資料 ###
            url = 'https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID=' + str(stock) + '&SYEAR=' + str(y2) + '&SSEASON=' + str(season) + '&REPORT_ID=C'
            time.sleep(10)
            # 偽瀏覽器
            headers = {
                            'Host': 'mops.twse.com.tw',
                            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'         
                            }
            # 下載該年月的網站，並用pandas轉換成 dataframe
            r = requests.get(url, headers=headers)
            r.encoding = 'big5'
            getdata = pd.read_html(StringIO(r.text), encoding='big-5')
            #------------優化表格------------#
            Integrated_table = getdata[1]['綜合損益表Statement of Comprehensive Income']
            Integrated_table = Integrated_table.drop('代號Code', axis = 1)
            Integrated_table.index = Integrated_table['會計項目Accounting Title'] 
            Integrated_table = Integrated_table.drop('會計項目Accounting Title',axis = 1)


            Balance_table = getdata[0]['資產負債表Balance Sheet']
            Balance_table = Balance_table.drop('代號Code', axis = 1)
            Balance_table.index = Balance_table['會計項目Accounting Title'] 
            Balance_table = Balance_table.drop('會計項目Accounting Title',axis = 1)

            money_table = getdata[2]['現金流量表Statements of Cash Flows']
            money_table = money_table.drop('代號Code', axis = 1)
            money_table.index = money_table['會計項目Accounting Title'] 
            money_table = money_table.drop('會計項目Accounting Title',axis = 1)
        
            list1.append(Integrated_table)
            list2.append(Balance_table)
            list3.append(money_table)
            #-------------------------------#

    #------------------------------先顯示目前價格----------------------------------
    # 要抓取的網址
    url = 'https://tw.stock.yahoo.com/q/q?s=' + str(stock) 
    #請求網站
    list_req = requests.get(url)
    #將整個網站的程式碼爬下來
    soup = BeautifulSoup(list_req.content, "html.parser")
    #找到b這個標籤
    get_stock_price= soup.findAll('b')[1].text #裡面所有文字內容
    print('stock_id:',stock,'\n'+get_stock_price)
    
    
#------------------------------------------------------印出財報------------------------------------------------------#
timecount = 0
for stk in candidate['證券代號'].values:
    print('=======================================================================')
    print('stock_id:',stk)
    print('=======================================================================')
    
    for num in range(4):
        print('-----------------------------{0}-----------------------------'.format(list1[timecount].columns[0]))

        #營收要比去年高
        print('營收:',list1[timecount].loc['營業收入合計　Total operating revenue'].values[0])
        #毛利跟營收要是正的
        print('毛利:',list1[timecount].loc['營業毛利（毛損）淨額Gross profit (loss) from operations'].values[0])
        #營業利益是正的
        print('營利:',list1[timecount].loc['營業利益（損失）Net operating income (loss)'].values[0])##營利稅前淨收
        #繼續營業淨利
        print('繼續營業淨利:',list1[timecount].loc['繼續營業單位稅前淨利（淨損）Profit (loss) from continuing operations before tax'].values[0])
        #稅前稅後淨利是正的
        print('上季淨收益:',list1[timecount].loc['本期淨利（淨損）Profit (loss)'].values[0])##當季淨收益

        #本業收益（營業利益率／稅前淨利率）　＞６０％
        a = list1[timecount].loc['營業利益（損失）Net operating income (loss)'].values[0] 
#         b = list1[timecount].loc['本期淨利（淨損）Profit (loss)'].values[0]
        b = list1[timecount].loc['營業收入合計　Total operating revenue'].values[0]
        if a.isnumeric() and b.isnumeric():
            print('本業收益（營利／營收）:',float(a)/float(b) )  
        else:
            a, b = filter(str.isnumeric , a),filter(str.isnumeric , b)
            a, b = list(a),list(b)
            str_a, str_b='' ,''
            for x in a: 
                str_a+=x 
            for y in b:
                str_b+=y
            a = str_a
            b = str_b
            print('本業收益（營業利益率／稅前淨利率）:',float(a)/float(b) )
        #營運現金是正的>0
        print('現金流:',list2[timecount].loc['現金及約當現金 Cash and cash equivalents'].values[0])
        timecount+=1
print('=======================================================================')

#-------------------------------------------------------------------------------------------------------------------#   

