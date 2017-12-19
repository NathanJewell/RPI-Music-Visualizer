import websocket

import time
import ssl
import _thread
from queue import LifoQueue
def main():

    # Define a function for the thread
    def print_time( threadName, va):
       while True:
          v = va.get()
          print (str(threadName) + str(v))
          time.sleep(.01)

    # Create two threads as follows
    num = LifoQueue(1)
    try:
       _thread.start_new_thread( print_time, ("Thread-1", num,) )
    except:
       print ("Error: unable to start thread")


    c = 0

    while 1:
        c += 1
        print(c)
        if not num.full():
            num.put(c)
        else:
            num.get()
            num.put(c)



if __name__ == '__main__':
    main();
