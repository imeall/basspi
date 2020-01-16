
# from https://stackoverflow.com/questions/22101023/how-to-handle-in-data-in-pyaudio-callback-mode
# and pianoputer
# and https://bastibe.de/2012-11-02-real-time-signal-processing-in-python.html

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
    #print(stream)
    numpyarray = np.fromstring(stream,dtype=np.int16)
    #print(numpyarray)
    return numpyarray

def numpy2stream(numpyarray):
    stream = numpyarray.tostring()
    return stream


def octaveshift(in_data): # 
    
    #print("in_data", in_data)
    # resample in_data
    resampled = signal.resample(in_data,2*CHUNK)

    # now convert resampled to list and throw away the extra samples
    #new_data = resampled.tolist()

    #data2 = new_data[0:CHUNK]

    # now convert data2 list back to numpy array
    #out1_data = np.asarray(data2, dtype=np.int16)
    #print("out_data", out_data)
    out_data = resampled[0:CHUNK].astype(int)
    #print("out_data", out_data)


    return out_data


def callback(in_data, frame_count, time_info, flag):

    #print("in_data", in_data)
    numpy_data = stream2numpy(in_data)
    #print("numpy_data", numpy_data)

    # shift it
    numpy_data2 = octaveshift(numpy_data)
    #print("numpy_data", numpy_data)
    
    out_data = numpy2stream(numpy_data2)
    #print("out_data", numpy_data)

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
#zs    print("stream is active")
    time.sleep(0.1)

print("stream stopped")

stream.stop_stream()
stream.close()

p.terminate()
