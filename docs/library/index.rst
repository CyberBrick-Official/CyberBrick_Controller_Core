.. _micropython_lib:

MicroPython libraries
=====================

.. warning::

   Important summary of this section

   * MicroPython provides built-in modules that mirror the functionality of the
     :ref:`Python standard library <micropython_lib_python>` (e.g. :mod:`os`,
     :mod:`time`), as well as :ref:`MicroPython-specific modules <micropython_lib_micropython>`
     (e.g. :mod:`bluetooth`, :mod:`machine`).
   * Most Python standard library modules implement a subset of the
     functionality of the equivalent Python module, and in a few cases provide
     some MicroPython-specific extensions (e.g. :mod:`array`, :mod:`os`)
   * Due to resource constraints or other limitations, some ports or firmware
     versions may not include all the functionality documented here.
   * To allow for extensibility, some built-in modules can be
     :ref:`extended from Python code <micropython_lib_extending>` loaded onto
     the device filesystem.

This chapter describes modules (function and class libraries) which are built
into MicroPython. This documentation in general aspires to describe all modules
and functions/classes which are implemented in the MicroPython project.
However, MicroPython is highly configurable, and each port to a particular
board/embedded system may include only a subset of the available MicroPython
libraries.

With that in mind, please be warned that some functions/classes in a module (or
even the entire module) described in this documentation **may be unavailable**
in a particular build of MicroPython on a particular system. The best place to
find general information of the availability/non-availability of a particular
feature is the "General Information" section which contains information
pertaining to a specific :term:`MicroPython port`.

On some ports you are able to discover the available, built-in libraries that
can be imported by entering the following at the :term:`REPL`::

    help('modules')

Beyond the built-in libraries described in this documentation, many more
modules from the Python standard library, as well as further MicroPython
extensions to it, can be found in :term:`micropython-lib`.

.. _micropython_lib_python:

Python standard libraries and micro-libraries
---------------------------------------------

The following standard Python libraries have been "micro-ified" to fit in with
the philosophy of MicroPython.  They provide the core functionality of that
module and are intended to be a drop-in replacement for the standard Python
library.

.. toctree::
   :maxdepth: 1

   array.rst
   asyncio.rst
   binascii.rst
   builtins.rst
   cmath.rst
   collections.rst
   errno.rst
   gc.rst
   gzip.rst
   hashlib.rst
   heapq.rst
   io.rst
   json.rst
   math.rst
   os.rst
   platform.rst
   random.rst
   re.rst
   select.rst
   socket.rst
   ssl.rst
   struct.rst
   sys.rst
   time.rst
   zlib.rst
   _thread.rst

.. _micropython_lib_micropython:

MicroPython-specific libraries
------------------------------

Functionality specific to the MicroPython implementation is available in
the following libraries.

.. toctree::
   :maxdepth: 1

   btree.rst
   cryptolib.rst
   deflate.rst
   framebuf.rst
   machine.rst
   micropython.rst
   neopixel.rst
   network.rst
   uctypes.rst
   vfs.rst

Libraries specific to the ESP8266 and ESP32
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following libraries are specific to the ESP8266 and ESP32.

.. toctree::
  :maxdepth: 2

  esp.rst
  esp32.rst

.. toctree::
  :maxdepth: 1

  espnow.rst


.. _micropython_lib_extending:

Extending built-in libraries from Python
----------------------------------------

A subset of the built-in modules are able to be extended by Python code by
providing a module of the same name in the filesystem. This extensibility
applies to the following Python standard library modules which are built-in to
the firmware: ``array``, ``binascii``, ``collections``, ``errno``, ``gzip``,
``hashlib``, ``heapq``, ``io``, ``json``, ``os``, ``platform``, ``random``,
``re``, ``select``, ``socket``, ``ssl``, ``struct``, ``time`` ``zlib``, as well
as the MicroPython-specific ``machine`` module. All other built-in modules
cannot be extended from the filesystem.

This allows the user to provide an extended implementation of a built-in library
(perhaps to provide additional CPython compatibility or missing functionality).
This is used extensively in :term:`micropython-lib`, see :ref:`packages` for
more information. The filesystem module will typically do a wildcard import of
the built-in module in order to inherit all the globals (classes, functions and
variables) from the built-in.

In MicroPython v1.21.0 and higher, to prevent the filesystem module from
importing itself, it can force an import of the built-in module it by
temporarily clearing ``sys.path`` during the import. For example, to extend the
``time`` module from Python, a file named ``time.py`` on the filesystem would
do the following::

  _path = sys.path
  sys.path = ()
  try:
    from time import *
  finally:
    sys.path = _path
    del _path

  def extra_method():
    pass

The result is that ``time.py`` contains all the globals of the built-in ``time``
module, but adds ``extra_method``.

In earlier versions of MicroPython, you can force an import of a built-in module
by appending a ``u`` to the start of its name. For example, ``import utime``
instead of ``import time``. For example, ``time.py`` on the filesystem could
look like::

  from utime import *

  def extra_method():
    pass

This way is still supported, but the ``sys.path`` method described above is now
preferred as the ``u``-prefix will be removed from the names of built-in
modules in a future version of MicroPython.

*Other than when it specifically needs to force the use of the built-in module,
code should always use* ``import module`` *rather than* ``import umodule``.

.. _micropython_lib_moditications:

Modifications to built-in MicroPython interfaces on CyberBrick Multi-Function Core Board
------------------------------------------------------------------------------------------

To protect intellectual property and ensure the stability of both software and hardware, 
the CyberBrick Multi-Function Core Board modifies the default MicroPython firmware 
by removing certain built-in APIs that could potentially bypass system safeguards, 
compromise storage integrity, or allow unauthorized low-level access.

The following built-in APIs have been intentionally **disabled or removed** in
the CyberBrick Multi-Function Core Board firmware:

- ``uos.dupterm``
- ``os.dupterm``
- ``esp32.set_boot``
- ``esp32.get_next_update``
- ``esp32.mark_app_valid_cancel_rollback``
- ``falshbdeb.Partition.set_boot``
- ``falshbdeb.Partition.get_next_update``
- ``falshbdeb.Partition.mark_app_valid_cancel_rollback``
- ``esp.flash_read``
- ``esp.flash_write``
- ``esp.flash_erase``
- ``machine.read_ram``
- ``machine.mem8``
- ``machine.mem16``
- ``machine.mem32``
- ``uctypes.bytes_at``
- ``uctypes.bytearray_at``
- ``uctypes.struct``
- ``bluetooth``
- ``webrepl``

These removals are designed to:

- Prevent arbitrary memory access and writing to flash, which could lead to
  **firmware corruption** or **system instability**.
- Remove rollback and bootloader control features that might allow
  **unauthorized firmware manipulation**.
- Restrict low-level Bluetooth stack access and disable WebREPL to **improve
  device security** and reduce the attack surface.

These limitations ensure a more secure and reliable environment tailored
specifically for CyberBrick educational and commercial applications. Developers
are encouraged to use the exposed APIs and extensions documented in this guide.