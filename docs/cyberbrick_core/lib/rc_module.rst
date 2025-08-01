rc_module
=========

This module provides functionality for radio control (RC) slave operations.

.. function:: rc_master_init()

   Initializes the RC master module.

   **Description**

   This function sets up the necessary configurations and resources for the RC master to operate. It is essential to call this function before starting any RC tasks.

   **Example**

   .. code-block:: python

      import rc_module

      rc_module.rc_master_init()

.. function:: rc_master_data()

   Retrieves the current RC data.

   **Description**

   This function returns the current RC data from the RC suite's remote control transmitter. 
   `rc_master_data()` 
   returns a tuple corresponding to the transmitter's interface numbers: [L1, L2, L3, R1, R2, R3, K1, K2, K3, K4]. 
   The first six elements are ADC values [0, 4095] from the transmitter's six joystick channels, 
   and the last four elements are high/low states [0, 1] from the transmitter's four button IOs. 
   For example, [1885, 1960, 1992, 2106, 1945, 2009, 1, 1, 1, 1].

   **Parameters**

   None

   **Returns**

   A tuple containing the current RC data, or None if no data is available.

   **Example**

   .. code-block:: python

      import rc_module

      rc_module.rc_master_init()
      rc_data = rc_module.rc_master_data()
      if rc_data:
          print("Joystick ADC values:", rc_data[:6])
          print("Button states:", rc_data[6:])
      else:
          print("No data is available.")

.. function:: rc_slave_init()

   Initializes the RC slave module.

   **Description**

   The bbl_rc_slave module is part of the RC car suite, serving as the receiver component. 
   It provides functionalities to manage and operate the RC receiver, enabling communication with the RC transmitter. 
   This module is essential for loading and configuring the resources necessary for the receiver's operation, 
   ensuring effective control over the RC car's movements and actions.

   **Example**

   .. code-block:: python

      import rc_module

      rc_module.rc_slave_init()

.. function:: rc_slave_data()

   Retrieves the current RC data.

   **Description**

   This function returns the current RC data from the RC suite's remote control transmitter. 
   When the transmitter and receiver are paired and the transmitter is operational, `rc_slave_data()` 
   returns a tuple corresponding to the transmitter's interface numbers: [L1, L2, L3, R1, R2, R3, K1, K2, K3, K4]. 
   The first six elements are ADC values [0, 4095] from the transmitter's six joystick channels, 
   and the last four elements are high/low states [0, 1] from the transmitter's four button IOs. 
   For example, [1885, 1960, 1992, 2106, 1945, 2009, 1, 1, 1, 1]. If the transmitter is not paired or operational, 
   `rc_slave_data()` returns None.

   **Parameters**

   None

   **Returns**

   A tuple containing the current RC data, or None if no data is available.

   **Example**

   .. code-block:: python

      import rc_module

      rc_module.rc_slave_init()
      rc_data = rc_module.rc_slave_data()
      if rc_data:
          print("Joystick ADC values:", rc_data[:6])
          print("Button states:", rc_data[6:])
      else:
          print("No data received. Please check if the transmitter is paired and operational.")

.. function:: rc_index()

   Retrieves the current RC index.

   **Description**

   This function returns the current index of the receiver board,
   which is determined during pairing with the transmitter.
   The return values may be 0, 1, 2, where 0 represents unpaired,
   1 represents configured to receive as slave 1, and 2 represents slave 2

   **Parameters**

   None

   **Returns**

   The current RC index.

   **Example**

   .. code-block:: python

      import rc_module

      rc_index = rc_module.rc_index()
      print("RC Index:", rc_index)

.. function:: rc_simulation()

   Retrieves the current RC testing and control instructions.

   **Description**

   This function will receive RC related testing and control instructions, which are usually from PC or APP.

   **Parameters**

   None

   **Returns**

   Instruction of string type.

   **Example**

   .. code-block:: python

      import time
      import rc_module

      while True:
         simulation = rc_module.rc_simulation()
         if simulation:
            print("RC simulation:", simulation)
         time.sleep(0.1)

.. function:: file_transfer()

   Synchronizes the RC configuration file from the CyberBrick App or PC.

   **Description**

   This function is used to synchronize the configuration file 
   named ``rc_config`` (in JSON format) from the CyberBrick App or a PC client. 
   The ``rc_config`` file contains parameters relevant to RC operations 
   such as channel mappings, thresholds, or user-defined presets. 
   The function should be polled regularly to ensure timely updates.

   **Parameters**

   None

   **Returns**

   ``True`` if a new configuration file has been received and synchronized; ``False`` otherwise.

   **Example**

   .. code-block:: python

      import time
      import rc_module

      while True:
         if rc_module.file_transfer():
            print("New RC configuration received.")
         time.sleep(0.1)
