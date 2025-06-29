# CyberBrick ESP-NOW receiver in CyberBrick MicroPython flavor
# To be copied to CyberBrick Core, paired with X11 remote control receiver shield
# Control for the CyberBrick official truck
# https://makerworld.com/de/models/1396031-cyberbrick-official-truck
#
# The outputs of X11 shield are driven from following inputs:
# * Servo1: channel 4 (right horizontal stick)
# * Servo2: channel 5 (right vertical stick)
# * Servo3: channel 1 (left horizontal stick)
# * Servo4: channel 3 (slider)
# * Motor1: channel 2 (left vertical stick)
# * Motor2: not driven by this code
# * NeoPixel_Channel1: not driven by this code
# * NeoPixel_Channel2: driven in code by throttle (LV) and 3-way switch position

# In CyberBrick official truck, the 4 NeoPixels are alls connected to channel2, 1 - FrontLeft, 2 - FrontRight, 3 - BackLeft, 4 - BackRight

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

import network
import aioespnow
import asyncio
from machine import Pin, PWM
from neopixel import NeoPixel
import utime

# Initialize Wi-Fi in station mode
sta = network.WLAN(network.STA_IF)
sta.active(True)
mac = sta.config('mac')
mac_address = ':'.join('%02x' % b for b in mac)
print("MAC address of the receiver:", mac_address)
sta.config(channel=1)  # Set channel explicitly if packets are not received
sta.disconnect()

# Initialize AIOESPNow
e = aioespnow.AIOESPNow()
try:
    e.active(True)
except OSError as err:
    print("Failed to initialize AIOESPNow:", err)
    raise

print("Initialized AIOESPNow")

# Async function to receive messages
async def receive_messages(e):
    # Drive NeoPixel on CyberBrick Core
    npcore = Pin(8, Pin.OUT)
    np = NeoPixel(npcore, 1)
    np[0] = (0, 10, 0) # dim green
    np.write()

    # Initialize all servo outputs with 1.5ms pulse length in 20ms period
    S1 = PWM(Pin(3), freq=50, duty_u16=4915) # servo center 1.5ms equals to 65535/20 * 1.5 = 4915
    S2 = PWM(Pin(2), freq=50, duty_u16=4915)
    S3 = PWM(Pin(1), freq=50, duty_u16=4915)
    S4 = PWM(Pin(0), freq=50, duty_u16=4915)

    # Initialize motor 1 output to idle (a brushed motor is controlled via 2 pins on HTD8811)
    M1A = PWM(Pin(4), freq=100, duty_u16=0)
    M1B = PWM(Pin(5), freq=100, duty_u16=0)

    #Initialize NeoPixel LED string 2 with 4 pixels
    LEDstring2pin = Pin(20, Pin.OUT)
    LEDstring2 = NeoPixel(LEDstring2pin, 4)
    for i in range(4):
      LEDstring2[i] = (0, 0, 0) # default all off
    LEDstring2.write()

    blinkerthrright = 1365 # 1/3 of 4095 
    blinkerthrleft  = 2730 # 2/3 of 4095
    blinkertime_ms  = 500  # 2 Hz

    while True:
        try:
            async for mac, msg in e:
                rxch = msg.decode().split(",")
                if len(rxch) == 10:
                  blinker = int(rxch[0]) # 3-way switch
                  
                  # 1 to 2ms range for 0 to 4095 input value
                  steering = int(rxch[4])
                  S1.duty_u16(int(((float(steering)*3277)/4095 + 3277)))
                  # 0.5 to 2.5ms range for 0 to 4095 input value
                  S2.duty_u16(int(((float(rxch[3])*6554)/4095 + 1638)))
                  S3.duty_u16(int(((float(rxch[2])*6554)/4095 + 1638)))
                  S4.duty_u16(int(((float(rxch[1])*6554)/4095 + 1638)))

                  throttle = int(rxch[2])
                  #deadzone check
                  midpoint = 2047
                  deadzoneplusminus = 100
                  if ((throttle < (midpoint+deadzoneplusminus)) and (throttle > (midpoint-deadzoneplusminus))):
                    #deadzone - no forward/backward movement
                    M1A.duty_u16(0)
                    M1B.duty_u16(0)

                    # Check for blinker
                    if ((blinker < blinkerthrright) or (blinker > blinkerthrleft)):
                      if (blinker < blinkerthrright):
                        # Right blinker actuated
                        LEDstring2[0] = (32, 32, 32) # Front left parking lights
                        LEDstring2[2] = (255, 0, 0)  # Back left brake on
                        if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
                          LEDstring2[1] = (0, 0, 0)    # Front right blinker dark cycle
                          LEDstring2[3] = (255, 0, 0)  # Back right brake on
                        else:
                          LEDstring2[1] = (255, 255, 0) # Front right blinker light cycle
                          LEDstring2[3] = (255, 255, 0) # Back  right blinker light cycle
                      else:
                        # Left blinker actuated
                        LEDstring2[1] = (32, 32, 32) # Front parking lights
                        LEDstring2[3] = (255, 0, 0)  # Back right brake on
                        if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
                          LEDstring2[0] = (0, 0, 0)    # Front left blinker dark cycle
                          LEDstring2[2] = (255, 0, 0)  # Back left brake on
                        else:
                          LEDstring2[0] = (255, 255, 0) # Front left blinker light cycle
                          LEDstring2[2] = (255, 255, 0) # Back  left blinker light cycle
                    else:
                      # No blinker actuated
                      LEDstring2[0] = (32, 32, 32) # Front parking lights
                      LEDstring2[1] = (32, 32, 32) # Front parking lights
                      LEDstring2[2] = (255, 0, 0) # Brake on
                      LEDstring2[3] = (255, 0, 0) # Brake on
                    LEDstring2.write()
                    
                  else:
                    if throttle > midpoint:
                      # backwards
                      M1A.duty_u16(min(32*(throttle-midpoint), 65535))
                      M1B.duty_u16(0)

                      # Check for blinker
                      if ((blinker < blinkerthrright) or (blinker > blinkerthrleft)):
                        if (blinker < blinkerthrright):
                          # Right blinker actuated
                          LEDstring2[0] = (32, 32, 32) # Front parking lights
                          LEDstring2[2] = (255, 255, 255) # Reverse on
                          if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
                            LEDstring2[1] = (0, 0, 0) # Front right blinker dark cycle
                            LEDstring2[3] = (255, 255, 255) # Reverse on
                          else:
                            LEDstring2[1] = (255, 255, 0) # Front right blinker light cycle
                            LEDstring2[3] = (255, 255, 0) # Back  right blinker light cycle
                        else:
                          # Left blinker actuated
                          LEDstring2[1] = (32, 32, 32) # Front parking lights
                          LEDstring2[3] = (255, 255, 255) # Reverse on
                          if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
                            LEDstring2[0] = (0, 0, 0) # Front left blinker dark cycle
                            LEDstring2[2] = (255, 255, 255) # Reverse on
                          else:
                            LEDstring2[0] = (255, 255, 0) # Front left blinker light cycle
                            LEDstring2[2] = (255, 255, 0) # Back  left blinker light cycle
                      else:
                        # No blinker actuated
                        LEDstring2[0] = (32, 32, 32) # Front parking lights
                        LEDstring2[1] = (32, 32, 32) # Front parking lights
                        LEDstring2[2] = (255, 255, 255) # Reverse on
                        LEDstring2[3] = (255, 255, 255) # Reverse on
                      LEDstring2.write()
                    else:
                      # forwards
                      M1A.duty_u16(0)
                      M1B.duty_u16(min(32*(midpoint-throttle), 65535))

                      # Check for blinker
                      if ((blinker < blinkerthrright) or (blinker > blinkerthrleft)):
                        if (blinker < blinkerthrright):
                          # Right blinker actuated
                          LEDstring2[0] = (255, 255, 255) # Front driving light
                          LEDstring2[2] = (32, 0, 0) # Dim red backlight
                          if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
                            LEDstring2[1] = (0, 0, 0) # Front right blinker dark cycle
                            LEDstring2[3] = (32, 0, 0) # Dim red backlight
                          else:
                            LEDstring2[1] = (255, 255, 0) # Front right blinker light cycle
                            LEDstring2[3] = (255, 255, 0) # Back  right blinker light cycle
                        else:
                          # Left blinker actuated
                          LEDstring2[1] = (255, 255, 255) # Front driving light
                          LEDstring2[3] = (32, 0, 0) # Dim red backlight
                          if ((utime.ticks_ms() % blinkertime_ms) > (blinkertime_ms / 2)):
                            LEDstring2[0] = (0, 0, 0) # Front left blinker dark cycle
                            LEDstring2[2] = (32, 0, 0) # Dim red backlight
                          else:
                            LEDstring2[0] = (255, 255, 0) # Front left blinker light cycle
                            LEDstring2[2] = (255, 255, 0) # Back  left blinker light cycle
                      else:
                        # No blinker actuated
                        LEDstring2[0] = (255, 255, 255) # Front driving light
                        LEDstring2[1] = (255, 255, 255) # Front driving light
                        LEDstring2[2] = (32, 0, 0) # Dim red backlight
                        LEDstring2[3] = (32, 0, 0) # Dim red backlight
                      LEDstring2.write()
                  
        except OSError as err:
            print("Error:", err)
            await asyncio.sleep(0.5)
            
# Main async function
async def main(e):
    # Run receive and stats tasks concurrently
    await asyncio.gather(receive_messages(e))

# Run the async program
try:
    asyncio.run(main(e))
except KeyboardInterrupt:
    print("Stopping receiver...")
    e.active(False)
    sta.active(False)
