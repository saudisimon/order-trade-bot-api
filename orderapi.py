import logbot
import json, os
from ftxapi import Ftx
from bybitapi import ByBit

subaccount_name = 'SUBACCOUNT_NAME'
leverage = 1.0
risk = 1.0 / 100
api_key = 'API_KEY'
api_secret = 'API_SECRET'
testnet = True
discord_alert_format = ''


# ================== SET GLOBAL VARIABLES ==================


def global_var(payload):
    global subaccount_name
    global leverage
    global risk
    global api_key
    global api_secret
    global testnet
    global discord_alert_format

    subaccount_name = payload['subaccount']

    if subaccount_name == os.environ['API_SUB_ACCOUNT_NAME_TESTING']:
        testnet = True
        leverage = os.environ['LEVERAGE_TESTING']
        leverage = float(leverage)

        risk = os.environ['RISK_TESTING']
        risk = float(risk) / 100

        api_key = os.environ['API_KEY_TESTING']

        api_secret = os.environ['API_SECRET_TESTING']

    elif subaccount_name == os.environ['API_SUB_ACCOUNT_NAME']:
        testnet = False

        leverage = os.environ['LEVERAGE_MYBYBITACCOUNT']
        leverage = float(leverage)

        risk = os.environ['RISK_MYBYBITACCOUNT']
        risk = float(risk) / 100

        api_key = os.environ['API_KEY_MYBYBITACCOUNT']

        api_secret = os.environ['API_SECRET_MYBYBITACCOUNT']

    else:
        logbot.logs("Subaccount name not found", True)
        return {
            "success": False,
            "error": "subaccount name not found"
        }
           
    return {
        "success": True
    }


# ================== MAIN ==================


def order(payload: dict):
    #   DEFINE GLOBAL VARIABLE
    glob = global_var(payload)
    if not glob['success']:
        return glob
    
    init_var = {
        'subaccount_name': subaccount_name,
        'leverage': leverage,
        'risk': risk,
        'api_key': api_key,
        'api_secret': api_secret,
        'testnet': testnet,
        'open_side': payload['action']
    }
    exchange = payload['exchange']
    
    #   SET EXCHANGE CLASS
    exchange_api = None
    try:
        if exchange.upper() == 'FTX':
            exchange_api = Ftx(init_var)
        elif exchange.upper() == 'BYBIT':
            exchange_api = ByBit(init_var)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    logbot.logs('>>> Exchange : {}'.format(exchange))
    logbot.logs('>>> Subaccount : {}'.format(subaccount_name))

    #   FIND THE APPROPRIATE TICKER IN DICTIONNARY
    ticker = ""
    if exchange.upper() == 'BYBIT':
        ticker = payload['ticker']
    else:
        with open('tickers.json') as json_file:
            tickers = json.load(json_file)
            try:
                ticker = tickers[exchange.lower()][payload['ticker']]
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
    logbot.logs(">>> Ticker '{}' found".format(ticker))

    #   ALERT MESSAGE CONDITIONS
    if payload['message'] == 'entry':
        logbot.logs(">>> Order message : 'entry'")
        result = exchange_api.exit_position(ticker)
        if not result['success']:
            return result
        orders = exchange_api.entry_position(payload, ticker)
        return orders

    elif payload['message'] == 'exit':
        logbot.logs(">>> Order message : 'exit'")
        exit_res = exchange_api.exit_position(ticker)
        return exit_res

    elif payload['message'][-9:] == 'breakeven':
        logbot.logs(">>> Order message : 'breakeven'")
        breakeven_res = exchange_api.breakeven(payload, ticker)
        return breakeven_res
    
    else:
        logbot.logs(f">>> Order message : '{payload['message']}'")

    return {
        "message": payload['message']
    }
