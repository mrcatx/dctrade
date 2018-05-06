import sys
import dc_lib as dc
import dc_api_lib as api

account = sys.argv[1]
dc.set_account(account)
api.login(sys.argv[2])