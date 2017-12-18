import pyaudio
import numpy as np
import pylab
import time

from matplotlib import pyplot as plot
from PIL import Image, ImageDraw
import os

import socket

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

RATE = 44100
CHUNK = int(RATE/20) # RATE / number of updates per second

BARS = 100
BAR_HEIGHT = 255
LINE_WIDTH = 5
line_ratio_max = 0
line_ratio_avg = 0
line_ratio = 0
line_ratios = []

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

def soundplott(stream):
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
    for d in data:

        if count < RATIO:
            count = count + 1

            if abs(d) > maximum_item:
                maximum_item = abs(d)
        else:
            max_array.append(maximum_item)

            if maximum_item > highest_line:
                highest_line = maximum_item
                maxi = d

            maximum_item = 0
            count = 1

    current_line_ratio = highest_line/BAR_HEIGHT;
    line_ratios.append(current_line_ratio)
    if(len(line_ratios) > 30):
        line_ratios.pop(0)


    if (current_line_ratio > line_ratio_max):
        line_ratio_max = highest_line/BAR_HEIGHT

    line_ratio_avg = sum(line_ratios)/len(line_ratios)
    line_ratio = max((line_ratio_max+2*line_ratio_avg)/3, current_line_ratio)

    #im = Image.new('RGBA', (BARS * LINE_WIDTH, BAR_HEIGHT), (255, 255, 255, 1))
    #draw = ImageDraw.Draw(im)

    current_x = 1
    final = [];
    for item in max_array:
        item_height = item/line_ratio
        final.append(item_height)

        current_y = (BAR_HEIGHT - item_height)/2
        #draw.line((current_x, current_y, current_x, current_y + item_height), fill=(169, 171, 172), width=4)

        current_x = current_x + LINE_WIDTH

    frequency = getFreq(data)

    #im.save("images/" + str(time.time()) + ".png")
    return (final, frequency, maxi);

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

    print(len(data))
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
                maxi = len(max_array)

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

        current_y = (BAR_HEIGHT - item_height)/2
        #draw.line((current_x, current_y, current_x, current_y + item_height), fill=(169, 171, 172), width=4)

        current_x = current_x + LINE_WIDTH

    frequency = getFreq(data)

    #im.save("images/" + str(time.time()) + ".png")
    return (final, frequency, maxi);

def colorize(d):
    data = d[0]
    frequency = d[1]
    #print("f: " + str(frequency))
    maxi = d[2]
    #print("m: " + str(maxi))


    def sigmoid(v): #v is between 0 and 1
        return 255/(1+pow(2.718, -.05*(v-125)))
    def invsigmoid(v):
        return -255/(1+pow(2.718, -.05*(v-125)))+255

    data = [v/255 for v in data]    #normalize
    colors = []
    lenratio = 255/len(data);
    colorratio = lenratio/len(data)
    freqratio = (np.clip(frequency, 50, 1000)-50)/950 #clamp and normalize
    for i in range(0, len(data)): #bass is bluer, high is redder

        intensity = pow(data[i], 1)
        r = sigmoid(255*intensity)*intensity#freqratio*255
        g = 0#colorratio*255
        b = invsigmoid(255*intensity)*intensity
        #if(i==maxi):


        colors.append(r)
        colors.append(g)
        colors.append(b)
    for x in range(144*3):
        colors.append(128)

    return colors

if __name__=="__main__":

    list_devices();
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK)

    host = '192.168.0.26'        # Symbolic name meaning all available interfaces
    port = 12345     # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))

    print(host , port)
    s.listen(1)
    conn, addr = s.accept()
    print('Connected by', addr)
    while True:
        data = conn.recv(1024).decode();

        chart = soundplot(stream)
        response = colorize(chart)
        response = ",".join(str(int(e)) for e in response)
        conn.send(response.encode())
        print("sent")
        if data == "END":
            conn.close()

    #for i in range(int(20*RATE/CHUNK)): #do this for 10 seconds
    #    soundplot(stream)

    stream.stop_stream()
    stream.close()
    p.terminate()


#data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
#pylab.plot(data)
#pylab.title(i)
#pylab.grid()
#pylab.axis([0,len(data),-2**16/2,2**16/2])
#pylab.savefig("03.png",dpi=50)
#pylab.close('all')
#print("took %.02f ms"%((time.time()-t1)*1000))
