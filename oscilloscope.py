import pyaudio 
import wave 
import sys
import math 
import progressbar
import struct 
import numpy as np
from matplotlib import pyplot as plt

'''
Janky oscilloscope. 

Tobin Feldman-Fitzthum - Spring 2019 

This program sucks. Do not distribute. 
'''

def main():
  # constants 
  CHUNK = 2100

  # read a WAV from command line 
  wf = wave.open(sys.argv[1], 'rb')
  sample_rate = wf.getframerate()

  p = pyaudio.PyAudio()
  stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                  channels = wf.getnchannels(),
                  rate = sample_rate, 
                  output = True)
 
  print(wf.getsampwidth())
  channels = wf.getnchannels()
  # TODO make this work in stereo? 
  #assert(wf.getnchannels() == 1)

  # can't handle 24-bit audio because there is no np.int24 dtype. could 
  # if you want to use 32-bit audio, change the string passed to struct.unpack
  assert(wf.getsampwidth() == 2)

  print("Sample width is {} bytes, with {} channels.".format(wf.getsampwidth(),channels))
  print(wf.getcompname())

  print("Loading All Frames...")
  #frames = []
  #data = wf.readframes(CHUNK)

  n_chunks = 0 
  # read the entire stream in, chunk size is irrelevant here
  data = wf.readframes(wf.getnframes())
  print(type(data))
  amps = struct.unpack("%ih" % (wf.getnframes() * channels), data)
  
  # normalize. might be better to vectorize this
  amps = [float(val) / pow(2, 15) for val in amps]
  amps = np.array(amps)
  
  # de-interleave if in stereo
  if channels > 1: 
    amps = amps.reshape(amps.shape[0]/channels,channels)
    amps = np.average(amps,axis=1)
 
  n_samples = amps.shape[0]
  print("{} frames loaded".format(n_samples))
  assert n_samples == wf.getnframes()
        

  print("{} total samples".format(n_samples))

  for i in progressbar.progressbar(range(0,n_samples,CHUNK)):
    sub_amp = amps[i:i + CHUNK] 
    
    # zero locking. not totally clear what to do if there are no zeros... 
    # TODO: check if it's close to zero, not just exactly zero
    zeros = np.where(sub_amp==0)[0]
    if len(zeros) > 0: 
      sub_amp = np.roll(sub_amp,-1*zeros[0])
    
    fig = plt.figure(figsize=(30,10))
    plt.ylim(-1,1)
    plt.axis('off')
    plt.style.use("dark_background") # fuck matplotlib
    s = fig.add_subplot(111)
    #s.set_facecolor("#000000")
    s.plot(sub_amp,color='green')
    fig.savefig('plot/plot{}.png'.format(str(i/CHUNK).zfill(5)))
    plt.close(fig)

  stream.close()    
  p.terminate()

if __name__ == "__main__":
  main()
