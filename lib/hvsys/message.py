#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations   # For neat recursive type hints


__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



class Message:
    READ_BYTE = '<'
    READ_SHORT = 'r'
    WRITE_SHORT = 'w'
    COMMAND_TYPES = [READ_BYTE, READ_SHORT, WRITE_SHORT]

    def __init__(self, command_type: str, address: int, device: type, capability: str, value: int):
        self.command_type = command_type
        self.address = address
        self.device = device

        caps = device.capabilities
        if capability not in caps:
            raise ValueError

        self.capability = capability
        self.subaddress = caps[capability]
        self.value = value
        self.checksum = '?'     #TODO checksum


    def is_write_command(self):
        return self.command_type == Message.WRITE_SHORT

    def is_read_command(self):
        return self.command_type != Message.WRITE_SHORT

    @classmethod
    def decode(cls, command: str, device: type = None) -> Message:
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

    # To be used by built-in str() function
    def __str__(self):
        if self.command_type not in Message.COMMAND_TYPES:
            raise ValueError

        if self.command_type == Message.WRITE_SHORT:
            return "%s%02x%02x%04x%s\n" % (self.command_type, self.address, self.subaddress, self.value, self.checksum)
        else:
            return "%s%02x%02x%s\n" % (self.command_type, self.address, self.subaddress, self.checksum)

        