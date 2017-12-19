import websocket

import time
import ssl
import _thread
from multiprocessing import Queue
def main():

    HOST = 'ws://192.168.0.26:12345'
    PORT = 12345                   # The same port as used by the server

    ledDataQueue = Queue(2)
    def message(ws, message):
        #all messages larger than 20 characters will be interpreted as led data
        if(len(message) > 20):
            if(ledDataQueue.qsize() > 0):
                ledDataQueue.get_nowait()

            ledDataQueue.put(message)
        else:
            print(message)

    def error(ws, error):
        print(error)

    def close(ws):
        print("Connection Close")

    def opener(ws):
        def setLeds(queue):
            while True:
                data = queue.get()
                print(data)
                if(len(data)):
                    ledData = [int(e) for e in data.split(",")]
                    doLeds(ledData)
        ws.send("sendLEDS") #tell webserver to send led info
        _thread.start_new_thread(setLeds, (ledDataQueue,))

    def connect():
        try:
            websocket.enableTrace(True)
            ws = websocket.WebSocketApp(HOST, on_message=message, on_error = error, on_close=close)
            ws.on_open = opener
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})
            time.sleep(3)
        except KeyboardInterrupt:
            exit()

    connect()



if __name__ == '__main__':
    main();
