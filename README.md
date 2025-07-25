# CyberBrick Multi-Function Core Board
----------------------------

This is a project repository for RC controller applications and Timelapse controllers based on the [MicroPython](https://github.com/micropython/micropython) project, which works well on CyberBrick Multi-Function Core Board with Receiver/Transmitter Shield or Timelapse Kit.

This is fun, enjoy it!

## About this repositoty
------------------------

This repository contains the following content:
- [docs/](docs/) -- user documentation in Sphinx reStructuredText format. This is used to generate the online documentation.
- [src/](src/) -- project engineering code, including application code projects for RC and Timelapse.
- [tools/](tools/) -- various tools, currently including visualization tools for advanced control of throttle speed curves in RC applications.


## How to use
-------------

### RC controller application

Installation environment dependency:

    $ pip install -r requirements.txt

Enter the RC code directory:

    $ cd src/app_rc/

In the app_rc folder, you can see the startup and control code used to implement RC applications. To achieve RC application functionality, you can upload the directory contents to the onboard file system directory of Multi-Function Core Board.

It is recommended to use the mpy_cross tool to convert [control.py](src/app_rc/app/control.py) and [parser.py](src/app_rc/app/parser.py) into bytecode in (.mpy) format, with the same name as the (.py) program. When encountering the problem of insufficient RAM space during program execution.

    $ mpy-cross .\app\control.py
    $ mpy-cross .\app\parse.py

### Timelapse Kit application

    $ cd src/app_timelapse/

Enter the timelapse code directory, upload the directory contents to the onboard file system directory of Multi-Function Core Board.
