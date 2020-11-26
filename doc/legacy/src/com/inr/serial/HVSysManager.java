package com.inr.serial;

import java.util.HashMap;
import java.util.Map;

import jssc.SerialPort;
import jssc.SerialPortException;

public class HVSysManager 
{
	Map<String, HVSysBus> portMap;

	public HVSysManager() {
		portMap = new HashMap<String, HVSysBus>();
	}

	public SerialPort GetSerialPort(String portId) throws SerialPortException {
		if(!portMap.containsKey(portId)) {			
			portMap.put(portId, new HVSysBus(portId));
		}
			
		return portMap.get(portId).serialPort;
	}
	
	/*
	public boolean sendCommand(HVSysCommand command) throws HVSysException {
		if(!portMap.containsKey(command.serialPortId)) {
			return false;
		}
		HVSysBus bus = portMap.get(command.serialPortId);
		bus.sendCommand(command);
		return true;
	}
	*/
}
