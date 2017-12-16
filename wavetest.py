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

def soundplot(stream):
    t1=time.time()
    data = np.fromstring(stream.read(CHUNK), np.int16)
    fs = RATE

    BARS = 15
    BAR_HEIGHT = 255
    LINE_WIDTH = 5

    length = len(data)
    RATIO = length/BARS

    count = 0
    maximum_item = 0
    max_array = []
    highest_line = 0

    for d in data:
    	if count < RATIO:
    		count = count + 1

    		if abs(d) > maximum_item:
    			maximum_item = abs(d)
    	else:
    		max_array.append(maximum_item)

    		if maximum_item > highest_line:
    			highest_line = maximum_item

    		maximum_item = 0
    		count = 1

    line_ratio = highest_line/BAR_HEIGHT

    im = Image.new('RGBA', (BARS * LINE_WIDTH, BAR_HEIGHT), (255, 255, 255, 1))
    draw = ImageDraw.Draw(im)

    current_x = 1
    final = [];
    for item in max_array:
        item_height = item/line_ratio
        final.append(item_height)

        current_y = (BAR_HEIGHT - item_height)/2
        draw.line((current_x, current_y, current_x, current_y + item_height), fill=(169, 171, 172), width=4)

        current_x = current_x + LINE_WIDTH


    #im.save("images/" + str(time.time()) + ".png")
    return final;

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

        print("Sending LED Info")
        data = soundplot(stream)
        data = ",".join(str(int(e)) for e in data)
        conn.send(data.encode())

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
