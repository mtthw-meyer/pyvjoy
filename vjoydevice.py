#!/usr/bin/python
from ctypes import *
from ctypes.wintypes import *


HID_USAGE_X    = 0x30
HID_USAGE_Y    = 0x31
HID_USAGE_Z    = 0x32
HID_USAGE_RX   = 0x33
HID_USAGE_RY   = 0x34
HID_USAGE_RZ   = 0x35
HID_USAGE_SL0  = 0x36
HID_USAGE_SL1  = 0x37


class vJoyPosition(Structure):
   _fields_ = [
      ('bDevice', c_uint, 8),
      ('wThrottle', c_long),
      ('wRudder', c_long),
      ('wAileron', c_long),
      ('wAxisX', c_long),
      ('wAxisY', c_long),
      ('wAxisZ', c_long),
      ('wAxisXRot', c_long),
      ('wAxisYRot', c_long),
      ('wAxisZRot', c_long),
      ('wSlider', c_long),
      ('wDial', c_long),
      ('wWheel', c_long),
      ('wAxisVX', c_long),
      ('wAxisVY', c_long),
      ('wAxisVZ', c_long),
      ('wAxisVBRX', c_long),
      ('wAxisVBRY', c_long),
      ('wAxisVBRZ', c_long),
      ('lButtons', c_long),   # 32 buttons: 0x00000001 means button1 is pressed, 0x80000000 -> button32 is pressed
      ('bHats', DWORD),       # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
      ('bHatsEx1', DWORD),    # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
      ('bHatsEx2', DWORD),    # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
      ('bHatsEx3', DWORD),    # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
      ('lButtonsEx1', c_long), # Buttons 33-64
      ('lButtonsEx2', c_long), # Buttons 65-96
      ('lButtonsEx3', c_long), # Buttons 97-128
]


class vJoyDevice:
   MAX_AXES       = 8
   MAX_HATS       = 4
   MAX_BUTTONS    = 128

   _AXES = {
      HID_USAGE_X: 'wAxisX',
      HID_USAGE_Y: 'wAxisY',
      HID_USAGE_Z: 'wAxisZ',
      HID_USAGE_RX: 'wAxisXRot',
      HID_USAGE_RY: 'wAxisYRot',
      HID_USAGE_RZ: 'wAxisZRot',
      HID_USAGE_SL0: 'wSlider',
      HID_USAGE_SL1: 'wDial',
   }

   #define HID_USAGE_WHL	0x38
   #define HID_USAGE_POV	0x39
   _axes = dict()

   def __init__(self, id):
      #cdll.vJoyInterface = cdll.vJoyInterface
      self.id = id
      position_data = {
         'bDevice':  self.id,
         'bHats':    -1,
         'bHatsEx1': -1,
         'bHatsEx2': -1,
         'bHatsEx3': -1,
      }

      # Reset controls on this device
      self.reset()

      # Get information about this device
      self.button_count = cdll.vJoyInterface.GetVJDButtonNumber(self.id)
      self.discrete_hats = cdll.vJoyInterface.GetVJDDiscPovNumber(self.id)
      self.continuous_hats = cdll.vJoyInterface.GetVJDContPovNumber(self.id)
      for HID, field in self._AXES.items():
         if cdll.vJoyInterface.GetVJDAxisExist(self.id, HID):
            min = c_int()
            max = c_int()
            cdll.vJoyInterface.GetVJDAxisMax(self.id, HID, pointer(min))
            cdll.vJoyInterface.GetVJDAxisMin(self.id, HID, pointer(max))
            self._axes[HID] = {
               'min': min.value,
               'max': max.value,
               'center': (min.value + max.value) / 2,
            }
            position_data[field] = self._axes[HID]['center']
      self.position = vJoyPosition(**position_data)
      return

   def set_axis(self, HID, value):
      field = self._AXES.get(HID, None)
      if field is not None:
         setattr(self.position, field, value)
      return

   def update(self):
      #VJOYINTERFACE_API BOOL		__cdecl	UpdateVJD(UINT rID, PVOID pData);	// Update the position data of the specified vJoy Device.
      #cdll.vJoyInterface.UpdateVJD.restype = c_bool
      return cdll.vJoyInterface.UpdateVJD(self.id, pointer(self.position))
   
   def reset(self):
      cdll.vJoyInterface.ResetVJD(self.id)
      return

   def reset_buttons(self):
      cdll.vJoyInterface.ResetButtons(self.id)
      return
      
   def reset_povs(self):
      cdll.vJoyInterface.ResetPovs(self.id)
      return

   def __str__(self):
      return 'vJoy device #%s' % self.id

   #// Write data
   #VJOYINTERFACE_API BOOL		__cdecl	SetAxis(LONG Value, UINT rID, UINT Axis);		// Write Value to a given axis defined in the specified VDJ 
   #VJOYINTERFACE_API BOOL		__cdecl	SetBtn(BOOL Value, UINT rID, UCHAR nBtn);		// Write Value to a given button defined in the specified VDJ 
   #VJOYINTERFACE_API BOOL		__cdecl	SetDiscPov(int Value, UINT rID, UCHAR nPov);	// Write Value to a given descrete POV defined in the specified VDJ 
   #VJOYINTERFACE_API BOOL		__cdecl	SetContPov(DWORD Value, UINT rID, UCHAR nPov);	// Write Value to a given continuous POV defined in the specified VDJ 
