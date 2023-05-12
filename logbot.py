import requests, os


DISCORD_LOGS_URL = os.environ['DISCORD_LOGS_URL']

DISCORD_ERR_URL = os.environ['DISCORD_ERR_URL']

DISCORD_AVATAR_URL = os.environ['DISCORD_AVATAR_URL']

DISCORD_STUDY_URL = os.environ['DISCORD_STUDY_URL']

DISCORD_STUDY_AVATAR_URL = os.environ['DISCORD_STUDY_AVATAR_URL']


logs_format = {
	"username": "Order Trade Logs",
	"avatar_url": DISCORD_AVATAR_URL,
	"content": ""
}

study_format = {
	"username": "Tradingview Alert",
	"avatar_url": DISCORD_STUDY_AVATAR_URL,
	"content": ""
}

def logs(message, error=False, log_to_discord=True):
    print(message)
    if log_to_discord:
        try:
            json_logs = logs_format
            json_logs['content'] = message
            if error:
                requests.post(DISCORD_ERR_URL, json=json_logs)
            else:
                requests.post(DISCORD_LOGS_URL, json=json_logs)
        except:
            pass

def study_alert(message, chart_url):
    try:
        json_logs = study_format
        json_logs['content'] = ">>> " + message + " \n\n" + chart_url
        requests.post(DISCORD_STUDY_URL, json=json_logs)
    except Exception as e:
        logs('>>> /!\ An exception occured : {}'.format(e), True)
        pass
