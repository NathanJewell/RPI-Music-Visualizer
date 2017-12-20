import pyaudio
import numpy as np
import pylab
import time
import colorsys
import socket
import json

import os
#pip install git+https://github.com/Pithikos/python-websocket-server
from websocket_server import WebsocketServer
import threading

#web configs
HOST = '192.168.0.26'        # Symbolic name meaning all available interfaces
PORT = 12345     # Arbitrary non-privileged port

s = socket.socket()

def list_devices():
    # List all audio input devices
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(str(i)+'. '+dev['name']+"  rate: " + str(dev['defaultSampleRate']))
        i += 1

def normalizeFreq(freq, low=0, high=1):
    low = fMAX * low + fMIN
    high = fMAX * high
    return (np.clip(int(freq), low, high)-low)/(high-low)

def sigmoid(v, shift=0, steepness=7, zero=False): #v is between 0 and 1
    zeroshift = sigmoid(0, steepness=steepness) if zero else 0
    s2 = sigmoid(0, steepness, shift) if zero else 0
    return (1+2*zeroshift)/(1+pow(2.718, -steepness*(v-.5-shift))) - zeroshift - s2
def invsigmoid(v, shift=0, steepness=7, one=False):
    oneshift = invsigmoid(0, shift, steepness) if zero else 0

    return (-1-2*oneshift)/(1+pow(2.718, -steepness*(v-.5-shift)))+1+oneshift

def hsv(s, start=0, inv=False):
    h = start-s if inv else start+s
    if h < 0:
        h = 1 + h
    elif h > 1:
        h = 0 + (h-1)
    rgb = colorsys.hsv_to_rgb(h, 1, 1)
    return (rgb[0] * 255,
    rgb[1] * 255,
    rgb[2] * 255)

class StripAnimation:
    #audio processing configs
    RATE = 44100
    CHUNK = int(RATE/100)-1 # RATE / number of updates per second

    NUMLED = 240
    MAX_AMP = 255
    line_ratio_max = 0
    line_ratio_avg = 0
    line_ratio = 5
    line_ratios = []

    LOW = .1
    MID = .6
    HIGH = 1

    #maximum and minimum for normalizing frequencies
    fMAX = 3000
    fMIN = 20

    rainbow = False #whether rainbow should be used (freq controls hue)
    rainbowStartValue = .7 #where rainbow should start in hue
    rainbowInversion = True #if normalized frequency should be inverted

    frequencySaturation = False #whether saturation should be freq controlled
    individualLEDAmplitudes = False #whether individual amplitudes should be displayed

    defaultBaseColor = (255, 0, 0) #base color to be used
    bassColor = (0, 0, 255)
    midColor = (0, 255, 0)
    highColor = (255, 0, 0)

    useBassDeppression = False
    useMidDeppression = False
    useHighDeppression = False

    def setRainbow(self, value):
        self.rainbow = bool(value)
    def setRainbowStartValue(self, value):
        self.rainbowStartValue = float(value)
    def setRainbowInversion(self, value):
        self.rainbowInversion = bool(value)
    def setFrequencySaturation(self, value):
        self.frequencySaturation = bool(value)
    def setIndividualLEDAmplitudes(self, value):
        self.individualLEDAmplitudes = bool(value)
    def setDefaultBaseColor(self, value):
        self.defaultBaseColor= (int(rgb) for rgb in value.split(","))
    def setBassColor(self, value):
        self.bassColor = (int(rgb) for rgb in value.split(","))
    def setMidColor(self, value):
        self.midColor = (int(rgb) for rgb in value.split(","))
    def setHighColor(self, value):
        self.highColor = (int(rgb) for rgb in value.split(","))
    def setUseBassDeppression(self, value):
        self.useBassDeppression = bool(value)
    def setUseMidDeppression(self, value):
        self.useMidDeppression = bool(value)
    def setUseHighDeppression(self, value):
        self.useHighDeppression = bool(value)
    def setNumLED(self, value):
        self.NUMLED = int(value)

    changeDict = {}
    currentDict = {}

    def __init__(self):
        changeDict = {
            "rainbow" : a.setRainbow,
            "rainbowStartValue" : a.setRainbowStartValue,
            "rainbowInversion" : a.setRainbowInversion,
            "frequencySaturation" : a.setFrequencySaturation,
            "individualLEDAmplitudes" : a.setIndividualLEDAmplitudes,
            "defaultBaseColor" : a.setDefaultBaseColor,
            "bassColor" : a.setBassColor,
            "midColor" : a.setMidColor,
            "highColor" : a.setHighColor,
            "useBassDeppression" : a.setUseBassDeppression,
            "useMidDeppression" : a.setUseMidDeppression,
            "useHighDeppression" : a.setUseHighDeppression,

        }
        currentDict =  {
            "rainbow" : self.rainbow,
            "rainbowStartValue" : self.rainbowStartValue,
            "rainbowInversion" : self.rainbowInversion,
            "frequencySaturation" : self.frequencySaturation,
            "individualLEDAmplitudes" : self.individualLEDAmplitudes,
            "defaultBaseColor" : self.defaultBaseColor,
            "bassColor" : self.bassColor,
            "midColor" : self.midColor,
            "highColor" : self.highColor,
            "useBassDeppression" : self.useBassDeppression,
            "useMidDeppression" : self.useMidDeppression,
            "useHighDeppression" : self.useHighDeppression,
        }




a = StripAnimation()

manipulation functions
def resetAnim():
    pass




def getFreq(data, low=0, high=1, normalize=True):
    #https://stackoverflow.com/questions/2648151/python-frequency-detection
    # Take the fft and square each value
    global a
    fftData=abs(np.fft.rfft(data))**2
    # find the maximum
    which = fftData[int(1+len(fftData)*low):int(len(fftData)*high)].argmax() + 1
    # use quadratic interpolation around the max
    if which != len(fftData)-1:
        y0,y1,y2 = np.log(fftData[which-1:which+2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        thefreq = (which+x1)*a.RATE/a.CHUNK
    else:
        thefreq = which*a.RATE/a.CHUNK

    return normalizeFreq(thefreq, low, high) if normalize else thefreq

def soundplot(data):
    length = len(data)
    RATIO = int(length/a.NUMLED)
    highest_line = 0
    global line_ratio, line_ratios, line_ratio_max, line_ratio_avg

    count = 0
    maximum_item = 0
    max_array = []

    maxi = 0;
    for i in range(NUMLED):
        d = abs(data[i*RATIO])

        max_array.append(d/line_ratio)

        if d > highest_line:
            highest_line = d
            maxi = i

    current_line_ratio = highest_line/MAX_AMP;
    line_ratios.append(current_line_ratio)
    if(len(line_ratios) > 30):
        line_ratios.pop(0)


    if (current_line_ratio > line_ratio_max):
        line_ratio_max = highest_line/MAX_AMP

    line_ratio_avg = sum(line_ratios)/len(line_ratios)
    line_ratio = max((line_ratio_max+line_ratio_avg)/2, current_line_ratio)


    freqs = (getFreq(data, 0, LOW), getFreq(data, LOW, MID), getFreq(data, MID, HIGH)) #normalized relative frequencies

    low = max_array[:int(NUMLED*LOW)]
    mid = max_array[int(NUMLED*LOW):int(NUMLED*MID)]
    high = max_array[int(NUMLED*MID):int(NUMLED*HIGH)]

    amps = (sum(low)/len(low), sum(mid)/len(mid), sum(high)/len(high))
    return (max_array, freqs, amps, getFreq(data),);



def colorize(d):
    global a

    data = d[0]
    freqs = d[1]
    amps = d[2]
    frequency = d[3]

    freqcolors = (a.lowColor, a.midColor, a.highColor) #low, mid, high
    basecolor =  a.defaultBaseColor

    data = [v/255 for v in data]    #normalize
    colors = []

    if rainbow:
        basecolor = hsv(frequency, .7, True)
    avgIntensity = sum(data)/len(data)
    for i in range(0, len(data)): #bass is bluer, high is redder
        intensity = pow(avgIntensity, 1)# * pow(data[i], .5)
        r = basecolor[0]*intensity#freqratio*255
        g = basecolor[1]*intensity#colorratio*255
        b = basecolor[2]*intensity

        colors.append(r)
        colors.append(g)
        colors.append(b)


    def depression(p, s, c, m=1): #position and size and color
        p = int(p)
        s = int(s)
        for i in range(p-s, p+s):
            if(i > 0 and i*3 < len(colors)):
                #r = abs(p-i)/s
                d=1 #decay
                colors[i*3] +=  c[0]*d*m
                colors[i*3 + 1] += c[1]*d*m
                colors[i*3 + 2] += c[2]*d*m
    #depression(BARS/3, int(avgIntensity)*(BARS//2), (0, 0, 100), (sum(data)/len(data)));
    if a.useBassDeppression:
        depression((BARS//6), (1-freqs[0])*15, freqcolors[0], amps[0]/255)
    if a.useMidDeppression:
        depression(BARS//3,  freqs[1]*10, freqcolors[1], amps[1]/255)
    if a.useHighDeppression:
        depression(BARS//1.5, (freqs[2])*10, freqcolors[2], amps[2]/255)

    return colors

def setAnimation(message): #& seperates fields, : seperates key value, "," seperates value elements
    global a
    response = ""
    def makeChange(key, value):
        if key in a.changeDict:
            a.changeDict[key](value)
        else:
            response += "INFO: Key (" + key + ") not found or changed\n"
    data = message.split("&")
    things = json.loads(message)
    for key, val in things.items():
        makeChange(key, val)

if __name__=="__main__":

    list_devices();
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK)

    #websocketserver function
    ledColorData = ""
    streamData = 0
    leds = []
    webclients = []
    def clientJoin(client, server):
        print("Client Joined")

    def clientLeave(client, server):
        print("Client Left")

    def message(client, server, message):
        if message == "ping":
            server.send_message(client, "pong")
        elif message == "sendLEDS":
            server.send_message(client, "sending LEDS")
            print("New LED Client")
            leds.append(client)
        elif message == "data":
            s.send_message(client, ledColorData)
        elif message.split("!")[0] == "setanimation":
            setAnimation(message.split("!")[1])
        elif message == "webclient":
            webclients.push(client)
            s.send_message(client, )

    s = WebsocketServer(PORT, host=HOST)
    s.set_fn_new_client(clientJoin)
    s.set_fn_client_left(clientLeave)
    s.set_fn_message_received(message)

    def processAudio():
        global ledColorData
        try:
            while(True):
                chart = soundplot(streamData)
                response = colorize(chart)
                ledColorData = ",".join(str(int(e)) for e in response)


        except KeyboardInterrupt:
            print("Stopping Audio Logging")

    def streamAudio():
        global streamData
        while True:
            streamData = np.fromstring(stream.read(CHUNK), np.int16)

    def webclientUpdate():
        global a
        while True:
            time.sleep(5)
            data = json.dumps(a.currentDict)
            for c in s.clients:
                if c in webclients:
                    s.send_message(c, data)

    webclientUpdateThread = threading.Thread(target=webclientUpdate)
    webclientUpdateThread.start()
    print("Started: Web Client Update Thread")

    streamThread = threading.Thread(target=streamAudio)
    streamThread.start()
    print("Started: Audio Stream Thread")
    time.sleep(.5)

    audioThread = threading.Thread(target=processAudio)
    audioThread.start()
    print("Started: Audio Process Thread")
    time.sleep(.5)

    s.run_forever()
    print("Started: Websocket Server")



    stream.stop_stream()
    stream.close()
    p.terminate()
