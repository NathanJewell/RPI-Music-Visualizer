import pyaudio
import numpy as np
import pylab
import time
import colorsys

import os
import logging
#pip install git+https://github.com/Pithikos/python-websocket-server
from websocket_server import WebsocketServer
import thread

#web configs
HOST = '192.168.0.26'        # Symbolic name meaning all available interfaces
PORT = 12345     # Arbitrary non-privileged port


#audio processing configs
RATE = 44100
CHUNK = int(RATE/20) # RATE / number of updates per second

BARS = 240
BAR_HEIGHT = 255
LINE_WIDTH = 5
line_ratio_max = 0
line_ratio_avg = 0
line_ratio = 0
line_ratios = []

LOW = 200
MID = 1500
HIGH = 2200

LOWP = int(LOW/HIGH * BARS)
MIDP = int(MID/HIGH * BARS)
HIGHP = BARS

def list_devices():
    # List all audio input devices
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(str(i)+'. '+dev['name'])
        i += 1

def getFreq(data): #https://stackoverflow.com/questions/2648151/python-frequency-detection
    # Take the fft and square each value
    fftData=abs(np.fft.rfft(data))**2
    # find the maximum
    which = fftData[1:].argmax() + 1
    # use quadratic interpolation around the max
    if which != len(fftData)-1:
        y0,y1,y2 = np.log(fftData[which-1:which+2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        thefreq = (which+x1)*RATE/CHUNK
    else:
        thefreq = which*RATE/CHUNK

    return thefreq



def soundplot(stream):
    t1=time.time()
    data = np.fromstring(stream.read(CHUNK), np.int16)
    fs = RATE

    length = len(data)
    RATIO = length/BARS
    highest_line = 0
    global line_ratio, line_ratios, line_ratio_max, line_ratio_avg

    count = 0
    maximum_item = 0
    max_array = []

    maxi = 0;
    for i in range(len(data)):
        d = data[i]

        if count < RATIO:
            count = count + 1

            if abs(d) > maximum_item:
                maximum_item = abs(d)
        else:
            max_array.append(maximum_item)

            if maximum_item > highest_line:
                highest_line = maximum_item
                maxi = i

            maximum_item = 0
            count = 1

    current_line_ratio = highest_line/BAR_HEIGHT;
    line_ratios.append(current_line_ratio)
    if(len(line_ratios) > 30):
        line_ratios.pop(0)


    if (current_line_ratio > line_ratio_max):
        line_ratio_max = highest_line/BAR_HEIGHT

    line_ratio_avg = sum(line_ratios)/len(line_ratios)
    line_ratio = max((line_ratio_max+line_ratio_avg)/2, current_line_ratio)
    #im = Image.new('RGBA', (BARS * LINE_WIDTH, BAR_HEIGHT), (255, 255, 255, 1))
    #draw = ImageDraw.Draw(im)

    current_x = 1
    final = [];
    for item in max_array:
        item_height = item/line_ratio
        final.append(item_height)

    lowf = data[:LOW]
    midf = data[LOW:MID]
    highf = data[MID:HIGH]

    freqs = (getFreq(lowf)/LOW, getFreq(midf)/(MID-LOW), getFreq(highf)/(HIGH-MID)) #normalized relative frequencies

    low = final[:LOWP]
    mid = final[LOWP:MIDP]
    high = final[MIDP:HIGHP]

    amps = (sum(low)/len(low), sum(mid)/len(mid), sum(high)/len(high))
    return (final, freqs, amps, getFreq(data));

last = False;

def colorize(d):
    global last
    data = d[0]
    freqs = d[1]
    #print("f: " + str(frequency))
    amps = d[2]
    frequency = d[3]

    #print("m: " + str(maxi))
    freqcolors = ((50, 0, 0), (100, 0, 0), (100, 0, 0)) #low, mid, high
    basecolor =  (0, 0, 0)
    smoothing = 0

    def sigmoid(v): #v is between 0 and 1
        return 1/(1+pow(2.718, -.2*(v-.5)))
    def invsigmoid(v):
        return -1/(1+pow(2.718, -.2*(v-.5)))+1

    def hsv(s):
        rgb = colorsys.hsv_to_rgb(s, 1, 1)
        return (rgb[0] * 255,
        rgb[1] * 255,
        rgb[2] * 255)

    data = [v/255 for v in data]    #normalize
    colors = []
    freqratio = (np.clip(int(frequency), 20, 2000)-20)/1980 #clamp and normalize

    if(last):
        basecolor = (50, 255, 255)
        time.sleep(.04)
    last = not last

    #basecolor = hsv(freqratio)
    for i in range(0, len(data)): #bass is bluer, high is redder

        intensity = 1#(pow(data[i], 1) + .5*smoothing)/(smoothing+1)
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
    #depression(BARS/3, int((sum(data)/len(data))*(BARS//2)), (0, 0, 100), (sum(data)/len(data)));
    #depression((BARS*freqs[0]), 20, freqcolors[0], amps[0]/255) #low one fourth
    #depression((BARS*freqs[1])/3 + BARS/3, 10, freqcolors[1], amps[1]/255) #mid two fourths
    #depression((BARS*freqs[2])/3 + (2*BARS)/3, 5, freqcolors[2], amps[2]/255) #high one fourth

    return colors

if __name__=="__main__":

    list_devices();
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK)

    lighters = []
    def clientJoin(client, server):
        pass

    def clientLeave(client, server):
        pass

    def message(client, server, message):
        if message == "ping":
            server.send_message(client, "pong")
        elif message == "sendLEDS":
            lighters.append(client)
            server.send_message(client, "sending LEDS")

    s = WebsocketServer(PORT, host=HOST, loglevel=loggin.INFO)
    s.set_fn_new_client(clientJoin)
    s.set_fn_client_left(clientLeave)
    s.set_fn_message_received(message)
    s.run_forever()


    while True:
        chart = soundplot(stream)
        response = colorize(chart)
        response = ",".join(str(int(e)) for e in response)
        for client in lighters:
            s.send_message(client, response)

    #for i in range(int(20*RATE/CHUNK)): #do this for 10 seconds
    #    soundplot(stream)

    stream.stop_stream()
    stream.close()
    p.terminate()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

print(host , port)
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)
