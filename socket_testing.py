import websockets
import asyncio
import time
from json import loads, dumps
from hmac import new as _new
from hashlib import sha512 as _sha512
from urllib.parse import urlencode as _urlencode

conf_api_key = '7AJJ71AC-Z8TU19W9-FRIJRHOK-YJALHGT2'
conf_api_secret = '5ff192325ba9e95afb686852f3c52deb19d28eb043e503d5062f18993465a2db91cee90d3f37b8fe83cd3e05b35c9655b378841df5f08097e8f469c25646dc14'


async def socket_client():
    try:
        async with websockets.connect('wss://api2.poloniex_api.com') as websocket:
            payload = _urlencode({'nonce': int(time.time() * 1000000000)})
            print(payload)
            sign = _new(
                conf_api_secret.encode('utf-8'),
                payload.encode('utf-8'),
                _sha512)

            channel_1000 = {
                "command": "subscribe",
                "channel": 1000,
                "key": conf_api_key,
                "payload": payload,
                "sign": sign.hexdigest(),
            }

            await websocket.send(dumps(channel_1000))

            while True:
                try:
                    message = await websocket.recv()
                    result = loads(message)
                    print(result)
                    if 'error' in result:
                        return False

                except Exception as e:
                    print("ORDER HANDLER: Potential Connection Error: " + str(repr(e)))

    except Exception as e:
        print("Connection Closed: " + str(repr(e)))
        raise SystemExit


def main():
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(socket_client())
        loop.run_forever()

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        loop.close()


if __name__ == "__main__":
    main()
