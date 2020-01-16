
# from https://stackoverflow.com/questions/22101023/how-to-handle-in-data-in-pyaudio-callback-mode
# and pianoputer
# and https://bastibe.de/2012-11-02-real-time-signal-processing-in-python.html

import pyaudio
import time
import numpy as np
import scipy.signal as signal

from wia import Wia
wia = Wia()
wia.access_token = "d_sk_vytoM32Ehx7SFWr3mU3mov8K"

CHANNELS = 1
RATE = 44100
CHUNK = 1024

MAX_RMS = 32767 / 2 # setting to 50% of peak amplitude to avoid overflows

# initial values
volume = 0
requested_volume = 0.2

p = pyaudio.PyAudio()


def changevolume():
    global requested_volume
    print("command received")
    requested_volume = 0.75


#wia.Stream.connect()
wia.Command.subscribe(**{"device": 'dev_ymRY2FAh', "slug": 'changevolume', "func": changevolume})


# data conversion functions
def stream2numpy(stream):
    numpyarray = np.fromstring(stream,dtype=np.int16)
    return numpyarray

def numpy2stream(numpyarray):
    stream = numpyarray.tostring()
    return stream

def amplify(in_data,factor):
#    print("in_data", in_data)
#    print("factor", factor)
    amplified = in_data*factor
    return amplified.astype(np.int16)

def findpeak(in_data):
    return np.amax(abs(in_data))

def loudness(in_data):
    rms = np.sqrt(np.mean(np.square(in_data,dtype=np.int_))) # 32 bit int to handle the squares
#    print("rms",rms)
    loudness = round(rms/(MAX_RMS / 2),2)
#    print("loudness", loudness)
    return loudness

def callback(in_data, frame_count, time_info, flag):

    global volume
    #print("in_data", in_data)

    numpy_data = stream2numpy(in_data)
    #print("numpy_data", numpy_data)

    volume = loudness(numpy_data)
    #print("volume",volume)

    if volume > 0:
        if volume > 1: 
            factor = 1/volume # reduce to the maximum volume = 1
        else:
            factor = requested_volume/volume # increase to the requested volume
     #   print("factor",factor)
#        print("numpy_data", numpy_data)
        numpy_data = amplify(numpy_data, factor)
#        print("numpy_data", numpy_data)

    # recalculate loudness and assign to global volume
    volume = loudness(numpy_data)
    #print("volume", volume)

    out_data = numpy2stream(numpy_data)
    #print("out_data", out_data)

    return (out_data, pyaudio.paContinue)


stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                input=True,
                stream_callback=callback,
                frames_per_buffer=CHUNK)

stream.start_stream()

while stream.is_active():
#    print("stream is active")
    time.sleep(0.1)
    wia.Event.publish(name="volume", data=volume)
    print("volume",volume)
    time.sleep(2)
    print("requested_volume", requested_volume)
    print("volume",volume)
    time.sleep(2)
    print("requested_volume", requested_volume)
    print("volume",volume)
    time.sleep(2)
    print("requested_volume", requested_volume)
    print("volume",volume)
    time.sleep(2)
    print("requested_volume", requested_volume)
    print("volume",volume)
    time.sleep(2)
    print("requested_volume", requested_volume)
    print("volume",volume)
    time.sleep(2)
    print("requested_volume", requested_volume)
    print("volume",volume)

    time.sleep(2)

    if volume>0.9:
        wia.Event.publish(name="tooloud", data=volume)

    time.sleep(5)

print("stream stopped")

stream.stop_stream()
stream.close()

p.terminate()
