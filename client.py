import websocket
import thread
import ssl

import time
from neopixel import *
from Queue import LifoQueue


# LED strip configuration:
LED_COUNT      = 254      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

def doLeds(strip, data):
    for i in range(0, len(data)/3):
        strip.setPixelColor(i, Color(data[i*3], data[i*3+1], data[i*3+2]))
    strip.show();

def main():

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize the library (must be called once before other functions).
    strip.begin()

    HOST = 'ws://192.168.0.100:12345'
    PORT = 12345                   # The same port as used by the server
    endlast = 0
    def message(ws, message):
        #all messages larger than 20 characters will be interpreted as led data
        if(len(message) > 20):
            def setLeds():
                ledData = [int(e) for e in message.split(",")]
                doLeds(strip, ledData)
                ws.send("data")


            thread.start_new_thread(setLeds, ())

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
