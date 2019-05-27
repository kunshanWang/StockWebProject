
import twstock
import mysql.connector
import time
import sys
from StockWebUtility import Aver


# select type, code, name from twstock where market = '上市' and type = '股票';

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="kusan",
        passwd="wqskusan@64",
        database="TWStockDB"
        )
except:
    print("connect mysql or open dtata base error!")
    sys.exit()

v_cursor = mydb.cursor()
v_sqlcommand = "select code from twstock where market = '上櫃' and type = '股票'"

v_cursor.execute(v_sqlcommand)
v_result = v_cursor.fetchall()

v_stockcode = '2330'
for x in v_result:
   print(x)
   v_stockcode = x[0]
    
   v_sqlcommand = 'show tables'
   v_cursor.execute(v_sqlcommand)

   v_tablelist = [item[0] for item in v_cursor.fetchall()]
   v_checktable = 'id_' + v_stockcode
   if v_checktable in v_tablelist:
       print(v_checktable +  'already create')
       continue

   try:
     v_sqlcommand = 'CREATE TABLE ID_' + v_stockcode + '(Tdate DATE, capacity INT, high float, low float, price float, diff float, 5d_price float, 10d_price float, 20d_price float, 25d_price float, 60d_price float, 100d_price float, 5d_vol INT, 20d_vol INT)'
     print(v_sqlcommand)
     v_cursor.execute(v_sqlcommand)
   except Exception as e:
        print(str(e))
        sys.exit()



# fill data to each stock db
   try:
        stock = twstock.Stock(v_stockcode)
        v_stockInfo = stock.fetch_from(2018,1)
   except Exception as e:
        print(str(e))
        sys.exit()
   
   time.sleep(50)
   aver5 = Aver(5)
   aver10 = Aver(10)
   aver20 = Aver(20)
   aver25 = Aver(25)
   aver60 = Aver(60)
   aver100 = Aver(100)
   aver5dVol = Aver(5)
   aver20dVol = Aver(20)

   for each_record in v_stockInfo:
       v_date = each_record.date.date()
       v_vol = each_record.capacity
       if v_vol == 0 :
           continue
       v_high = each_record.high
       v_low = each_record.low
       v_price = each_record.close
       v_diff = each_record.change
       aver5.Addnew(v_price)
       aver10.Addnew(v_price)
       aver20.Addnew(v_price)
       aver25.Addnew(v_price)
       aver60.Addnew(v_price)
       aver100.Addnew(v_price)
       v_aver5 = aver5.GetAver()
       v_aver10 = aver10.GetAver()
       v_aver20 = aver20.GetAver()
       v_aver25 = aver25.GetAver()
       v_aver60 = aver60.GetAver()
       v_aver100 = aver100.GetAver()
       aver5dVol.Addnew(v_vol)
       aver20dVol.Addnew(v_vol)
       v_aver5dVol = aver5dVol.GetAver()
       v_aver20dVol = aver20dVol.GetAver()
       v_sqlcommand = 'INSERT INTO ID_' + v_stockcode + '(Tdate, capacity, high, low, price, diff, 5d_price, 10d_price, 20d_price, 25d_price, 60d_price, 100d_price, 5d_vol, 20d_vol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
       v_sqlinservalue = (v_date, v_vol, v_high, v_low, v_price, v_diff, v_aver5, v_aver10, v_aver20, v_aver25, v_aver60, v_aver100, v_aver5dVol, v_aver20dVol)
       v_cursor.execute(v_sqlcommand, v_sqlinservalue)
    #    print (v_sqlcommand)
    #    print (v_sqlinservalue)
   mydb.commit()

