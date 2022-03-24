import keyring
import sys
import requests


TRADE_IDS = []


username = keyring.get_password("nmc", "currentuser")
csrftoken = None
sessionid = None
if username:
    csrftoken = keyring.get_password("nmc", "csrftoken")
    sessionid = keyring.get_password("nmc", "sessionid")

if not csrftoken or not sessionid:
    print("Couldn't sign in using existing credentials. Exiting...")
    sys.exit(1)

session = requests.Session()
session.cookies['csrftoken'] = csrftoken
session.cookies['sessionid'] = sessionid
session.headers['X-CSRFToken'] = csrftoken

for trade in TRADE_IDS:
    session.headers['Referer'] = "https://www.neonmob.com/jojojo8359/collection/?view-trade=" + str(trade)
    print('Trade #' + str(trade))
    r = session.post('https://www.neonmob.com/api/trades/' + str(trade) + '/accept/')
    print(r.json())
    r.raise_for_status()
