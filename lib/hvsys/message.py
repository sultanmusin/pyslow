#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from __future__ import annotations   # For neat recursive type hints


__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



class Message:
    """
    Describes request message for HVsys electonics transmitted over a serial bus (plain text protocol). 
    All numbers for request (and response) are hex-coded values
    Message format is: 'CAARR[VVVV]M\n', where
        C is command type, one of '<' (read byte), 'r' (read short) or 'w' (write short)
        AA is device address (for example, hv supply labeled '100' has address 0x64, thus AA=64)
        RR is register offset inside device (see device classes HVsysSupply, HVsysLED)
        VVVV is specified only for 'w' (write) commands
        M is checksum (checksum check can be enabled or disabled)
    Request (and response) ends with a new line.
    """
    READ_BYTE = '<'
    READ_SHORT = 'r'
    WRITE_SHORT = 'w'
    COMMAND_TYPES = [READ_BYTE, READ_SHORT, WRITE_SHORT]

    def __init__(self, command_type: str, address: int, device: type, capability: str, value: int):
        """
        Construct a message. 
        All numbers for request (and response) are hex-coded values
        :param command_type: one of COMMAND_TYPES '<' (read byte), 'r' (read short) or 'w' (write short)
        :param address integer device address (0-255)
        :param device one of device classes [HVsysSupply, HVsysLED]
        :param capability one of device capabilities (should be present in device in the previous parameter
        :param value 0-65535, short value (ignored for read commands)
        """
        self.command_type = command_type
        self.address = address
        self.device = device

        caps = device.capabilities
        if capability not in caps:
            raise ValueError

        self.capability = capability
        self.subaddress = caps[capability]
        self.value = value
        self.checksum = '?' if self.is_read_command() else '!'    #TODO checksum

    def is_write_command(self):
        """
        If this message is a write command
        """
        return self.command_type == Message.WRITE_SHORT

    def is_read_command(self):
        """
        If this message is a read command
        """
        return self.command_type != Message.WRITE_SHORT

    @classmethod
    def decode(cls, command: str, device: type = None):
        """
        Restore the message object from string representation
        :param command: command string
        :param device: one of HVsys device types that support device.capabilities 
        """
        command_type = command[0] 
        if command_type not in Message.COMMAND_TYPES:
            raise ValueError

        address = int(command[1:3], 16)
        subaddress = int(command[3:5], 16)

        value = int(command[5:9], 16) if(command_type == Message.WRITE_SHORT) else 0
        cap = None

        if device is None:
            raise ValueError("Cannot decode message with unknown device type")
        elif subaddress not in device.capabilities_by_subaddress:
            raise ValueError("Cannot decode message for device type '%s' with invalid subaddress %d"%(device.DESCRIPTION, subaddress))
        else:
            cap = device.capabilities_by_subaddress[subaddress]

        return Message(command_type, address, device, cap, value)

    
    def __str__(self):
        """
        Convert message to string (to send over a serial line or display)
        To be used by built-in str() function
        """
        if self.command_type not in Message.COMMAND_TYPES:
            raise ValueError

        if self.command_type == Message.WRITE_SHORT:
            return "%s%02x%02x%04x%s\n" % (self.command_type, self.address, self.subaddress, self.value, self.checksum)
        else:
            return "%s%02x%02x%s\n" % (self.command_type, self.address, self.subaddress, self.checksum)
