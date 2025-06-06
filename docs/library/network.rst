****************************************
:mod:`network` --- network configuration
****************************************

.. module:: network
   :synopsis: network configuration

This module provides network drivers and routing configuration. To use this
module, a MicroPython variant/build with network capabilities must be installed.
Network drivers for specific hardware are available within this module and are
used to configure hardware network interface(s). Network services provided
by configured interfaces are then available for use via the :mod:`socket`
module.

For example::

    # connect/ show IP config a specific network interface
    # see below for examples of specific drivers
    import network
    import time
    nic = network.Driver(...)
    if not nic.isconnected():
        nic.connect()
        print("Waiting for connection...")
        while not nic.isconnected():
            time.sleep(1)
    print(nic.ifconfig())

    # now use socket as usual
    import socket
    addr = socket.getaddrinfo('micropython.org', 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(b'GET / HTTP/1.1\r\nHost: micropython.org\r\n\r\n')
    data = s.recv(1000)
    s.close()

Common network adapter interface
================================

This section describes an (implied) abstract base class for all network
interface classes implemented by :term:`MicroPython ports <MicroPython port>`
for different hardware. This means that MicroPython does not actually
provide ``AbstractNIC`` class, but any actual NIC class, as described
in the following sections, implements methods as described here.

.. class:: AbstractNIC(id=None, ...)

Instantiate a network interface object. Parameters are network interface
dependent. If there are more than one interface of the same type, the first
parameter should be `id`.

.. method:: AbstractNIC.active([is_active])

        Activate ("up") or deactivate ("down") the network interface, if
        a boolean argument is passed. Otherwise, query current state if
        no argument is provided. Most other methods require an active
        interface (behaviour of calling them on inactive interface is
        undefined).

.. method:: AbstractNIC.connect([service_id, key=None, *, ...])

       Connect the interface to a network. This method is optional, and
       available only for interfaces which are not "always connected".
       If no parameters are given, connect to the default (or the only)
       service. If a single parameter is given, it is the primary identifier
       of a service to connect to. It may be accompanied by a key
       (password) required to access said service. There can be further
       arbitrary keyword-only parameters, depending on the networking medium
       type and/or particular device. Parameters can be used to: a)
       specify alternative service identifier types; b) provide additional
       connection parameters. For various medium types, there are different
       sets of predefined/recommended parameters, among them:

       * WiFi: *bssid* keyword to connect to a specific BSSID (MAC address)

.. method:: AbstractNIC.disconnect()

       Disconnect from network.

.. method:: AbstractNIC.isconnected()

       Returns ``True`` if connected to network, otherwise returns ``False``.

.. method:: AbstractNIC.scan(*, ...)

       Scan for the available network services/connections. Returns a
       list of tuples with discovered service parameters. For various
       network media, there are different variants of predefined/
       recommended tuple formats, among them:

       * WiFi: (ssid, bssid, channel, RSSI, security, hidden). There
         may be further fields, specific to a particular device.

       The function may accept additional keyword arguments to filter scan
       results (e.g. scan for a particular service, on a particular channel,
       for services of a particular set, etc.), and to affect scan
       duration and other parameters. Where possible, parameter names
       should match those in connect().

.. method:: AbstractNIC.status([param])

       Query dynamic status information of the interface.  When called with no
       argument the return value describes the network link status.  Otherwise
       *param* should be a string naming the particular status parameter to
       retrieve.

       The return types and values are dependent on the network
       medium/technology.  Some of the parameters that may be supported are:

       * WiFi STA: use ``'rssi'`` to retrieve the RSSI of the AP signal
       * WiFi AP: use ``'stations'`` to retrieve a list of all the STAs
         connected to the AP.  The list contains tuples of the form
         (MAC, RSSI).

.. method:: AbstractNIC.ifconfig([(ip, subnet, gateway, dns)])

       Get/set IP-level network interface parameters: IP address, subnet mask,
       gateway and DNS server. When called with no arguments, this method returns
       a 4-tuple with the above information. To set the above values, pass a
       4-tuple with the required information.  For example::

        nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))

.. method:: AbstractNIC.config('param')
            AbstractNIC.config(param=value, ...)

       Get or set general network interface parameters. These methods allow to work
       with additional parameters beyond standard IP configuration (as dealt with by
       `ifconfig()`). These include network-specific and hardware-specific
       parameters. For setting parameters, the keyword argument
       syntax should be used, and multiple parameters can be set at once. For
       querying, a parameter name should be quoted as a string, and only one
       parameter can be queried at a time::

        # Set WiFi access point name (formally known as SSID) and WiFi channel
        ap.config(ssid='My AP', channel=11)
        # Query params one by one
        print(ap.config('ssid'))
        print(ap.config('channel'))

Specific network class implementations
======================================

The following concrete classes implement the AbstractNIC interface and
provide a way to control networking interfaces of various kinds.

.. toctree::
   :maxdepth: 1

   network.WLAN.rst

Network functions
=================

The following are functions available in the network module.

.. function:: country([code])

    Get or set the two-letter ISO 3166-1 Alpha-2 country code to be used for
    radio compliance.

    If the *code* parameter is provided, the country will be set to this value.
    If the function is called without parameters, it returns the current
    country.

    The default code ``"XX"`` represents the "worldwide" region.

.. function:: hostname([name])

    Get or set the hostname that will identify this device on the network. It will
    be used by all interfaces.

    This hostname is used for:
     * Sending to the DHCP server in the client request. (If using DHCP)
     * Broadcasting via mDNS. (If enabled)

    If the *name* parameter is provided, the hostname will be set to this value.
    If the function is called without parameters, it returns the current
    hostname.

    A change in hostname is typically only applied during connection. For DHCP
    this is because the hostname is part of the DHCP client request, and the
    implementation of mDNS in most ports only initialises the hostname once
    during connection. For this reason, you must set the hostname before
    activating/connecting your network interfaces.

    The length of the hostname is limited to 32 characters.
    :term:`MicroPython ports <MicroPython port>` may choose to set a lower
    limit for memory reasons. If the given name does not fit, a `ValueError`
    is raised.

    The default hostname is typically the name of the board.

.. function:: phy_mode([mode])

    Get or set the PHY mode.

    If the *mode* parameter is provided, the PHY mode will be set to this value.
    If the function is called without parameters, it returns the current PHY
    mode.

    The possible modes are defined as constants:
        * ``MODE_11B`` -- IEEE 802.11b,
        * ``MODE_11G`` -- IEEE 802.11g,
        * ``MODE_11N`` -- IEEE 802.11n.

    Availability: ESP8266.
