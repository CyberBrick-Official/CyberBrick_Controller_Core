# CyberBrick ESP-NOW receiver in CyberBrick MicroPython flavor
# To be copied to CyberBrick Core, paired with X11 remote control receiver shield
# Control for the CyberBrick official forklift
# https://makerworld.com/de/models/1395994-cyberbrick-official-forklift
#
# The outputs of X11 shield are driven from following inputs:
# * Servo1: fork up/down (channel 3 (controlled by the slider on the remote))
# * Motor1: right track (mix of channel 2 (left vertical stick) and channel 4 (right horizontal stick))
# * Motor2: left track  (mix of channel 2 (left vertical stick) and channel 4 (right horizontal stick))
# * NeoPixel_Channel2: front lights, driven in code by 3-way switch position and button press

# In CyberBrick official forklift, the 2 NeoPixels are all connected to channel2, 1 - Right, 2 - Left

"""
The incoming telegram via ESP-NOW is expected in the following order:
 1)  ch0 L1, unsigned 12-bit value   (3-way switch on Cyberbrick official standard remote)
 2)  ch1 L2, unsigned 12-bit value   (Left horizontal (LH) stick)
 3)  ch2 L3, unsigned 12-bit value   (Left vertical (LV) stick)
 4)  ch3 R1, unsigned 12-bit value   (Slider)
 5)  ch4 R2, unsigned 12-bit value   (Right horizontal (RH) stick)
 6)  ch5 R3, unsigned 12-bit value   (Right vertical (LH) stick)
 7)  ch6 K1, 1-bit value, low-active (Button)
 8)  ch7 K2, 1-bit value, low-active (Not used)
 9)  ch9 K3, 1-bit value, low-active (Not used)
10) ch10 K4, 1-bit value, low-active (Not used)
"""

from machine import Pin, PWM
import network
import espnow
from neopixel import NeoPixel
import utime

# Initialize servo outputs with 1.5ms pulse length in 20ms period
S1 = PWM(Pin(3), freq=50, duty_u16=4915) # servo center 1.5ms equals to 65535/20 * 1.5 = 4915
#S2 = PWM(Pin(2), freq=50, duty_u16=4915)
#S3 = PWM(Pin(1), freq=50, duty_u16=4915)
#S4 = PWM(Pin(0), freq=50, duty_u16=4915)

# Initialize motor 1 and 2 outputs to idle (a brushed motor is controlled via 2 pins on HTD8811)
M1A = PWM(Pin(4), freq=100, duty_u16=0)
M1B = PWM(Pin(5), freq=100, duty_u16=0)
M2A = PWM(Pin(6), freq=100, duty_u16=0)
M2B = PWM(Pin(7), freq=100, duty_u16=0)

# Initialize Wi-Fi in station mode
sta = network.WLAN(network.STA_IF)
sta.active(True)
mac = sta.config('mac')
mac_address = ':'.join('%02x' % b for b in mac)
print("MAC address of the receiver:", mac_address)

def wifi_reset():
  # Reset Wi-Fi to AP_IF off, STA_IF on and disconnected
  sta = network.WLAN(network.WLAN.IF_STA); sta.active(False)
  ap = network.WLAN(network.WLAN.IF_AP); ap.active(False)
  sta.active(True)
  while not sta.active():
      time.sleep(0.1)
  while sta.isconnected():
      time.sleep(0.1)
  sta = network.WLAN(network.STA_IF)
  sta.active(True)
  sta.config(channel=1,pm=sta.PM_NONE,reconnects=0)
  sta.disconnect()

wifi_reset()

# Initialize ESP-NOW
e = espnow.ESPNow()

def enow_reset():
  try:
      e.active(True)
  except OSError as err:
      print("Failed to initialize ESP-NOW:", err)
      raise

enow_reset()

# Drive NeoPixel on CyberBrick Core
npcore = Pin(8, Pin.OUT)
np = NeoPixel(npcore, 1)
np[0] = (0, 10, 0) # dim green
np.write()

#Initialize NeoPixel LED string 2 with 2 pixels
LEDstring2pin = Pin(20, Pin.OUT)
LEDstring2 = NeoPixel(LEDstring2pin, 2)
for i in range(2):
  LEDstring2[i] = (0, 0, 0) # default all off
LEDstring2.write()

sliderthrright    = int(4095/3)
sliderthrleft     = int(2*4095/3)
blinkertime_ms    = 750  # 1.5 Hz
servomidpoint     = int(1.5*65535/20) # 1.5 ms
midpoint          = 2047
deadzoneplusminus = 100

while True:
  try:
    # Receive message (host MAC, message, 500ms failsafe timeout)
    host, msg = e.recv(500)
    if msg == None:
      # Failsafe
      # Motors off
      M1A.duty_u16(0)
      M1B.duty_u16(0)
      M2A.duty_u16(0)
      M2B.duty_u16(0)
      # Fork to idle
      S1.duty_u16(servomidpoint)
      # blinking red LEDs
      if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
        LEDstring2[0] = (0, 0, 0) # Right dark
        LEDstring2[1] = (0, 0, 0) # Left dark
      else:
        LEDstring2[0] = (255, 0, 0) # Right red
        LEDstring2[1] = (255, 0, 0) # Left red
      LEDstring2.write()

      e.active(False)
      wifi_reset()
      enow_reset()
    
    else:
      rxch = msg.decode().split(",")
      if len(rxch) == 10:
        # assuming that we received valid message
        lightcontrol = int(rxch[0]) # 3-way switch
        if (lightcontrol > sliderthrleft):
          if int(rxch[6]) == 0: # Button pressed
            #Yellow alternating blinking lights
            if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
              LEDstring2[0] = (0, 0, 0) # Right dark
              LEDstring2[1] = (255, 255, 0) # Left yellow
            else:
              LEDstring2[0] = (255, 255, 0) # Right yellow
              LEDstring2[1] = (0, 0, 0) # Left dark
          else:
            LEDstring2[0] = (255, 255, 255) # Right white
            LEDstring2[1] = (255, 255, 255) # Left white
        elif (lightcontrol < sliderthrright):
          #Yellow blinking lights
          if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
            LEDstring2[0] = (0, 0, 0) # Right dark
            LEDstring2[1] = (255, 255, 0) # Left yellow
          else:
            LEDstring2[0] = (255, 255, 0) # Right yellow
            LEDstring2[1] = (0, 0, 0) # Left dark
        else:
          if int(rxch[6]) == 0: # Button pressed
            #Yellow blinking lights
            if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
              LEDstring2[0] = (0, 0, 0) # Right dark
              LEDstring2[1] = (0, 0, 0) # Left dark
            else:
              LEDstring2[0] = (255, 255, 0) # Right yellow
              LEDstring2[1] = (255, 255, 0) # Left yellow
          else:
            LEDstring2[0] = (0, 0, 0) # Right dark
            LEDstring2[1] = (0, 0, 0) # Left dark
        LEDstring2.write()

        # 0.5 to 2.5ms range for 0 to 4095 input value
        fork = int(rxch[3])
        S1.duty_u16(int(((float(fork)*6554)/4095 + 1638)))
        #1 to 2ms range for 0 to 4095 input value
        #S2.duty_u16(int(((float(rxch[5])*3277)/4095 + 3277)))
        #0.5 to 2.5ms range for 0 to 4095 input value
        #S3.duty_u16(int(((float(rxch[2])*6554)/4095 + 1638)))
        #S4.duty_u16(int(((float(rxch[1])*6554)/4095 + 1638)))

        steering = int(rxch[4])
        throttle = int(rxch[2])
                  
        lefttrack = int(((steering-midpoint) + (throttle-midpoint))/2 + midpoint)
        righttrack = int(((steering-midpoint) - (throttle-midpoint))/2 + midpoint)
                  
        if ((righttrack < (midpoint+deadzoneplusminus)) and (righttrack > (midpoint-deadzoneplusminus))):
          #deadzone - no forward/backward movement
          M1A.duty_u16(0)
          M1B.duty_u16(0)
        else:
          if righttrack > midpoint:
            # backwards
            M1A.duty_u16(min(32*(righttrack-midpoint), 65535))
            M1B.duty_u16(0)
          else:
            # forwards
            M1A.duty_u16(0)
            M1B.duty_u16(min(32*(midpoint-righttrack), 65535))
                  
        if ((lefttrack < (midpoint+deadzoneplusminus)) and (lefttrack > (midpoint-deadzoneplusminus))):
          #deadzone - no forward/backward movement
          M2A.duty_u16(0)
          M2B.duty_u16(0)
        else:
          if lefttrack > midpoint:
            # backwards
            M2A.duty_u16(min(32*(lefttrack-midpoint), 65535))
            M2B.duty_u16(0)
          else:
            # forwards
            M2A.duty_u16(0)
            M2B.duty_u16(min(32*(midpoint-lefttrack), 65535))
  except OSError as err:
    print("Error:", err)
    time.sleep(0.5)
    e.active(False)
    wifi_reset()
    enow_reset()

  except KeyboardInterrupt:
    print("Stopping receiver...")
    e.active(False)
    sta.active(False)
    break
