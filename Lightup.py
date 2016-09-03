#!/usr/bi/python3
import threading
from time import sleep

presentDevices = []
trackDevices = []

def Spinner(sec):
  import itertools, sys, time
  t_end = time.time() + sec
  spinner = itertools.cycle(['-', '/', '|', '\\'])
  while time.time() < t_end:
    sys.stdout.write(next(spinner))  # write the next character
    sys.stdout.flush()                # flush stdout buffer (actual character display)
    sys.stdout.write('\b')            # erase the last written char
    sleep(.1)

def SignalFinding(blinks):
   import os, subprocess, binascii, select, struct
   import RPi.GPIO as gpio, sys, time

   gpio.setwarnings(False)
   gpio.setmode(gpio.BOARD)      # use P1 pin numbers
   gpio.setup(12, gpio.OUT)
  
   t_end = time.time() + 15
   #while time.time() < t_end:
   for i in range(blinks):
     gpio.output(12, 1)
     sleep(0.1)
     gpio.output(12, 0)
     sleep(0.1)

try:
  import sys
  from subprocess import call
  from bluepy.btle import Scanner, DefaultDelegate, Peripheral

  class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        trackDevices.append(dev.addr)
        if isNewDev and dev.addr not in presentDevices:
            presentDevices.append(dev.addr)
            print("Discovered device", dev.addr, dev.updateCount, dev.rssi, dev.connectable)
            SignalFinding(5)
            sleep(0.5) 
            for (adtype, desc, value) in dev.getScanData():
              if desc == "Complete Local Name":
                call(["espeak", "Found %s" % value])
                SignalFinding(1)
                sleep(0.2)
 
        elif isNewData:
            #print("Received new data from", dev.addr, isNewDev, isNewData)
            for (adtype, desc, value) in dev.getScanData():
              print("Changes %s(%s): %s = %s" % (dev.addr, dev.addrType, desc, value))
              #SignalFinding(1)
              sleep(0.2)
  
  scanner = Scanner().withDelegate(ScanDelegate())
  while True:
    trackDevices.clear()
    scanner.scan(10.0)

    for item in presentDevices:
      if item not in trackDevices:
        print("Removing device ", item)
        presentDevices.remove(item)
        SignalFinding(3)

    Spinner(10.0)

except RuntimeError:
  print("use sudo!")
  sys.exit()
