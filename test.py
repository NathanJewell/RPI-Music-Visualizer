import websocket
import _thread
import ssl

import time
#from neopixel import *
#from Queue import LifoQueue




def main():

    # Create NeoPixel object with appropriate configuration.
    #strip = null#Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize the library (must be called once before other functions).
    #strip.begin()

    HOST = 'ws://10.248.137.67:12345'
    PORT = 12345                   # The same port as used by the server
    endlast = 0
    def message(ws, message):
        #all messages larger than 20 characters will be interpreted as led data
        if(len(message) > 20):
            def setLeds():
                ledData = [int(e) for e in message.split(",")]
                #doLeds(strip, ledData)
                ws.send("data")


            #thread.start_new_thread(setLeds, ())

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
