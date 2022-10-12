from websocket import create_connection
import json

ws = create_connection("wss://api2.poloniex_api.com:443")
ws.send('{"command" : "subscribe", "channel" : 1001}')

while True:
    result = ws.recv()
    json_result = json.loads(result)
    if len(json_result) >= 3:
        print(json_result)

ws.cache_c()
