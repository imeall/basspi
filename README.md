# basspi
Assignment for WIT HDip in Computer Science, Semester 2, Computer Systems

Exploring Real Time Audio Signal Processing in Python on the Raspberry Pi

There isn't a lot of audio processing going on on the Raspberry Pi and when I started this project I soon discovered why. The device has its limitations. There's no on-board sound input and despite the improvements in computer processing power, Digital Signal Processing is is still reserved for specialised hardware and software.

The original aim of the project was to make an octave-shifter. This is a device which is commercially available. The Boss Super Octave is a popular model. It is used by buy a guitarists who wish to add a bass sound to their playing, without actually having a bass guitar in the group.

The best known method of frequency shifting uses a technique known as phase vocoder. This is a computationally intensive process, and while I found some Python code which uses this most notably https://github.com/Zulko/pianoputer, it does not do so in real time

Attempts to adapt such code to work in real time proved fruitless. In the end I resorted to a ‘dirty hack’: resampling my data at twice the sample frequency and then throwing away half the data, leaving me with the same number of samples, with half the data stretched out over them. It sounds terrible.

That programme, bassberrypi.py, is included for the sake of interest only.

Instead I focused on on an attribute of the sound which could be more easily manipulated in real time i.e. the amplitude. amplifier.py is submitted for my assignment.
