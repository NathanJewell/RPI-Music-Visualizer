import pyaudio
import numpy as np
import time
import colorsys
import json
import math
import struct

import os
#pip install git+https://github.com/Pithikos/python-websocket-server
from websocket_server import WebsocketServer
import threading
from scipy.ndimage import filters

#web configs
HOST = '192.168.0.26'        # Symbolic name meaning all available interfaces
PORT = 12345     # Arbitrary non-privileged port


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
    low = a.fMAX * low + a.fMIN
    high = a.fMAX * high
    return (np.clip(int(freq), low, high)-low)/(high-low)

def sigmoid(v, shift=0, steepness=7, zero=False): #v is between 0 and 1
    zeroshift = sigmoid(0, steepness=steepness) if zero else 0
    s2 = sigmoid(0, steepness, shift) if zero else 0
    return (1+2*zeroshift)/(1+pow(2.718, -steepness*(v-.5-shift))) - zeroshift - s2
def invsigmoid(v, shift=0, steepness=7, one=False):
    oneshift = invsigmoid(0, shift, steepness) if one else 0

    return (-1-2*oneshift)/(1+pow(2.718, -steepness*(v-.5-shift)))+1+oneshift

def hsv(s, start=0, inv=False):
    h = start-s if inv else start+s
    if h < 0:
        h = 1 + h%1
    elif h > 1:
        h = 0 + (h%1-1)
    rgb = colorsys.hsv_to_rgb(h, 1, 1)
    return (rgb[0] * 255,
    rgb[1] * 255,
    rgb[2] * 255)

class StripAnimation:
    #audio processing configs
    RATE = 44100
    FPS = 20
    CHUNK = int(RATE/FPS) # RATE / number of updates per second

    NUMLED = 180
    MAX_AMP = np.zeros(NUMLED)
    VOLUME_ARR = np.zeros(300)

    line_ratio_max = 0
    VOLUME_MAX = 0
    line_ratio_max = 0
    line_ratio_avg = 0
    line_ratio = 5
    line_ratios = []

    LOW = .1
    MID = .6
    HIGH = 1

    #COMPUTED--------
    LOW = int(LOW*NUMLED)
    MID = int(MID*NUMLED)
    HIGH = int(HIGH*NUMLED)
    #----------


    #maximum and minimum for normalizing frequencies
    fMAX = 3000
    fMIN = FPS

    mirrored = True #whether display is mirrored down center
    frequencyRainbow = False #whether rainbow should be used (freq controls hue)
    timeBasedRainbow = True #whether color should vary with time
    stringRainbow = True #whether strip should be spectrum of itself
    useSigmoid = False #whether to invert two colors using sig and invsig
    timeBasedRainbowTime = 120000 #time to cycle through all colors
    rainbowStartValue = .66 #where rainbow should start in hue
    rainbowInversion = True #if normalized frequency should be inverted

    frequencySaturation = True #whether saturation should be freq controlled
    individualLEDAmplitudes = True #whether individual amplitudes should be displayed

    defaultBaseColor = (0, 0, 200) #base color to be used
    bassColor = (0, 0, 255)
    midColor = (0, 255, 0)
    highColor = (255, 0, 0)

    useBassDeppression = False
    useMidDeppression = False
    useHighDeppression = False

    def setFrequencyRainbow(self, value):
        self.frequencyRainbow = bool(value)
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
            "frequencyRainbow" : self.setFrequencyRainbow,
            "rainbowStartValue" : self.setRainbowStartValue,
            "rainbowInversion" : self.setRainbowInversion,
            "frequencySaturation" : self.setFrequencySaturation,
            "individualLEDAmplitudes" : self.setIndividualLEDAmplitudes,
            "defaultBaseColor" : self.setDefaultBaseColor,
            "bassColor" : self.setBassColor,
            "midColor" : self.setMidColor,
            "highColor" : self.setHighColor,
            "useBassDeppression" : self.setUseBassDeppression,
            "useMidDeppression" : self.setUseMidDeppression,
            "useHighDeppression" : self.setUseHighDeppression,

        }
        currentDict =  {
            "frequencyRainbow" : self.frequencyRainbow,
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

def getFreq(fftData, low=0, high=a.NUMLED, normalize=True):
    #https://stackoverflow.com/questions/2648151/python-frequency-detection
    # Take the fft and square each value

    # find the maximum
    which = fftData[(1+low):high].argmax() + 1
    # use quadratic interpolation around the max
    if which != len(fftData)-1:
        y0,y1,y2 = np.log(fftData[which-1:which+2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        thefreq = (which+x1+low)*a.RATE/a.CHUNK
    else:
        thefreq = (which+low)*a.RATE/a.CHUNK
    if math.isnan(thefreq):
        thefreq = 0
    return normalizeFreq(thefreq, low, high) if normalize else thefreq

def rms( data ):
    count = len(data)/2
    shorts =  data
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt( sum_squares / count )

def soundplotOLD(data):
    length = len(data)
    RATIO = int(length/a.NUMLED)
    highest_line = 0

    count = 0
    maximum_item = 0
    max_array = []

    maxi = 0;
    for i in range(a.NUMLED):
        d = abs(data[i*RATIO])

        max_array.append(d/a.line_ratio)

        if d > highest_line:
            highest_line = d
            maxi = i

    current_line_ratio = highest_line/a.MAX_AMP;
    a.line_ratios.append(current_line_ratio)
    if(len(a.line_ratios) > 30):
        a.line_ratios.pop(0)


    if (current_line_ratio > a.line_ratio_max):
        a.line_ratio_max = highest_line/a.MAX_AMP

    a.line_ratio_avg = sum(a.line_ratios)/len(a.line_ratios)
    a.line_ratio = max((a.line_ratio_max+a.line_ratio_avg)/2, current_line_ratio)


    freqs = (getFreq(data, 0, a.LOW), getFreq(data, a.LOW, a.MID), getFreq(data, a.MID, a.HIGH)) #normalized relative frequencies

    low = max_array[:int(a.NUMLED*a.LOW)]
    mid = max_array[int(a.NUMLED*a.LOW):int(a.NUMLED*a.MID)]
    high = max_array[int(a.NUMLED*a.MID):int(a.NUMLED*a.HIGH)]

    amps = (sum(low)/len(low), sum(mid)/len(mid), sum(high)/len(high))
    return (max_array, freqs, amps, getFreq(data),0);#old soundplotting before i realized how sound works

def logFFTData(data, base):
    target = a.NUMLED
    current = len(data)
    currentLog = math.log(current, base)
    indices = np.logspace(.5, currentLog, num=target, base=base)
    indices = indices.astype(int)
    which = 0
    count = 0
    ret = []
    for i in range(len(indices)): #using maximum from each block
        if(which == indices[i]):
            count+=1
        else:
            if count:
                m = np.average(data[which:(which+count)]) #find the maximum in the section
                for z in range(count):  #add proper number to the array
                    ret.append(m)
                #reset counters
            count = 0
            which = indices[i]


    return data[indices]


def soundplot(data):
    global a
    fftData=abs(np.fft.rfft(data))**2
    bandscale = 1000

    fftData = logFFTData(fftData[:int(len(fftData)*.8)], 2.71) #scale frequencies to reflect human logarithmic hearing scale

    bands = (fftData[:a.LOW],fftData[a.LOW:a.MID],fftData[a.MID:a.HIGH])

    frequencies = (
                getFreq(fftData, 0, a.LOW),
                getFreq(fftData, a.LOW, a.MID),
                getFreq(fftData, a.MID, a.HIGH))
    frequency = getFreq(fftData)

    amps = (bands[0]/np.max(bands[0]),
            bands[1]/np.max(bands[1]),
            bands[2]/np.max(bands[2]))
    #fftData = np.append(bands[0], [bands[1], bands[2]])
    fftData = fftData[:a.NUMLED]
    a.MAX_AMP = np.maximum(a.MAX_AMP, fftData)
    cMax = (a.MAX_AMP + fftData)/2
    fftData = np.divide(fftData, cMax)
    #fftData /= np.max(fftData)
    if a.mirrored:
        fftData = fftData[0::2].copy()
        close = np.fliplr([fftData])[0]
        fftData = np.append(close, fftData)

    volume = abs(np.average(data))
    if(volume > a.VOLUME_MAX):
        a.VOLUME_MAX = volume

    a.VOLUME_ARR = a.VOLUME_ARR[1:]
    a.VOLUME_ARR = np.append(a.VOLUME_ARR, volume)
    a.VOLUME_AVG = np.average(a.VOLUME_ARR)
    volume = volume/((a.VOLUME_MAX+a.VOLUME_AVG)/2)

    fftData = filters.gaussian_filter1d(fftData, .5)


    return (fftData, frequencies, amps, frequency, volume);

def colorize(d):
    global a

    data = d[0]
    freqs = d[1]
    amps = d[2]
    frequency = d[3]
    volume = d[4]

    freqcolors = (a.bassColor, a.midColor, a.highColor) #low, mid, high
    basecolor =  a.defaultBaseColor

    colors = []

    if a.timeBasedRainbow:
        basecolor = hsv((int(time.time()*1000)%a.timeBasedRainbowTime)/a.timeBasedRainbowTime, a.rainbowStartValue, a.rainbowInversion)

    if a.frequencyRainbow:
        basecolor = hsv(frequency, a.rainbowStartValue, a.rainbowInversion)
    avgIntensity = volume
    rainbow = []
    if(a.mirrored):
        rainbow = [hsv(i/(len(data)//2), a.rainbowStartValue, a.rainbowInversion) for i in range(len(data)//2)]
        rainbow.extend(np.fliplr([rainbow])[0])

    for i in range(0, len(data)): #bass is bluer, high is redder
        intensity = pow(avgIntensity, 1)
        if a.stringRainbow:
            basecolor = hsv(i/len(data), a.rainbowStartValue, a.rainbowInversion)
            if a.mirrored:
                basecolor = rainbow[i]

        if a.individualLEDAmplitudes:
            intensity = pow(data[i], .5)*pow(intensity, .7)
        if(a.useSigmoid):
            r = invsigmoid(avgIntensity)*basecolor[0]*intensity#freqratio*255
            g = sigmoid(avgIntensity)*basecolor[1]*intensity#colorratio*255
            b = basecolor[2]*intensity
        else:
            r = basecolor[0]*intensity #freqratio*255
            g = basecolor[1]*intensity #colorratio*255
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
    #depression(a.NUMLED//2, int(avgIntensity*(a.NUMLED//4)), hsv(avgIntensity), (sum(data)/len(data)));
    if a.useBassDeppression:
        depression((a.NUMLED//2), (amps[0]*25), freqcolors[0])
    if a.useMidDeppression:
        depression(a.NUMLED//3,  freqs[1]*10, freqcolors[1], amps[1]/255)
    if a.useHighDeppression:
        depression(a.NUMLED//1.5, (freqs[2])*10, freqcolors[2], amps[2]/255)

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
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=a.RATE,input=True,frames_per_buffer=a.CHUNK)

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
        time.sleep(3)
        global ledColorData
        while True:
            chart = soundplot(streamData)
            response = colorize(chart)
            ledColorData = ",".join(str(int(e)) for e in response)

    def streamAudio():
        global streamData
        audioThread = threading.Thread(target=processAudio)
        audioThread.start()
        print("Started: Audio Process Thread")
        time.sleep(.5)
        while True:
            streamData = np.fromstring(stream.read(a.CHUNK), np.int16)

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

    s.run_forever()
    print("Started: Websocket Server")



    stream.stop_stream()
    stream.close()
    p.terminate()
