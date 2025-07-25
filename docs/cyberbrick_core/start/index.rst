Getting Started with CyberBrick Core
====================================

Welcome to the MicroPython beginner's tutorial for the Multi-Function Core Board. This guide will walk you through setting up the development environment, basic programming, and common applications.

This tutorial is intended to get you started using MicroPython on the ESP32-C3
system-on-a-chip.  If it is your first time it is recommended to follow the
tutorial through in the order below.  Otherwise the sections are mostly self
contained, so feel free to skip to those that interest you.

The tutorial does not assume that you know Python, but it also does not attempt
to explain any of the details of the Python language.  Instead it provides you
with commands that are ready to run, and hopes that you will gain a bit of
Python knowledge along the way.  To learn more about Python itself please refer
to `<https://www.python.org>`__.

1. Setting Up the Development Environment
-----------------------------------------

The Multi-Function Core Board supports MicroPython programming directly without needing to re-flash the firmware. To set up your development environment using Visual Studio Code (VSCode), follow the steps below:

- A Multi-Function Core Board
- A USB-C cable
- A computer (Windows, macOS, or Linux)
- Visual Studio Code (https://code.visualstudio.com/)
- Node.js (https://nodejs.org/)
- Pymakr extension for VSCode (https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr)

1. Install Visual Studio Code
2. Install Node.js Pymakr requires Node.js as a dependency. After installation, verify it by running the following command in your terminal or command prompt: node -v
3. Install the Pymakr Extension in VSCode. Open VSCode. Click on the Extensions icon in the Activity Bar on the side of the window. Find the Pymakr extension in the search results and click "Install".

For more detailed instructions and troubleshooting, 
refer to the documentation on using VSCode for 
MicroPython programming: https://github.com/pycom/pymakr-vsc/blob/HEAD/GET_STARTED.md

If you don't want to make such complex configurations, 
you can search for "Python IDE for beginners" in the browser 
to choose a more suitable development environment.

2. Connecting to REPL
----------------------

REPL (Read Evaluate Print Loop) is an interactive terminal for MicroPython, allowing you to quickly test code and run commands.

You can refer to this website (https://docs.micropython.org/en/latest/zephyr/tutorial/repl.html) to connect to connect to the REPL of the Multi-Function Core Board.

Once connected to REPL, you can enter Python code and execute it immediately.

Example:

.. code-block:: python

   print("Hello, CyberBrick!")

3. Basic Usage
--------------

On the Multi-Function Core Board, you can use MicroPython to control peripherals such as GPIO, 
I2C, and PWM. For example, to light up the onboard RGB, 
to light up the onboard RGB, Make it light up the red light:

.. code-block:: python

   import machine
   import neopixel
   import time

   pin = machine.Pin(8, machine.Pin.OUT)
   np = neopixel.NeoPixel(pin, 1)

   np[0] = (255, 0, 0)  #(R, G, B)
   np.write()

Additionally, you can control GPIO pins, such as setting IO2 to high:

.. code-block:: python

   import machine

   io2 = machine.Pin(2, machine.Pin.OUT)
   io2.value(1)  # Set IO2 to high

4. File System
--------------

The Multi-Function Core Board includes a file system formatted in FAT, stored in the flash memory behind the MicroPython firmware.

You can use the `os` module to interact with the file system. For example, to list files:

.. code-block:: python

   import os
   print(os.listdir())
