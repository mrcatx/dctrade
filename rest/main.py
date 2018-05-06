import sys
import os
# lib_path = '%s/../'%os.getcwd()
# suffix = '/'.join(os.getcwd().split('/')[-2])
print(os.getcwd())
# print(suffix)
sys.path.append('/code/')
from flask import Flask
from flask_restful import Resource, Api
import dc_lib


app = Flask(__name__)
api = Api(app)
accounts = ['18011464336','18011466536']

class appraisement(Resource):
    def get(self):
        data = []
        for account in accounts:
            config = dc_lib.get_account_config(account)
            appraisement = config.get('appraisement',-1)
            usdt = config.get('usdt_stock',-1)
            ratio = round((appraisement-usdt)/appraisement*100,2)
            data.append({
                'account':account,
                'appraisement':appraisement,
                'usdt_stock':usdt,
                'ratio':ratio,
                'update_time':config['update_time']
            })
        return data

class vercode(Resource):
    def get(self):        
        data = []
        for account in accounts:
            config = dc_lib.get_account_config(account)
            data.append({
                'url':'%s/user/img_vercode/send/?usage=login&hwid=%s&time=1524155704389'%(dc_lib.dc_base_url,config['hwid']),
                'account':account
            })
        return data
        
        
api.add_resource(appraisement, '/appraisement')
api.add_resource(vercode, '/vercode')

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0',port=5000)