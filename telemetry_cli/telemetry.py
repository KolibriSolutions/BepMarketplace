import websocket
from telemetry_key import API_KEY
import argparse
import sys
import json
import os

def on_message(ws, message):
    try:
        data = json.loads(message)
    except:
        return

    with open('./data/{}.log'.format(data['user']), 'a') as stream:
        stream.write(message + '\n')

    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### Connection closed ###")

def on_open(ws):
    print("### Connection opened ###")
    # def run(*args):
    #     threading.Thread(target=run, args=()).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gather telemetry events from the marketplace system")
    parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')
    MODE = parser.parse_args().mode

    if MODE =='debug':
        domain = 'ws://localhost:8080'
    elif MODE == 'production':
        domain = 'wss://bep.ele.tue.nl'
    else:
        sys.exit(-1)

    if not os.path.exists("./data"):
        os.makedirs("./data")

    ws = websocket.WebSocketApp("{}/tracking/telemetry/{}/".format(domain, API_KEY),
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
