import twstock


class historical_data:
    def __init__(self, id):
        self.id = str(id)
        self.stock = twstock.Stock(id)
        self.price = self.stock.price[-20:]
        self.high = self.stock.high[-20:]
        self.low = self.stock.low[-20:]


# id_his = historical_data("股票代碼")
# id_his.price 呼叫20天收盤價list
# id_his.high 呼叫20天最高價list
# id_his.low 呼叫20天最低價list
