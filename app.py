import logbot
import json, os
from flask import Flask, request
from orderapi import order
import schedule

app = Flask(__name__)

@app.route("/")
def hello_trader():
    print('RESTART WORKER')
    return "<p>Hello! You Alive</p>"

@app.route("/tradingview-to-webhook-order", methods=['POST'])
def tradingview_webhook():

    logbot.logs("========= STRATEGY =========")
    
    data = json.loads(request.data)

    webhook_passphrase = os.environ['WEBHOOK_PASSPHRASE']

    if 'passphrase' not in data.keys():
        logbot.logs(">>> /!\ No passphrase entered", True)
        return {
            "success": False,
            "message": "no passphrase entered"
        }

    if data['passphrase'] != webhook_passphrase:
        logbot.logs(">>> /!\ Invalid passphrase", True)
        return {
            "success": False,
            "message": "invalid passphrase"
        }

    orders = order(data)
    print(orders)
    try:
        chart_url = 'https://www.tradingview.com'
        logbot.study_alert(json.dumps(orders), chart_url)
    except KeyError:
        logbot.logs(">>> /!\ Key 'chart_url' not found", True)
    return orders

@app.route("/tradingview-to-discord-study", methods=['POST'])
def discord_study_tv():

    logbot.logs("========== STUDY ==========")
    
    data = json.loads(request.data)

    webhook_passphrase = os.environ['WEBHOOK_PASSPHRASE']

    if 'passphrase' not in data.keys():
        logbot.logs(">>> /!\ No passphrase entered", True)
        return {
            "success": False,
            "message": "no passphrase entered"
        }

    if data['passphrase'] != webhook_passphrase:
        logbot.logs(">>> /!\ Invalid passphrase", True)
        return {
            "success": False,
            "message": "invalid passphrase"
        }
    del data["passphrase"]

    try:
        chart_url = data["chart_url"]
        del data["chart_url"]
        logbot.study_alert(json.dumps(data), chart_url)
    except KeyError:
        logbot.logs(">>> /!\ Key 'chart_url' not found", True)

    return {
        "success": True
    }
# try:
#     schedule.every(2).seconds.do(hello_trader)
# except Exception as e:
#     pass
# while True:
#     schedule.run_pending()