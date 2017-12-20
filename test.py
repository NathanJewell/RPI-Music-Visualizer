import pyaudio
import numpy as np
import pylab
import time

from matplotlib import pyplot as plot
from PIL import Image, ImageDraw
import os

import socket
import threading

RATE = 44100
CHUNK = int(RATE/100) # RATE / number of updates per second

def soundplot(stream):
    t1=time.time()
    data = np.fromstring(stream.read(CHUNK), np.int16)
    fs = RATE

    BARS = 100
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
    		max_array.append(d)

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


    def save(image):
        image.save("images/" + str(time.time()) + ".png")

    t1 = threading.Thread(target=save, args=(im,))
    t1.start()
    
    return final;

if __name__=="__main__":
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK)


    while True:
        data = soundplot(stream)


    #for i in range(int(20*RATE/CHUNK)): #do this for 10 seconds
    #    soundplot(stream)

    stream.stop_stream()
    stream.close()
    p.terminate()
