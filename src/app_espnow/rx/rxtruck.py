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
# * NeoPixel_Channel2: not driven by this code

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

    while True:
        try:
            async for mac, msg in e:
                rxch = msg.decode().split(",")
                if len(rxch) == 10:
                  # 1 to 2ms range for 0 to 4095 input value
                  S1.duty_u16(int(((float(rxch[4])*3277)/4095 + 3277)))
                  # 0.5 to 2.5ms range for 0 to 4095 input value
                  #S2.duty_u16(int(((float(rxch[3])*6554)/4095 + 1638)))
                  #S3.duty_u16(int(((float(rxch[2])*6554)/4095 + 1638)))
                  #S4.duty_u16(int(((float(rxch[1])*6554)/4095 + 1638)))

                  throttle = int(rxch[2])
                  #deadzone check
                  midpoint = 2047
                  deadzoneplusminus = 100
                  if ((throttle < (midpoint+deadzoneplusminus)) and (throttle > (midpoint-deadzoneplusminus))):
                    #deadzone
                    M1A.duty_u16(0)
                    M1B.duty_u16(0)
                  else:
                    if throttle > midpoint:
                      # backwards
                      M1A.duty_u16(min(32*(throttle-midpoint), 65535))
                      M1B.duty_u16(0)
                    else:
                      # forwards
                      M1A.duty_u16(0)
                      M1B.duty_u16(min(32*(midpoint-throttle), 65535))
                  
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
