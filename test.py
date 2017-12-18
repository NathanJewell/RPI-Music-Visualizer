import websocket

import time
import ssl
def main():

    HOST = 'ws://192.168.0.26:12345'
    PORT = 12345                   # The same port as used by the server

    def message(ws, message):
        #all messages larger than 20 characters will be interpreted as led data
        if(len(message) > 20):
            data = [int(e) for e in message.split(",")]
            doLeds(strip, data)

    def error(ws, error):
        print(error)

    def close(ws):
        print("Connection Close")

    def opener(ws):
        ws.send("sendLEDS") #tell webserver to send led info

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(HOST, on_message=message, on_error = error, on_close=close)
    ws.on_open = opener
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})



if __name__ == '__main__':
    main();
