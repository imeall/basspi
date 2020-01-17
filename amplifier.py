# file: amplifier.py
# Conn O Muineachain
# HDIP in Computer Science, Semester 2
# Computer Systems
# Assignment 2
# 16/01/2019

# The programme 
# - takes in a live audio stream
# - measures it's loudness using root-mean-square
# - limits the loudness of the output signal to 50% of the peak amplitude (2**15-1)/2
# - represents the audio volume on a scale from 0.00 to 1.00
# - publishes the volume to wia.io every 15 seconds
# - publishes a 'too loud' message to wia.io if the volume exceeds 1.0 (generates an email)
# - subscribes to a command from wia.io to change the volume

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
requested_volume = 0.4

p = pyaudio.PyAudio()

def changevolume(): # hardcoded the value because I couldn't figure out how to pass data from wia.io
    global requested_volume
    print("command received")
    requested_volume = 0.75


wia.Stream.connect()
wia.Command.subscribe(**{"device": 'dev_ymRY2FAh', "slug": 'changevolume', "func": changevolume})

# data conversion functions
def stream2numpy(stream): #converts pyaudio stream to numpy array
    numpyarray = np.fromstring(stream,dtype=np.int16)
    return numpyarray

def numpy2stream(numpyarray): #converts numpy array to pyaudio stream
    stream = numpyarray.tostring()
    return stream

def amplify(in_data,factor): 			# simple scalar mutiplication of the elements (samples) of the numpy array
    amplified = in_data*factor			# 'factor' is a float
    return amplified.astype(np.int16)	# so we convert the result back to 16-bit integer before returning

def loudness(in_data):
    rms = np.sqrt(np.mean(np.square(in_data,dtype=np.int_))) # cast to 32-bit int to handle the big squares
    loudness = round(rms/(MAX_RMS/2),2) # loudness is the ratio of RMS to MAX_RMS, rounded to 2 decimal places
    return loudness

# the callback function is specified in the stream initialisation below, stream=p.open(...)
# When stream.start_stream(), callback begins executing repeatedly in its own thread
# it continues until stream.stop_stream(), or the main thread ends
def callback(in_data, frame_count, time_info, flag):
    global volume # we will read and write to this variable. the main thread also uses it to update wia.io

    numpy_data = stream2numpy(in_data) # convert data from pyaudio stream in order to use scipy, numpy libraries

    volume = loudness(numpy_data)

    if volume > 0:				# on some iterations of this callback function, the 1024 samples are all 0
    							# when this happens we simply refrain from making any changes to volume
        if volume > 1: 
            factor = 1/volume 						# reduce to the maximum volume, i.e. 1
            volume = 1								
        else:
            factor = requested_volume/volume 		# change to the requested volume
            volume = requested_volume

        numpy_data = amplify(numpy_data, factor)	# now call the amplify function using the factor we've calculated

    out_data = numpy2stream(numpy_data)				# convert data from numpy array back to pyaudio stream - we're done

    return (out_data, pyaudio.paContinue)


stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                input=True,
                stream_callback=callback,
                frames_per_buffer=CHUNK)

stream.start_stream()

while stream.is_active():	# once the stream is started, this loop executes continously until the stream stops
							# or the programme is interrupted
    wia.Event.publish(name="volume", data=volume)		# publish current audio volume every 15 seconds
    time.sleep(10)

    if volume>1.0:										# if signal volume exceeds the maximum we have specified
        wia.Event.publish(name="tooloud", data=volume)	# publish to wia.io (generates an email)

    time.sleep(5)

print("stream stopped")

stream.stop_stream()
stream.close()

p.terminate()
