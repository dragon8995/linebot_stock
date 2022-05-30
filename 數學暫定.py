#s6-decision
import twstock
import requests
import pandas
import time

def decision(latest_price, aver_5day_high, aver_5day_low, moving_average_20day, moving_average_5day, moving_average_5min, moving_average_10min, moving_average_20min, tick3_average_5):
    
    if latest_price > aver_5day_high:
        print("衝啊！今天就是做多的好日子啊")
    
    if moving_average_5min > moving_average_10min > moving_average_20min:
        print("多頭排列！快進場！準備暴漲了！")
        return
    
    if moving_average_5min < moving_average_20min:
        print("空頭排列！手上有股票的塊陶！")
        return
    
    if latest_price <= moving_average_20day:
        if latest_price <= aver_5day_low:
            print("今天放空囉！")
            return
        else:
            print("不想賠錢的趕快賣...")
            return
    else:
        if latest_price > moving_average_5day:
            if latest_price > tick3_average_5:
                print("強勢股阿！加碼了加碼了！")
                return
            else:
                print("狀態不錯，準備進場！")
                return
    
    
    
    
aver_5day_high = None
aver_5day_low = None
    
moving_average_20day = None
moving_average_5day = None

latest_price = None

moving_average_20min = None
moving_average_10min = None
moving_average_5min = None

average_5_Lst = []
tick3_average_5 = None

priceLst = []
priceLst_num = 0

s = twstock.Stock('3105')

aver_5day = s.moving_average(s.price, 5)[-1]
aver_20day = s.moving_average(s.price, 20)[-1]

aver_5day_high = sum(s.high[-5:])/5
aver_5day_low = sum(s.low[-5:])/5


#f = True
#k = 1

#time.sleep(10)


while True:
    close = input().split(", ")
    
    if close[-1] != 'None':
        latest_price = float(close[-1])
        
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
            
            
    if priceLst_num >= 20:
        moving_average_20min = sum(priceLst)/20
        moving_average_10min = sum(priceLst[-10:])/10
        tick3_average_5 = sum(average_5_Lst)/3
        decision(latest_price, aver_5day_high, aver_5day_low, moving_average_20day, moving_average_5day, moving_average_5min, moving_average_10min, moving_average_20min, tick3_average_5)
        print()
