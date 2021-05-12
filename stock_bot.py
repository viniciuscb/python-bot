import json
import re

import websocket
import csv
import requests

from urllib.request import urlopen

try:
    import thread
except ImportError:
    import _thread as thread


# checks if it is a stock query message, returns stock name or None
def get_stock_query(message_data):
    stock_name = None
    if message_data['model'] == 'chat.message':
        content = message_data['fields']['content']
        stock_command_match = re.match('^/stock=(.*)', content)
        if stock_command_match:
            stock_name = stock_command_match.groups()[0]
    return stock_name


def fetch_stock_information(stock_name):
    with requests.Session() as s:
        download = s.get(f"https://stooq.com/q/l/?s={stock_name}&f=sd2t2ohlcv&h&e=csv")

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        rows = list(cr)
        stock_value = rows[1][3]
        return stock_value


def on_message(ws, message):
    message_list = json.loads(message)
    for message_data in message_list:
        stock_name = get_stock_query(message_data)
        if stock_name is not None:
            stock_value = fetch_stock_information(stock_name)
            if stock_value is not None:
                if stock_value == "N/D":
                    stock_message = f"{stock_name.upper()} quote not found / not available"
                else:
                    stock_message = f"{stock_name.upper()} quote is ${stock_value} per share"
                ws.send(json.dumps({'message': stock_message}))


def on_error(ws, error):
    print(error)


def on_close(ws):
    connection_message = "stocks bot 2 disconnected"
    ws.send(json.dumps({'message': connection_message}))
    print("### closed ###")


def on_open(ws):
    connection_message = "stocks bot 2 connected"
    ws.send(json.dumps({'message': connection_message}))
    print("### connected ###")


if __name__ == "__main__":
    # websocket.enableTrace(True)

    host = "localhost:8000"
    authorization_token = input("Authorization token:")

    room_name = input("Connect to which room?")
    extra_headers = {"Authorization": f"Token {authorization_token}"}

    ws = websocket.WebSocketApp(f"ws://{host}/ws/chat/{room_name}/",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                header=extra_headers)

    ws.run_forever()
