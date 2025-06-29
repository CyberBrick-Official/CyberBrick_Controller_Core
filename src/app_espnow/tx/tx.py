# CyberBrick ESP-NOW transmitter in CyberBrick MicroPython flavor
# To be used on CyberBrick Core, paired with X12 remote control transmitter shield

from machine import Pin, ADC
import network
import aioespnow
import asyncio
from neopixel import NeoPixel

"""
The outgoing telegram via ESP-NOW is the following:
1) L1, unsigned 12-bit value (3-way switch on Cyberbrick official standard remote)
2) L2, unsigned 12-bit value (Left horizontal (LH) stick)
3) L3, unsigned 12-bit value (Left vertical (LV) stick)
4) R1, unsigned 12-bit value (Slider)
5) R2, unsigned 12-bit value (Right horizontal (RH) stick)
6) R3, unsigned 12-bit value (Right vertical (LH) stick)
7) K1, 1-bit value, low-active (Button)
8) K2, 1-bit value, low-active (Not used)
9) K3, 1-bit value, low-active (Not used)
10) K4, 1-bit value, low-active (Not used)
"""

# Comment lists controls as used by the CyberBrick official standard remote
l1 = ADC(Pin(0), atten=ADC.ATTN_11DB) # 3-way-switch
l2 = ADC(Pin(1), atten=ADC.ATTN_11DB) # LH
l3 = ADC(Pin(2), atten=ADC.ATTN_11DB) # LV
r1 = ADC(Pin(3), atten=ADC.ATTN_11DB) # S1
r2 = ADC(Pin(4), atten=ADC.ATTN_11DB) # RH
r3 = ADC(Pin(5), atten=ADC.ATTN_11DB) # RV
k1 = Pin(6, Pin.IN)  # Button
k2 = Pin(7, Pin.IN)  # Not used
k3 = Pin(21, Pin.IN) # Not used
k4 = Pin(20, Pin.IN) # Not used

# Initialize Wi-Fi in station mode
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel=1)  # Set channel explicitly if packets are not delivered
sta.disconnect()

# Initialize AIOESPNow
e = aioespnow.AIOESPNow()
try:
    e.active(True)
except OSError as err:
    print("Failed to initialize AIOESPNow:", err)
    raise
    
# Receiver's MAC address (Replace with your receiver MAC aa:bb:cc:dd:ee:ff!)
receiver_mac = b'\xaa\xbb\xcc\xdd\xee\xff'

# Add peer
try:
    e.add_peer(receiver_mac)
except OSError as err:
    print("Failed to add peer:", err)
    raise

# Async function to send messages
async def send_messages(e, peer):
    # Drive NeoPixel on CyberBrick Core
    npcore = Pin(8, Pin.OUT)
    np = NeoPixel(npcore, 1)
    val = 16
    while True:
        try:
            message = f"{l1.read()},{l2.read()},{l3.read()},{r1.read()},{r2.read()},{r3.read()},{k1.value()},{k2.value()},{k3.value()},{k4.value()}"
            await e.asend(peer, message)  
            # "Breathing" LED effect in violet tone
            if (val > 255):
              np[0] = ((int)((511-val)/2), 0, (511-val))
            else:
              np[0] = ((int)(val/2), 0, val)
            np.write()
            val = val + 8 # NeoPixel intensity change step size
            if val > (511-16):
              val = 16
            await asyncio.sleep(0.02)  # Send every 20 milliseconds / @50 Hz
        
        except OSError as err:
            print("Error:", err)
            await asyncio.sleep(0.5)

# Main async function
async def main(e, peer):
    await send_messages(e, peer)

# Run the async program
try:
    asyncio.run(main(e, receiver_mac))
except KeyboardInterrupt:
    print("Stopping sender...")
    e.active(False)
    sta.active(False)
