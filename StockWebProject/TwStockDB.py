m_debug = 0
import twstock
import sys
#stock = twstock.Stock('2330')
#print(stock.sid)

# create stock database
import mysql.connector

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="kusan",
        passwd="wqskusan@64"
        )
except:
    print("connect mysql error!")

mycursor = mydb.cursor()

try:
    mycursor.execute("CREATE DATABASE TWStockDB")
except:
    print("Database twstockdb already create!")

if (m_debug == 1):
    mycursor.execute("SHOW DATABASES")
    for x in mycursor:
        print(x)

v_createtablecur = mydb.cursor()
v_createtablecur.execute("USE TWStockDB")
# stockIDlist = stock.Keys();



#create stock table
v_sqlcommand = "CREATE TABLE TWSTOCK(type VARCHAR(256),code VARCHAR(40) PRIMARY KEY, name VARCHAR(256), start VARCHAR(40), market VARCHAR(40), classify VARCHAR(40))"

try:
    v_createtablecur.execute(v_sqlcommand)
except Exception as e:
    print(str(e))
    sys.exit()


v_stockkeylist = twstock.codes.keys()
v_stockid = "6411"

if (m_debug ==1):
    print(v_stockkeylist)
    v_stockInfo = twstock.codes.get(v_stockid)
    print(v_stockInfo)
    print(v_stockInfo.type)
    print(v_stockInfo.code)
    print(v_stockInfo.name)
    print(v_stockInfo.ISIN)
    print(v_stockInfo.start)
    print(v_stockInfo.market)
    print(v_stockInfo.group)

#insert data to twstock table


#v_stockid = "6411"
#v_stockInfo = twstock.codes.get(v_stockid)
#v_sqlcommand = "INSERT INTO TWSTOCK(type, code, name, start, market, classify) VALUES (%s, %s, %s, %s, %s, %s)"
#v_sqlinservalue = (v_stockInfo.type, v_stockInfo.code, v_stockInfo.name, v_stockInfo.start, v_stockInfo.market, v_stockInfo.group)
#v_createtablecur.execute(v_sqlcommand, v_sqlinservalue)


for v_stockid in v_stockkeylist:
    v_stockInfo = twstock.codes.get(v_stockid)
    print(v_stockid)
    v_sqlcommand = "INSERT INTO TWSTOCK(type, code, name, start, market, classify) VALUES (%s, %s, %s, %s, %s, %s)"
    v_sqlinservalue = (v_stockInfo.type, v_stockInfo.code, v_stockInfo.name, v_stockInfo.start, v_stockInfo.market, v_stockInfo.group)
    v_createtablecur.execute(v_sqlcommand, v_sqlinservalue)
 

mydb.commit()