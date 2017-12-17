import socket

import time
from neopixel import *


# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

def toRGB(val):
    c = 255/6;
    def R(v):
        if(v < (c)):
            return 0
        elif(v >= (c) and v <= (2*c)):
            return 255-((v-c)*6)
        elif(v > (2*c) and v < (4*c)):
            return 0;
        elif(v > (4*c) and v <= (5*c)):
            return (v-(4*c)*6);
        else:
            return 255;
    def G(v):
        if(v < (c)):
            return ((v-c)*6)
        elif(v >= (c) and v <= (3*c)):
            return 255
        elif(v > (3*c) and v < (4*c)):
            return 255-((v-(3*c))*6)
        else:
            return 0
    def B(v):
        if(v < (2*c)):
            return 0
        elif(v >= (2*c) and v <= (3*c)):
            return (v-(2*c))*6
        elif(v > (3*c) and v < (5*c)):
            return 255;
        else:
            return 255-((v-(5*c))*6)
    print(Color(R(val), G(val), B(val))
    return Color(R(val), G(val), B(val))

def doLeds(strip, data):
    for i in range(0, len(data)):
        strip.setPixelColor(i, toRGB(data[i]))
    strip.show();

def main():
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize the library (must be called once before other functions).
    strip.begin()

    host = '192.168.0.26'
    port = 12345                   # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    connected = True;
    while(connected):
        data = "led"
        s.send(data.encode())
        data = s.recv(1024).decode().split(",")
        data = [int(e) for e in data]
        doLeds(strip, data)
        print(data);
        print('Received', repr(data))
        if data == "END":
            s.close()

if __name__ == '__main__':
    main();
