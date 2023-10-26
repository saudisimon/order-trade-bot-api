import requests, os


DISCORD_LOGS_URL = os.environ['DISCORD_LOGS_URL']

DISCORD_ERR_URL = os.environ['DISCORD_ERR_URL']

DISCORD_AVATAR_URL = os.environ['DISCORD_AVATAR_URL']

DISCORD_STUDY_URL = os.environ['DISCORD_STUDY_URL']

DISCORD_STUDY_AVATAR_URL = os.environ['DISCORD_STUDY_AVATAR_URL']

trade_signal_log_format = {
	"username": "Lucas",
	"avatar_url": DISCORD_AVATAR_URL,
	"content": ""
}

trade_signal_format = {
	"username": "YaYa",
	"avatar_url": DISCORD_STUDY_AVATAR_URL,
	"content": ""
}

def logs(message, error=False, log_to_discord=True):
    print(message)
    if log_to_discord:
        try:
            json_logs = trade_signal_log_format
            json_logs['content'] = message
            if error:
                requests.post(DISCORD_ERR_URL, json=json_logs)
            else:
                requests.post(DISCORD_LOGS_URL, json=json_logs)
        except:
            pass

def trade_signal(message):
    try:
        json_logs = trade_signal_format
        json_logs['content'] = '@everyone' + message
        requests.post(DISCORD_STUDY_URL, json=json_logs)
    except Exception as e:
        logs('>>> An exception occured : {}'.format(e), True)
        pass

def convert_orders_to_trade_signal(orders):
    content = ''
    for order in orders:
        symbol = order['symbol']
        side = order['side']
        price = order['price']
        stop_loss = order['stop_loss']
        take_profit = order['take_profit']
        content = symbol + '  ' + side + '\n\nPrice: {}\n'.format(price)
        if stop_loss > 0:
            content = content + '\nSL: {}\n'.format(stop_loss)
        if take_profit > 0:
            content = content + '\nTP: {}\n'.format(take_profit)
    return content

def convert_request_to_trade_signal(order):
    content = ''
    symbol = order['ticker']
    side = order['action']
    content = symbol + '  ' + side + '\n'
    del order['ticker']
    del order['action']
    keys = order.keys()
    for key_name in keys:
        value = order[key_name]
        if isinstance(value, (int, float)) and value > 0:
            content = content + '\n{}'.format(key_name) + ': {}\n'.format(value)
        else:
            content = content + '\n{}'.format(key_name) + ': {}\n'.format(value)
    return content