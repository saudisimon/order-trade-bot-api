import logbot
import json, os
from flask import Flask, request
from orderapi import order

app = Flask(__name__)

@app.route("/")
def hello_trader():
    print('RESTART WORKER')
    return "<p>Hello! You Alive</p>"

@app.route("/tradingview-to-webhook-order", methods=['POST'])
def tradingview_webhook():    
    data = json.loads(request.data)

    webhook_passphrase = os.environ['WEBHOOK_PASSPHRASE']

    if 'passphrase' not in data.keys():
        logbot.logs("No passphrase entered", True)
        return {
            "success": False,
            "message": "no passphrase entered"
        }
    if data['passphrase'] != webhook_passphrase:
        logbot.logs("Invalid passphrase", True)
        return {
            "success": False,
            "message": "invalid passphrase"
        }

    try:
        orders = order(data)
        if 'success' in orders.keys() and orders['success'] == False:
            logbot.logs('Stopped trade due to exception!')
            logbot.logs('Exception: Can not place order!\nMessage: {}'.format(orders['error']) +'\n\nRequest data: ' + json.dumps(data), True)
            return orders
        logbot.logs(json.dumps(orders))
        signal_data = logbot.convert_orders_to_trade_signal(orders['orders'])
        logbot.trade_signal(signal_data)
    except Exception as e:
        logbot.logs('Stopped trade due to exception!')
        logbot.logs('Exception: Can not place order!\nMessage: {}'.format(e) +'\n\nRequest data: ' + json.dumps(data), True)
    return orders

@app.route("/tradingview-to-discord-study", methods=['POST'])
def discord_study_tv():    
    data = json.loads(request.data)

    webhook_passphrase = os.environ['WEBHOOK_PASSPHRASE']

    if 'passphrase' not in data.keys():
        logbot.logs("No passphrase entered", True)
        return {
            "success": False,
            "message": "no passphrase entered"
        }

    if data['passphrase'] != webhook_passphrase:
        logbot.logs("Invalid passphrase", True)
        return {
            "success": False,
            "message": "invalid passphrase"
        }
    del data["passphrase"]

    try:
        if 'action' in data.keys() and 'message' in data.keys() and 'ticker' in data.keys():
            if data['action'] == 'buy':
                action = 'Buy'
            elif data['action'] == 'sell':
                action = 'Sell'
            else:
                return {
                    "success": False
                }
            if data['message'] == 'exit':
                action = 'Close ' + action
            elif data['message'] != 'entry':
                return {
                    "success": False
                }
            signal_data = logbot.convert_request_to_trade_signal(data)
            logbot.trade_signal(signal_data)
        else:
            logbot.logs('Request data is invalid!\nRequest data: ' + json.dumps(data))
            return {
                "success": False
            }
    except Exception as e:
        logbot.logs('Exception: Can not place order!\nMessage: {}'.format(e) +'\n\nRequest data: ' + json.dumps(data), True)
        return {
            "success": False
        }

    return {
        "success": True
    }
