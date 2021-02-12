# -*- coding: utf-8 -*-
from pymongo import MongoClient
import urllib.parse
import datetime
from flask import Flask
from flask_pymongo import pymongo
from app import app
###############################################################################
#                       股票機器人 Python基礎教學 【pymongo教學】                      #
###############################################################################

# Authentication Database認證資料庫
Authdb='stockdb'





##### 資料庫連接 #####
def constructor():
    #client = MongoClient('你的連接指令')
    CONNECTION_STRING = "mongodb+srv://Jerry:abcd1234@cluster0.3gbxu.mongodb.net/stockdb?retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_STRING)
    db = client.get_database('flask_mongodb_atlas')
    return db
   
#----------------------------儲存使用者的股票--------------------------
def write_user_stock_fountion(stock, bs, price):  
    db=constructor()
    collect = pymongo.collection.Collection(db, 'mystock')
    collect.insert({"stock": stock,
                    "data": 'care_stock',
                    "bs": bs,
                    "price": float(price),
                    "date_info": datetime.datetime.utcnow()
                    })
    
#----------------------------殺掉使用者的股票--------------------------
def delete_user_stock_fountion(stock):  
    db=constructor()
    collect = pymongo.collection.Collection(db, 'mystock')
    collect.remove({"stock": stock})
    
#----------------------------秀出使用者的股票--------------------------
def show_user_stock_fountion():  
    db=constructor()
    collect = pymongo.collection.Collection(db, 'mystock')
    cel=list(collect.find({"data": 'care_stock'}))

    return cel



