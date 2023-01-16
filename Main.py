#!/usr/bin/env python

# Import modules
import opc      # create connection
import time     # manage performance time
import numpy    # process sound
import pyaudio  # record sound
import wave     # process sound
import msvcrt   # take input without blocking

# Parameters/variables
Color = (252, 252, 53)
Color_Black = (0, 0, 0)
Address = 'localhost:7890'  # hold host address
cycle_count = 0  # hold a counter of the cycles done
i = 0  # a counter
my_pixels = [Color_Black] * 360  # initiate list my_pixels

# Menu
print("Audio Visualizer [Version 0.1 - prototype]\nCreated in March 2019, by Carmagniole Alexandre and Noel Adrien")
print("\n\n Press '1' to see keys usable during runtime OR\n Press any other key to continue...")
print("------------------------------------------------------------------------------")
key = msvcrt.getch()
if key == b'1':
    print("Keys and function:")
    print(" 1. Change the color of the leds\n 2. To exit")
    print("-------------------------------------------------------------------")
    print(" Press any key to continue...")
    msvcrt.getch()

"""Create connection to the host"""
# Create a client object for connection
client = opc.Client(Address)

# Test if can connect
if client.can_connect():
    print('Connection to ', Address, ' was sucessful')
else:
    print('Connection to ', Address, 'failed')


"""Runtime environment
Here the codes are looped indefinitely
to process the recorded audio"""
while True:
    # Take start time
    time_start = time.time()
    # Increment the cycle count
    cycle_count += 1

    # Wait for a key to be pressed
    if msvcrt.kbhit():
        key = msvcrt.getch()  # Record the pressed key
        # Change the color of the leds
        if key == b'1':
            if Color == (252, 252, 53):
                Color = (188, 30, 143)
            elif Color == (188, 30, 143):
                Color = (34, 178, 1)
            elif Color == (34, 178, 1):
                Color = (252, 252, 53)
            else:
                Color = (252, 252, 53)
        elif key == b'2':
            break

    """Take audio input and process"""
    # Parameters to record the audio
    CHUNK = 1500  # Max chunks: 2666.7 to keep 15 fps
    RATE = 40000  # Must be max freq * 4, for max freq to be represented
    CHANNELS = 1
    FORMAT = pyaudio.paInt16

    freqBand = [1]*61  # holds the amplitude of each led columns

    # initiate the window and the stream
    window = numpy.blackman(CHUNK)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Record audio
    data = stream.read(CHUNK)
    # window process
    indata = numpy.array(wave.struct.unpack("%dh" % CHUNK, data))*window
    """ Here each point of the windowed audio is scanned searching for zero(s),
        after founding a zero, we scan for a peak
        as these 2 points are found we substract the distance between them
        multiply the result to have the period of the waveform
        using the period we find the frequency"""
    # Scan for zero
    for i in range(len(indata)):
        # Test for zero
        if indata[i] == 0:
            marker_zero = i     # Mark the zero point
            marker_peak = -1    # Initiat the peak marker
            x = i + 1

            # Scan for a peak
            while (x+1) < len(indata):
                # Test to see if absolute amplitude decrease, means theres a apeak
                if abs(indata[x+1]) <= abs(indata[x]) or x == len(indata):
                    marker_peak = x  # Mark peak
                    break  # Break from loop
                elif indata[x] == 0:
                    marker_peak = round(x + ((x - marker_zero)/2))  # Mark potential peak
                    break
                else:
                    x += 1

            # Calculate the frequency
            freq = RATE/((marker_peak - marker_zero)*4)
            freqIndex = round((freq/10000)*60)  # Defines the band of the frequency

            # Test to see if amplitude in freqBand needs to be replace
            if abs(indata[marker_peak]) > freqBand[freqIndex]:
                freqBand[freqIndex] = abs(indata[marker_peak])

            # Search for last peak on timeline
            # Doing so increase the number of potential frequency detected
            marker_zero = i
            marker_peak = -1
            x = i - 1
            # Scan for past peaks
            while (x - 1) > 0:
                if abs(indata[x - 1]) >= abs(indata[x]) or x == 1:
                    marker_peak = x
                    break   # Break from loop
                elif indata[x] == 0:
                    marker_peak = round(x + ((x - marker_zero)/2))  # Mark potential peak
                    break
                else:
                    x -= 1

            # Calculate the frequency through period of waveform
            freq = RATE / ((marker_zero - marker_peak) * 4)
            freqIndex = round((freq / 10000) * 60)  # Defines the band of the frequency

            # Test to see if amplitude in freqBand needs to be replace
            if abs(indata[marker_peak]) > abs(freqBand[freqIndex]):
                freqBand[freqIndex] = abs(indata[marker_peak])

    # Set the color of each leds per column based on the amplitude
    for i in range(60):
        # 1st led
        if freqBand[i] > 10:
            my_pixels[i+300] = Color
        else:
            my_pixels[i + 300] = Color_Black
        # 2nd led
        if freqBand[i] > 15:
            my_pixels[i+240] = Color
        else:
            my_pixels[i+240] = Color_Black
        # 3rd led
        if freqBand[i] > 25:
            my_pixels[i+180] = Color
        else:
            my_pixels[i+180] = Color_Black
        # 4th led
        if freqBand[i] > 35:
            my_pixels[i+120] = Color
        else:
            my_pixels[i+120] = Color_Black
        # 5th led
        if freqBand[i] > 55:
            my_pixels[i+60] = Color
        else:
            my_pixels[i+60] = Color_Black
        # 6th led
        if freqBand[i] > 100:
            my_pixels[i] = Color
        else:
            my_pixels[i] = Color_Black

    # Calculate the time elapsed during this cycle
    time_end = time.time()
    perf_time = time_end - time_start
    # make the program wait (1/target fps)
    if (1/15) > perf_time:
        time.sleep((1/15) - perf_time)

    # Set pixels color at the end of cycle
    if client.put_pixels(my_pixels, channel=0):
        print("connected, cycle number: ", cycle_count, " , cycle time: ", perf_time, " sec")
    else:
        print("not connected")

print("\nThanks for trying this audio visualizer.\nExiting... Press any key to continue...")
msvcrt.getch()
