g_coins = {"115": "QTUM"
    , "113": "EOS"
    , "108": "RCN"
    , "107": "TNB"
    , "125": "ABT"
    , "109": "LRC"
    , "110": "KNC"
    , "118": "CMT"
    , "124": "MEET"
    , "103": "ETH"
    , "101": "BTC"
    , "104": "DT"
    , "119": "CHT"
    ,'129':'NEO'
    ,'117':'SAFE'
    ,'111':'BCH'
    }

def get_code(coin_id):
    return g_coins[coin_id]

def get_id(coin_code):
    for k,v in g_coins.items():
        if  v == coin_code:
            return k