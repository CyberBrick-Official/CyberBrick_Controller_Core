# CyberBrick ESP-NOW transmitter in CyberBrick MicroPython flavor
# To be used on CyberBrick Core, paired with X12 remote control transmitter shield
# The code in this file supports up to 3 models, model selection done via 3-way switch, connected at L1 input of X12 shield

from machine import Pin, ADC
import network
import espnow
from neopixel import NeoPixel
import time

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
mac = sta.config('mac')
mac_address = ':'.join('%02x' % b for b in mac)
print("MAC address of the transmitter:", mac_address)

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
    
# Model receiver's MAC addresses (Replace with your receiver MAC aa:bb:cc:dd:ee:ff!)
# If you plan to control only 1 model, enter the same address to all 3 lines.
# If you plan to control 2 models, you can enter 2 lines with the same model receiver MAC and continue using the 3-way switch as a binary channel.
# With a single model and all 3 addresses below filled with the same MAC, you can have full 3-position switch functionality on the model side for first channel.
# In case you wish to control the examples truck and forklift in this ESP-NOW demo,
# use receiver1_mac for Truck and both, receiver2_mac and receiver3_mac for forklift.
receiver1_mac = b'\xaa\xbb\xcc\xdd\xee\xff'
receiver2_mac = b'\xaa\xbb\xcc\xdd\xee\xff'
receiver3_mac = b'\xaa\xbb\xcc\xdd\xee\xff'

# Drive NeoPixel on CyberBrick Core
npcore = Pin(8, Pin.OUT)
np = NeoPixel(npcore, 1)
val = 16

while True:
  try:
    l1_value = l1.read()
    message = f"{l1_value},{l2.read()},{l3.read()},{r1.read()},{r2.read()},{r3.read()},{k1.value()},{k2.value()},{k3.value()},{k4.value()}"
    if l1_value < 1365: # 1/3 of 4095 
      # right switch position - model 1
      try:
        e.get_peer(receiver1_mac)
      except OSError as err:
        if err.errno == -12393: # ESP_ERR_ESPNOW_NOT_FOUND
          peer_num, encrypt_num = e.peer_count()
          if peer_num > 0:
            peers = e.get_peers()
            e.del_peer(peers[0][0])
          try:
            e.add_peer(receiver1_mac)
          except OSError as err:
            print("Failed to add peer:", err)
      if not e.send(receiver1_mac, message, True):
        e.active(False)
        wifi_reset()
        enow_reset()
        
    elif l1_value < 2730: # 2/3 of 4095
      # middle position - model 2
      try:
        e.get_peer(receiver2_mac)
      except OSError as err:
        if err.errno == -12393: # ESP_ERR_ESPNOW_NOT_FOUND
          peer_num, encrypt_num = e.peer_count()
          if peer_num > 0:
            peers = e.get_peers()
            e.del_peer(peers[0][0])
          try:
            e.add_peer(receiver2_mac)
          except OSError as err:
            print("Failed to add peer:", err)
      if not e.send(receiver2_mac, message, True):
        e.active(False)
        wifi_reset()
        enow_reset()
        
    else:
      # left position - model 3
      try:
        e.get_peer(receiver3_mac)
      except OSError as err:
        if err.errno == -12393: # ESP_ERR_ESPNOW_NOT_FOUND
          peer_num, encrypt_num = e.peer_count()
          if peer_num > 0:
            peers = e.get_peers()
            e.del_peer(peers[0][0])
          try:
            e.add_peer(receiver3_mac)
          except OSError as err:
            print("Failed to add peer:", err)
      if not e.send(receiver3_mac, message, True):
        e.active(False)
        wifi_reset()
        enow_reset()
            
    # "Breathing" LED effect in violet tone
    if (val > 255):
      np[0] = ((int)((511-val)/2), 0, (511-val))
    else:
      np[0] = ((int)(val/2), 0, val)
    np.write()
    val = val + 8 # NeoPixel intensity change step size
    if val > (511-16):
      val = 16

    time.sleep(0.02) # Send every 20 milliseconds / @50 Hz

  except OSError as err:
    print("Error:", err)
    time.sleep(0.5)
    e.active(False)
    wifi_reset()
    enow_reset()
        
  except KeyboardInterrupt:
    print("Stopping sender...")
    e.active(False)