import websocket

import time
import ssl
import _thread
def main():

    HOST = 'ws://192.168.0.26:12345'
    PORT = 12345                   # The same port as used by the server

    newData = []
    ledData = []
    def message(ws, message):
        #all messages larger than 20 characters will be interpreted as led data
        if(len(message) > 20):
            newData = message
        else:
            print(message)

    def error(ws, error):
        print(error)

    def close(ws):
        print("Connection Close")
        connect() #try and reconnect

    def opener(ws):
        def setLeds(*args):
            while True:
                ledData = newData
                doLeds([int(e) for e in ledData.split(",")])
        print("thread terminating...")
        _thread.start_new_thread(setLeds, ())
        ws.send("sendLEDS") #tell webserver to send led info

    def connect():
        try:
            websocket.enableTrace(True)
            ws = websocket.WebSocketApp(HOST, on_message=message, on_error = error, on_close=close)
            ws.on_open = opener
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})
        except KeyboardInterrupt:
            exit()

    connect()



if __name__ == '__main__':
    main();
