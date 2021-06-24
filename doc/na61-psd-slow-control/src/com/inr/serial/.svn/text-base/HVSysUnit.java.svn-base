package com.inr.serial;


import java.util.HashMap;
import java.util.Map;

import com.inr.serial.HVSysCommand.CommandType;

import jssc.SerialPort;
import jssc.SerialPortEvent;
import jssc.SerialPortEventListener;
import jssc.SerialPortException;
//import jssc.SerialPortList;
//import jssc.SerialPortTimeoutException;



public class HVSysUnit implements SerialPortEventListener {

//	protected String serialPortId;
	protected SerialPort serialPort;
		
	public static Map<Integer, String> DeviceIds = null;
	
	static {
		DeviceIds = new HashMap<Integer,String>();
	}
	
	public static String findDeviceNameById(int id)
	{
		if(DeviceIds.containsKey(id)) {
			return (String)DeviceIds.get(id);
		}
		else {
			return "unknown";
		}
	}

	public enum DeviceType {
		HV_SUPPLY(0x800c),
		LED_SOURCE(0x8006);
		
		private final int id;
		
		DeviceType(int _id) {
			this.id = _id;
		}
		
		public int getId(){
			return this.id;
		}
	}
	
	
	public static HVSysUnit createDevice(SerialPort port, int address, DeviceType deviceType) throws HVSysException {
		HVSysUnit result = null;
		switch(deviceType) {
			case HV_SUPPLY:
				result = new HVSysSupply(port, address);
				break;
			case LED_SOURCE:
				result = new HVSysLED(port, address);
				break;
			default:
				throw new HVSysException("Bad device type in createDevice(): "+ deviceType.toString());
		}
		return result;
	}
	
	protected int cellAddress;
	/*
	public static boolean pingDeviceAddress(String portId, byte cellAddress) 
	{
		HVSysUnit tester;
		int response = 0;
		try {
			tester = new HVSysUnit(portId, cellAddress);
			response = tester.readShort((byte)0);
		} catch (Exception e) {
			// just ignore 
			e.printStackTrace();
		}
		return (response >= 0);
	}
	
	public static String findDevicePort() throws Exception 
	{
		String[] portNames = SerialPortList.getPortNames();

		for(String portId : portNames) {
			System.out.println("findDevicePort: " + portId);
			boolean ping = pingDeviceAddress(portId, (byte)0);
			
			if(ping) {
				return portId;
			}
		}

		throw new Exception("No online HVSys devices. Check connection.");
	}
*/
	public HVSysUnit(SerialPort port, int address)  
	{
		serialPort = port;
		cellAddress = address;
	}
	
/*
	public static String readShortAsStringCommand(int cellAddress, byte subAddress) {
		HVSysCommand cmd = new HVSysCommand("", cellAddress, subAddress, CommandType.READ_SHORT, 0, 2);
		try {
			return cmd.getCommandText();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	public String readShortAsString(byte subAddress) {
		String cmd = readShortAsStringCommand(cellAddress, subAddress);
		
		//System.out.println(cmd);
		byte[] response;
		
		try {
			serialPort.writeBytes(cmd.getBytes());
			response = serialPort.readBytes(6, 1000);		
		}
		catch(SerialPortException e) {
			e.printStackTrace();
			return "-1";
		}
		catch(SerialPortTimeoutException e) {
			e.printStackTrace();
			return "-2";
		}
		
		return new String(response).substring(0, 4);
	}

	public int readShort(byte subAddress) {
		String response = readShortAsString(subAddress);
		return Integer.parseInt(response, 16);	
	}

	public String readByteAsString(byte subAddress) {
		String cmd = String.format("<%02x%02x_\n", cellAddress, subAddress);
		
		byte[] response;
		
		try {
			serialPort.writeBytes(cmd.getBytes());
			response = serialPort.readBytes(4, 1000);		
		}
		catch(SerialPortException e) {
			e.printStackTrace();
			return "-1";
		}
		catch(SerialPortTimeoutException e) {
			e.printStackTrace();
			return "-2";
		}
		
		return new String(response).substring(0, 2);
	}

	public int readByte(byte subAddress) {
		String response = readByteAsString(subAddress);
		return Integer.parseInt(response, 16);	
	}

	public void writeShort(byte subAddress, int value) {
		String cmd = String.format("w%02x%02x%04x_\n", cellAddress, subAddress, value & 0xFFFF);
		
		//byte[] response;
		
		try {
			serialPort.writeBytes(cmd.getBytes());
			//response = 
			//serialPort.readBytes(4, 1000);		
		}
		catch(SerialPortException e) {
			e.printStackTrace();
		}
		
		catch(SerialPortTimeoutException e) {
			e.printStackTrace();
		}
		
	}
*/
	// these get defined in derived classes
	public int getDeviceId() {
		return 0;
	}

	public int getIdealDeviceId() {
		return 0;
	}
	
	public boolean checkDeviceId() {
		return (getDeviceId() == getIdealDeviceId());
	}
/*
	public void close() {
		try {
			SerialPort port = serialPort;
			if (port.isOpened()) {
				port.closePort();
			}
		} catch(SerialPortException e) {
			e.printStackTrace();			
		}
	}
*/
	@Override
	public void serialEvent(SerialPortEvent event) {
		int nBytes = event.getEventType();
		try {
			byte[] buffer = serialPort.readBytes(nBytes);
			System.out.println("Recv: " + new String(buffer));
		} catch(SerialPortException e) {
			e.printStackTrace();			
		}
		
	}

	// helperz
	protected HVSysCommand getCommand(int subAddress, CommandType commandType) {
		return new HVSysCommand(cellAddress, subAddress, commandType, 0, 1, null);
	}
	
	protected HVSysCommand getCommand(int subAddress, CommandType commandType, int value, int priority) {
		return new HVSysCommand(cellAddress, subAddress, commandType, value, priority, null);
	}
	
	protected HVSysCommand getCommand(int subAddress, CommandType commandType, HVSysCallback callback) {
		return new HVSysCommand(cellAddress, subAddress, commandType, 0, 1, callback);
	}
	
	protected HVSysCommand getCommand(int subAddress, CommandType commandType, int value, int priority, HVSysCallback callback) {
		return new HVSysCommand(cellAddress, subAddress, commandType, value, priority, callback);
	}
	

	public HVSysCommand getReadCommand(int subAddress) {
		return getCommand(subAddress, CommandType.READ_SHORT);
	}
	
	public HVSysCommand getReadCommand(int subAddress, HVSysCallback callback) {
		return getCommand(subAddress, CommandType.READ_SHORT, callback);
	}

	public HVSysCommand getWriteCommand(int subAddress, int value) {
		return getCommand(subAddress, CommandType.WRITE_SHORT, value, 2);
	}
	
	public HVSysCommand getWriteCommand(int subAddress, int value, HVSysCallback callback) {
		return getCommand(subAddress, CommandType.WRITE_SHORT, value, 2, callback);
	}

	public static int POWER_OFF = 0;
	public static int POWER_ON = 1;
	
	
}