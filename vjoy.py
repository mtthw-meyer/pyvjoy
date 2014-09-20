#!/usr/bin/python
from ctypes import *
from threading import Thread
from time import sleep
import os

from vjoydevice import *


class vJoyError(Exception):
   pass


VjoyStatus = [
   'VJD_STAT_OWN',   # 0: The  vJoy Device is owned by this application.
	'VJD_STAT_FREE',  # 1: The  vJoy Device is NOT owned by any application (including this one).
	'VJD_STAT_BUSY',  # 2: The  vJoy Device is owned by another application. It cannot be acquired by this application.
	'VJD_STAT_MISS',  # 3: The  vJoy Device is missing. It either does not exist or the driver is down.
	'VJD_STAT_UNKN'   # 4: Unknown   
]


class vJoy:
   _vJoyInterface = None
   _devices = dict()

   def __init__(self):
      # Setup interface to the vJoy library
      try:
         if self._vJoyInterface is None:
            self._vJoyInterface = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), 'vJoyInterface'))
      except OSError:
         raise vJoyError('Failed to load the vJoy library(dll) file')
      
      # Check if a vJoy device is present
      if not self._vJoyInterface.vJoyEnabled():
         raise  vJoyError('No vJoy device(s) enabled')
      else:
         self.product = cast(self._vJoyInterface.GetvJoyProductString(), c_wchar_p).value
         self.manufacturer = cast(self._vJoyInterface.GetvJoyManufacturerString(), c_wchar_p).value
         self.serial = cast(self._vJoyInterface.GetvJoySerialNumberString(), c_wchar_p).value
   
      self.vjoy_devices = dict()
      
      # Create a thread for feeding values to the virtual joystick
      # Make it a daemon so it will be killed when the program exits
      self._feeder = Thread(target = self._feed)
      self._feeder.daemon = True
      self._feeder.start()
      return

   def _feed(self):
      while True:
         for id, device in self._devices.items():
            device.update()
         sleep(0.005)
      return

   def get_device(self, id):
      return self._devices.get(id, None)

   def acquire_device(self, id):
      #VJOYINTERFACE_API BOOL		__cdecl	AcquireVJD(UINT rID);				// Acquire the specified vJoy Device.
      #vjoy_id = c_int(id)
      status = self._vJoyInterface.GetVJDStatus(id)
      if VjoyStatus[status] == 'VJD_STAT_FREE':
         if self._vJoyInterface.AcquireVJD(id):
            self._devices[id] = vJoyDevice(self._vJoyInterface, id)
      return self._devices.get(id, None)

   def relinquish_device(self, id):
      if id in self._devices:
         self._devices.pop(id)
      self._vJoyInterface.RelinquishVJD(id)


if __name__ == '__main__':
   import sys
   import pdb
   device = int(sys.argv[1])
   print 'Loading driver...'
   vjoy = vJoy('')
   print 'Success!'
   print 'Trying to load device %s...' % device
   vjoy_1 = vjoy.acquire_device(device)
   print 'Loaded device %s!' % vjoy_1
   sleep(2)
   vjoy_1.set_axis(HID_USAGE_SL1, 0)
   sleep(2)
   vjoy.relinquish_device(device)
   print 'Tests passed!'
   print 'Exiting...'
