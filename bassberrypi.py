# file: bassberrypi.py
# Conn O Muineachain
# HDIP in Computer Science, Semester 2
# Computer Systems
# Assignment 2
# 16/01/2019

# The programme is a failed attempt to realise a working real-time octave shifter in python.
# I've included it to show my work. Run it if you like - it's not pretty :/ 
# Please see the other file amplifier.py for a reasonably working programme, including IOT features

# designed to take in a live audio stream, shift it down an octave
# and output the octave-shifted output in real-time.
# I discovered that this task is beyond the abilities of an interpreted language.
# This programme does achieve bass-shifting audio using a 'dirty hack', but the quality
# is apalling. There is no IOT ability in this programme, because I abondoned the task
# and wrote another programme (amplifier.py) to do the simpler task of amplifying the 
# magnitude of the real-time signal. amplifier.py DOES have IOT features

import pyaudio
import time
import numpy as np
import scipy.signal as signal
CHANNELS = 1
RATE = 44100
CHUNK = 8000

p = pyaudio.PyAudio()

# data conversion functions
def stream2numpy(stream):
    numpyarray = np.fromstring(stream,dtype=np.int16)
    return numpyarray

def numpy2stream(numpyarray):
    stream = numpyarray.tostring()
    return stream


def octaveshift(in_data): # this is a dirty hack - and it sounds nasty :) 
	# resample in_data
    resampled = signal.resample(in_data,2*CHUNK)
    # our new signal has twice the number of samples
    # we throw away the second half of the set and return the same amount of samples - but slower
    out_data = resampled[0:CHUNK].astype(int)
    return out_data


def callback(in_data, frame_count, time_info, flag):

    # convert from pyaudio stream to numpy array
    numpy_data = stream2numpy(in_data)

    # shift it
    numpy_data2 = octaveshift(numpy_data)
    
    # convert from numpy array back to pyaudio stream
    out_data = numpy2stream(numpy_data2)

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
    time.sleep(0.1)

print("stream stopped")

stream.stop_stream()
stream.close()

p.terminate()
