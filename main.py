import requests
import json
import time
import subprocess

# PARAMS
API_URL = "https://www.alphavantage.co/query?function=global_quote&symbol={}.SA&outputsize=full&apikey=SUBSTITUA_SUA_KEY_AQUI"
WATCH_DELAY_MIN = 30
TIME_BETWEEN_REQUESTS = 10
START_PERC = 5/100
STOP_GAIN_PERC = 30/100
STOP_LOSS_PERC = 15/100

# COLORS
CEND = '\33[0m'
CBLINK = '\33[5m'
CWHITE = '\33[37m'
CGREEN = '\33[32m'
CBLUE = '\33[34m'
CYELLOW = '\33[33m'

# CONSTANTS
START = 0
STOP_GAIN = 1
STOP_LOSS = 2


def stock(ticket):
    price = 0
    respJson = _get(ticket)
    try:
        price = respJson['Global Quote']["05. price"]
    except KeyError:
        print("[{}] Error in quote {}".format(time.ctime(), ticket))

    return float(price)


def _get(ticket):
    # Wait between requests
    time.sleep(TIME_BETWEEN_REQUESTS)
    print("[{}] Analysing: {}".format(time.ctime(), ticket))

    respJson = None
    url = API_URL.format(ticket)
    try:
        resp = requests.get(url)
        respJson = json.loads(resp.content)
    except RuntimeError as e:
        print(e.__cause__)

    return respJson


def _log_notification(call, ticket, price):
    if(START == call):
        color = CBLUE
        title = 'START CALL'
    elif(STOP_GAIN == call):
        color = CGREEN
        title = 'STOP GAIN CALL'
    elif(STOP_LOSS == call):
        title = 'STOP LOSS CALL'
        color = CWHITE

    print(CBLINK + color +
          "[{}] ({}) - {} : R$ {}".format(time.ctime(), title, ticket, price) + CEND)


def _notify(call, ticket, price):
    if(START == call):
        title = 'START CALL'
        icon = 'face-devilish'
    elif(STOP_GAIN == call):
        title = 'STOP GAIN CALL'
        icon = 'face-cool'
    elif(STOP_LOSS == call):
        title = 'STOP LOSS CALL'
        icon = 'face-worried'

    _log_notification(call, ticket, price)

    info = "{} - R$ {}".format(ticket, price)
    subprocess.run(
        "notify-send '{}' '{}' --icon={}".format(title, info, icon), shell=True)


def watch_starts():
    starts = open('start.csv', 'r')
    for i in starts:
        ticket, base_price = i.split(',')[0].strip(), float(i.split(',')[1])
        current_price = stock(ticket)
        if _start_call(current_price, base_price):
            _notify(START, ticket, current_price)


def _start_call(current_price, base_price):
    if(current_price == 0):
        return False
    else:
        return current_price <= base_price - (base_price * START_PERC)


def watch_stops():
    stops = open('stop.csv', 'r')
    for i in stops:
        ticket, base_price = i.split(',')[0].strip(), float(i.split(',')[1])
        current_price = stock(ticket)
        if _stop_gain(current_price, base_price):
            _notify(STOP_GAIN, ticket, current_price)
        elif _stop_loss(current_price, base_price):
            _notify(STOP_LOSS, ticket, current_price)


def _stop_loss(current_price, base_price):
    if(current_price == 0):
        return False
    else:
        return current_price < base_price - (base_price * STOP_LOSS_PERC)


def _stop_gain(current_price, base_price):
    if(current_price == 0):
        return False
    else:
        return current_price > base_price + (base_price * STOP_GAIN_PERC)


def main():
    index = 0
    print("[{}] Starting Banpei-kun (ばんぺいくんRX)".format(time.ctime()))
    while True:
        print("[{}] Iteration {}".format(time.ctime(), index))
        index += 1

        print(CYELLOW+"[{}] Start Calls".format(time.ctime())+CEND)
        watch_starts()
        print(CYELLOW+"[{}] Stop Calls".format(time.ctime())+CEND)
        watch_stops()

        time.sleep(60*WATCH_DELAY_MIN)


if __name__ == '__main__':
    main()
