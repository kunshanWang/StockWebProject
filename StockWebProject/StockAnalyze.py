
from StockWebUtility import MySqlObject

Mysqlobject = MySqlObject('TWSTOCKDB', 'twstock')
Mysqlobject.ConnectDB()

# 5av > 20 av

result = Mysqlobject.Query5avOver20av()
print(len(result))
print(result)
