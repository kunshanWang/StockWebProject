import twstock
import sys
import mysql.connector
import datetime
import time
from flask_socketio import SocketIO, emit

class StockWebUtility(object):
    """description of class"""

class Aver:
    def __init__(self, count):
        self.count = count
        self.val = [0]
        for x in range(count-1):
            self.val.append(0)

    def Addnew(self, count):
        if count == None:
            count = 0
        self.val.insert(0, count)
        self.val.pop()

    def Printall(self):
        for x in range(self.count):
            print(self.val[x])
        

    def GetAver(self):
        sum = 0
        for x in range(self.count):
            sum += self.val[x]
        return sum/self.count


class MySqlObject:
    
    mysqlhost='localhost'
    mysqluser='kusan'
    mysqlpasswd='wqskusan@64'

    def __init__(self, dbname, stocktable):
        self.dbname = dbname
        self.stocktable = stocktable

    def ConnectDB(self):
        self.mydb = mysql.connector.connect(
        host=self.mysqlhost,
        user= self.mysqluser,
        passwd=self.mysqlpasswd,
        database=self.dbname
        )
        self.cursor = self.mydb.cursor()

    def ConnectDBWCB(self, socketio):
        socketio.emit('log', 'MySqlObject:connect')
        self.mydb = mysql.connector.connect(
        host=self.mysqlhost,
        user= self.mysqluser,
        passwd=self.mysqlpasswd,
        database=self.dbname
        )
        self.cursor = self.mydb.cursor()


    def GetStockId(self, type):
        
#        strsqlcommand = "select code from " + self.stocktable + " (where market ='上市')"  + " and type = '股票'"

 #       if bool(type):            
        strsqlcommand = "select code from " + self.stocktable + " where market ='" + type + "' and type = '股票'"
        
        self.cursor.execute(strsqlcommand)
        v_tablelist = [item[0] for item in self.cursor.fetchall()]
        print ("update stock num:" + str(len(v_tablelist)))
        return v_tablelist

    def GetLastDateInTable(self, tableid):
        strsqlcommand = "select max(tdate) from id_" + tableid
        self.cursor.execute(strsqlcommand)
        v_result = self.cursor.fetchone()
        return v_result[0]

    def GetColumnDataLatest(self, tableid, aver, column_name, num):
         strsqlcommand = "select Count(*) from id_" + tableid
         self.cursor.execute(strsqlcommand)
         totalrow = self.cursor.fetchone()[0]
         offest = 0
         if totalrow > num :
            offest = totalrow-num
         strsqlcommand = "select " + column_name +" from id_" + tableid + " LIMIT " + str(num) +" OFFSET " + str(offest)
         self.cursor.execute(strsqlcommand)
         v_queryList = self.cursor.fetchall()
         for x in v_queryList:
             aver.Addnew(x[0])

    def AddnewData(self, sqlcommand, sqlinservalue):
        self.cursor.execute(sqlcommand, sqlinservalue)    

    def QueryDB(self, sqlcommand):
        self.cursor.execute(sqlcommand)
        return self.cursor.fetchall()
    
    def UpdateDB(self, sqlcommand):
        self.cursor.execute(sqlcommand)
    
    def QueryCondiction(self, QP1, QOP, QP2):
        strsqlcommand = 'show tables'
        self.cursor.execute(strsqlcommand)

        v_tablelist = [item[0] for item in self.cursor.fetchall()]
        result = ["0"]
        for eachid in v_tablelist:
            if eachid == "twstock" or eachid =='checklist':
                continue
            
            strsqlcommand = "select "+ QP1 + " from " + eachid + " order by Tdate Desc limit 2"
            queryresultQP1 = self.QueryDB(strsqlcommand)
            QP1list = [item[0] for item in queryresultQP1]

            strsqlcommand = "select "+ QP2 + " from " + eachid + " order by Tdate Desc limit 2"
            queryresultQP2 = self.QueryDB(strsqlcommand)
            QP2list = [item[0] for item in queryresultQP2]

            if QOP == "Large":
                if QP1list[0] > QP2list[0] and QP1list[1] < QP2list[1] :
                    result.append(str(eachid))
            else: 
                if QP1list[0] < QP2list[0] and QP1list[1] > QP2list[1] :
                    result.append(str(eachid))

        result.pop(0)
        return result


    # query if 5day over 20av
    def Query5avOver20av(self):
        return self.QueryCondiction("5d_price", "Large", "20d_Price")

    def Query5avOver20avold(self):
        strsqlcommand = 'show tables'
        self.cursor.execute(strsqlcommand)

        v_tablelist = [item[0] for item in self.cursor.fetchall()]
        result = ["0"]
        for eachid in v_tablelist:
            # get 5av
            if eachid == "twstock" or eachid =='checklist':
                continue
            strsqlcommand = "select 5d_price from " + eachid + " order by Tdate Desc limit 2"
            queryresult = self.QueryDB(strsqlcommand)
            #self.cursor.execute(strsqlcommand)
            lisprice5d = [item[0] for item in queryresult]
            # get 20av
            strsqlcommand = "select 20d_price from " + eachid + " order by Tdate Desc limit 2"
            #self.cursor.execute(strsqlcommand)
            queryresult = self.QueryDB(strsqlcommand)
            lisprice20d = [item[0] for item in queryresult]

            if lisprice5d[0] > lisprice20d[0]: 
                if lisprice5d[1] < lisprice20d[1]:
                    result.append(str(eachid))
        
        
        result.pop(0)
        return result

    def DbCommit(self):
        self.mydb.commit()


class StockUpdate:

    def __init__(self, mysqlobject):
        self.mysql = mysqlobject

    def UpdateAll(self, type, start, socketio = None):
        stockidlist = self.mysql.GetStockId(type)
        strsqlcommand = "select itemvalue from checklist where checkitem = 'lastUpdate'"
        queryresult = self.mysql.QueryDB(strsqlcommand)
        lastupdate = queryresult[0]
        if socketio != None:
           socketio.emit('log', 'StockUpdate Updateall')
           
        startcounter = 0
        for eachid in stockidlist:
            startcounter = startcounter + 1
            if socketio != None:
                socketio.emit('Progress', str(startcounter) + '/' + str(len(stockidlist)))

            if eachid == "twstock" or eachid =='checklist':
                continue
            if int(eachid) < start:
                continue
            if socketio != None:
                socketio.emit('log', 'checking id:' + eachid)
           

            latestdateinDB = self.mysql.GetLastDateInTable(eachid)
            print(latestdateinDB)
            nowdate = datetime.datetime.now().date()
            
 #           print(nowdate)
            aver5 = Aver(5)
            aver10 = Aver(10)
            aver20 = Aver(20)
            aver25 = Aver(25)
            aver60 = Aver(60)
            aver100 = Aver(100)
            aver5dVol = Aver(5)
            aver20dVol = Aver(20)

            self.mysql.GetColumnDataLatest(eachid, aver5, "price", 5)
            self.mysql.GetColumnDataLatest(eachid, aver10, "price", 10)
            self.mysql.GetColumnDataLatest(eachid, aver20, "price", 20)
            self.mysql.GetColumnDataLatest(eachid, aver25, "price", 25)
            self.mysql.GetColumnDataLatest(eachid, aver60, "price", 60)
            self.mysql.GetColumnDataLatest(eachid, aver100, "price", 100)
            self.mysql.GetColumnDataLatest(eachid, aver5dVol, "capacity", 5)
            self.mysql.GetColumnDataLatest(eachid, aver20dVol, "capacity", 20)
 #           print("aver5:" + str(aver5.GetAver()))
 #           print("aver10:" + str(aver10.GetAver()))
 #           print("aver20:" + str(aver20.GetAver()))
 #           print("aver20dvol:" + str(aver20dVol.GetAver()))

            if nowdate > latestdateinDB:
                v_year = latestdateinDB.strftime("%Y")
                v_month = latestdateinDB.strftime("%m")
             
 #               if int(eachid) < int(lastupdate) and int(lastupdate) != 10000 : 
 #                   continue

                for x in range(0,8) :
                    try:
                        v_stock = twstock.Stock(eachid)
                        v_stockInfo = v_stock.data
                        if nowdate > latestdateinDB + datetime.timedelta(days = 31):
                            v_stockInfo = v_stock.fetch_from(int(v_year),int(v_month))
                    except Exception as e:
                        print("get stock data error! id:" + eachid)
                        time.sleep(2)
                        if x==7 :
                            print(str(e))
                            sys.exit()
                    else:
                        time.sleep(10)
                        break


                for each_record in v_stockInfo:
                    
                    if each_record.date.date() <= latestdateinDB:
                        continue
                    msg = "Update id:" + eachid + " update Data at " + each_record.date.date().strftime("%Y %m %d")
                    print(msg)
                    if socketio != None:
                        socketio.emit('log', 'update id:' + eachid)

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
                    v_sqlcommand = 'INSERT INTO ID_' + eachid + '(Tdate, capacity, high, low, price, diff, 5d_price, 10d_price, 20d_price, 25d_price, 60d_price, 100d_price, 5d_vol, 20d_vol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                    v_sqlinservalue = (v_date, v_vol, v_high, v_low, v_price, v_diff, v_aver5, v_aver10, v_aver20, v_aver25, v_aver60, v_aver100, v_aver5dVol, v_aver20dVol)
                    
                    self.mysql.AddnewData(v_sqlcommand, v_sqlinservalue)
    #                v_cursor.execute(v_sqlcommand, v_sqlinservalue)

    #    print(len(stockidlist))
    #   select max(tdate) from table
            strsqlcommand = "update checklist set itemvalue =" + eachid + " where checkitem = 'lastUpdate'"
            self.mysql.UpdateDB(strsqlcommand)
            lastupdate = eachid
            self.mysql.DbCommit()

        # reset lastupdate value to 10000 after commplete
        strsqlcommand = "update checklist set itemvalue = '10000' where checkitem = 'lastUpdate'"
        self.mysql.UpdateDB(strsqlcommand)


        


         
            


