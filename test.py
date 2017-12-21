import websocket
import _thread
import ssl

import time


def main():


    HOST = 'ws://192.168.0.26:12345'
    PORT = 12345                   # The same port as used by the server
    endlast = 0
    def message(ws, message):
        #all messages larger than 20 characters will be interpreted as led data
        rectime = time.time()*1000000
        if(len(message) > 20):
            def setLeds():
                global endlast
                start = time.time() * 1000000
                ledData = [int(e) for e in message.split(",")]
                d1 = time.time() * 1000000
                doLeds(strip, ledData)
                d2 = time.time() * 1000000
                ws.send("data")
                endthis = time.time() * 1000000
                print("transfer: " + str(rectime-endlast))
                print("process: " + str(end-start))
                print("sending: " + str(end-d2))
                print("putting: " + str(d2-d1))
                print("manipul: " + str(d1 - start))
                endlast=endthis

            _thread.start_new_thread(setLeds, ())

            #if ledDataQueue.full():
            #    ledDataQueue.get()
            #ledDataQueue.put(message)
        else:
            print(message)

    def error(ws, error):
        print(error)

    def close(ws):
        print("Connection Close")

    def opener(ws):
        ws.send("sendLEDS") #tell webserver to send led info
        ws.send("data")
        #thread.start_new_thread(setLeds, (ledDataQueue,))

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
