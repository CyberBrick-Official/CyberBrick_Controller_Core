This branch adds a community driven [ESP-NOW MicroPython](https://makerworld.com/en/cyberbrick/api-doc/library/espnow.html#module-espnow) code as an alternative to the original App driven intuitively usable, but from features more limited, [CyberBrick ecosystem](https://eu.store.bambulab.com/de/collections/cyberbrick).

![grafik](https://github.com/user-attachments/assets/c2bb8b41-50f1-4dd4-9488-35fa91815801)
![grafik](https://github.com/user-attachments/assets/c8ad39b4-6703-469e-9dfb-a9e1706d7380)

The examples in this branch currently include code for [official CyberBrick remote](https://makerworld.com/de/models/1395991-cyberbrick-official-standard-remote), [truck](https://makerworld.com/de/models/1396031-cyberbrick-official-truck), [forklift](https://makerworld.com/de/models/1395994-cyberbrick-official-forklift) and the [bulldozer by MottN](https://makerworld.com/de/models/1461532-bulldozer-cyberbrick-rc). Use these example to adapt the code to further models.

What are the benefits of the code in this branch in comparison to the original CyberBrick MicroPython stack:
- Fully open-source with no hidden/frozen MicroPython modules used.
- Smoother control - full 12-bits are used to control the servos and also the motors, instead of only ca. 41 steps for motor and 102 steps for servo angle in original control. Also, the motor control PWM frequency is increased from 50 Hz to 100 Hz.
- Fully customizable NeoPixel LED driver. Actuate the various LED pixels from remote or from some logic combination of other channel states.

Downsides:
- current code is not yet able to control more than 6 PWM outputs simultanously (each servo needs 1 and each brushed motor 2 PWM outputs, so you could for example instead control 2 brushed motors and 2 servos, but not 4 servos and 2 brushed motors at the same time with this codebase). This can be remedied, by moving at least 2 PWM controls to a timer and software PWM based solution, similarly as CyberBrick original code does.
- No fancy intuitive graphical configuration environment, as is the case with CyberBrick apps. Here, the user has to configure the output mapping in receiver side MicroPython code.

On the X12 transmitter shield all inputs are being sampled and transmitted, the mapping below lists the connections in the parenthesis for the CyberBrick official standard remote:
- channel 1: L1, unsigned 12-bit value (3-way switch on Cyberbrick official standard remote)
- channel 2: L2, unsigned 12-bit value (Left horizontal (LH) stick)
- channel 3: L3, unsigned 12-bit value (Left vertical (LV) stick)
- channel 4: R1, unsigned 12-bit value (Slider)
- channel 5: R2, unsigned 12-bit value (Right horizontal (RH) stick)
- channel 6: R3, unsigned 12-bit value (Right vertical (LH) stick)
- channel 7: K1, 1-bit value, low-active (Button)
- channel 8: K2, 1-bit value, low-active (Not used)
- channel 9: K3, 1-bit value, low-active (Not used)
- channel 10: K4, 1-bit value, low-active (Not used)

The mapping for the [truck](https://makerworld.com/de/models/1396031-cyberbrick-official-truck) is:
- Servo1: steering, channel 4 (right horizontal stick)
- Motor1: throttle, channel 2 (left vertical stick)
- NeoPixel_Channel2: driven in code by throttle (LV) and steering (RH)

The mapping for the [forklift](https://makerworld.com/de/models/1395994-cyberbrick-official-forklift) is:
- Servo1: fork up/down (channel 3 (controlled by the slider on the remote))
- Motor1: right track (mix of channel 2 (left vertical stick) and channel 4 (right horizontal stick))
- Motor2: left track  (mix of channel 2 (left vertical stick) and channel 4 (right horizontal stick))
- NeoPixel_Channel2: driven in code by 3-way switch position and button press

The mapping for the [bulldozer](https://makerworld.com/de/models/1461532-bulldozer-cyberbrick-rc) is:
- Servo1: blade (channel 3 ((controlled by the slider on the remote))
- Motor1: right track (mix of channel 2 (left vertical stick) and channel 4 (right horizontal stick))
- Motor2: left track  (mix of channel 2 (left vertical stick) and channel 4 (right horizontal stick))
- NeoPixel_Channel1: cabin lights, driven in code by the button
- NeoPixel_Channel2: front lights, driven in code by the button

The model switching is carried out via 3-way switch on the remote, similarly to original CyberBrick example code. The code is not limited to controlling only 3 models.

Instructions for testing it out:
Step1. Download or check out (git clone) this espnowdemo branch.

Step 2. If you do not already have a [REPL capable MicroPython development environment setup](https://makerworld.com/en/cyberbrick/api-doc/cyberbrick_core/start/index.html#setting-up-the-development-environment), I suggest you take a look at [Arduino Lab for MicroPython](https://labs.arduino.cc/en/labs/micropython), which in my opinon will be easiest to work with.
Another easy to use option is [Thonny](https://thonny.org/).

Step 3. Hook up the first receiver side CyberBrick Core to your computer, open Arduino Lab for MicroPython and press Connect. On first start of Arduino lab for MicroPython you are asked to pick a folder where to store the files locally. Provide here the folder, where you extracted or git cloned the repository of this PR. You can directly provide the `src/community/app_espnow` subfolder of that repo.

Step 4. Open the Files window (in the top right corner of Arduino Lab for MicroPython). You might want to backup your `boot.py` from the board. To do this, select `boot.py` in the left side and then click the button with right arrow icon in the middle of the Arduino Lab for MicroPython to start copying the `boot.py` file from your CyberBrick core to your computer.

Step 5. Navigate to either `rx/truck`, `rx/forklift` or `rx/bulldozer`subfolder on the right side (double click on `rx` and then double click either on `truck`, `forklift` or `bulldozer`). Select both files (`boot.py` and `rxtruck.py` or `boot.py` and `rxforklift.py` or `boot.py` and `rxbulldozer.py`) and then click the left arrow icon to copy them to your receiver side CyberBrick Core module. You will be overwriting your stock `boot.py` file while doing so, thus be sure you made a backup into one local folder structure above in the previous step. If not, not much is lost, as that original state of the boot.py file is also available on CyberBrick Git repository at: https://raw.githubusercontent.com/CyberBrick-Official/CyberBrick_Controller_Core/refs/heads/master/src/app_rc/boot.py

Step 6. Change back to “Editor” view (top right corner of Arduino Lab for MicroPython). Hit “Reset”. The REPL console window should be open on the bottom of the screen, if not, click the tiny up arrow button on the bottom right corner of the Arduino Lab for MicroPython. Write down the MAC address of your receiver side CyberBrick Core that shold be listed in the console. You will need this later in step 10 below. If you do not see the MAC address listed, power cycle your CyberBrick Core, then reconnect and hit the “Reset” button once more.

Step 7. Disconnect the Arduino Lab for MicroPython software from your receiver core module and disconnect the USB cable as well.

Step 8. Repeat steps 3 to 7 above for further models you wish to control and do not forget to note down their individual MAC addresses.

Step 9. Connect your transmitter side CyberBrick core module with USB to your computer and hit “Connect” in the Arduino Lab for MicroPython. Go again to the Files tab. This time copy over the two files from `tx` subfolder, again overwriting the stock `boot.py` file. Do note that you do not need to backup the `boot.py` explicitly also from the second CyberBrick core, as the file will be by default exactly the same as what was found by default on the receiver core in step 4 above.

Step 10. Select on the left pane (!) the `tx.py` and hit the edit button (the button above the left arrow button in the middle between the panes). The view should switch back to Editor automatically. Scroll down to line 72:
https://github.com/rotorman/CyberBrick_Controller_Core/blob/62cd7a15465fa2eec329c070f92b5b0a35efc7c9/src/community/app_espnow/tx/tx.py#L72-L80
and enter your receiver MAC address(es) into receiver_mac(n) by replacing the AA, BB, CC, DD, EE and FF with your values that you read out in step 6 above. Hit Save.

Step 11. Disconnect the Arduino Lab for MicroPython software from your transmitter core module and disconnect the USB cable as well. Assemble the transmitter side module into your CyberBrick remote.

Step 12. Assemble your receiver side module(s) into the models.

Step 13. Power up the transmitter, power up the receiver(s). You should be able to control the models from your transmitter via ESP-NOW.
