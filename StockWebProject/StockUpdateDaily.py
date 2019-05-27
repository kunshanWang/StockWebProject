
from StockWebUtility import Aver
from StockWebUtility import MySqlObject
from StockWebUtility import StockUpdate


                    


Mysqlobject = MySqlObject('TWSTOCKDB', 'twstock')
Mysqlobject.ConnectDB()
StockObject = StockUpdate(Mysqlobject)
StockObject.UpdateAll('上市', 0)
StockObject.UpdateAll('上櫃', 0)