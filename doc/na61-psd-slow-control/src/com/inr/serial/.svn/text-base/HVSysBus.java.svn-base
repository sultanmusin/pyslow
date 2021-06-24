package com.inr.serial;

//import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Queue;
//import java.util.concurrent.PriorityBlockingQueue;

import java.util.concurrent.ArrayBlockingQueue;

import jssc.SerialPort;
import jssc.SerialPortException;
//import jssc.SerialPortTimeoutException;

public class HVSysBus implements Runnable {
	protected Queue<HVSysCommand> queue;
	protected SerialPort serialPort;
	protected String serialPortId;
	public String getSerialPortId() {
		return serialPortId;
	}

	protected Thread thread;
	
	protected Map<Integer, HVSysUnit> devices;

	public HVSysBus(String portId) throws SerialPortException{
		queue = new ArrayBlockingQueue<HVSysCommand>(100);

		devices = new HashMap<Integer, HVSysUnit>();

		serialPortId = portId;
		serialPort = new SerialPort(portId);
		
	}
	
	

	/*
	private void flushPort() throws SerialPortException {
		for(int i = 0; i < 100; i++) {
			try {
				serialPort.readBytes(1, 1);
			} catch (SerialPortTimeoutException e) {
			}
		}
	}
	*/

	public SerialPort getSerialPort() {
		return serialPort;
	}

	public Map<Integer, HVSysUnit> getDevices() {
		return devices;
	}

	public HVSysUnit getDevice(int address) {
		if(!devices.containsKey(address))
			System.out.println("HVSysUnit.getDevice(" + address + "): no such device");
		return devices.get(address);
	}

	public boolean hasDevice(int address) {
		return devices.containsKey(address);
	}

	public void setSerialPortId(String serialPortId) {
		this.serialPortId = serialPortId;
	}

	public void closePort() throws SerialPortException {
		if(serialPort.isOpened()) {
			serialPort.closePort();
		}
	}

	public HVSysUnit addDevice(HVSysUnit.DeviceType deviceType, int ledId) throws HVSysException {
		HVSysUnit device = HVSysUnit.createDevice(serialPort, ledId, deviceType);		
		devices.put(ledId, device);
		return device;
	}

	public void sendCommand(HVSysCommand command) throws HVSysException {
//		System.out.println("Bus "+ serialPortId + ": <sendCommand>");
		queue.add(command);
//		System.out.println("Bus "+ serialPortId + ":   queue length = " + queue.size());
		if(thread == null || !thread.isAlive()) {
//			System.out.println("Bus "+ serialPortId + ":   starting worker thread");
			thread = new Thread(this);
			thread.start();
		}
//		System.out.println("Bus "+ serialPortId + ": </sendCommand>");
		
	}
	
	public void waitForMessages() {
		try {
			//System.out.println("Bus "+ serialPortId + ": <waitForMessages>");
			if(null != thread && thread.isAlive()) {
				thread.join();
			}
		} catch (InterruptedException e) {
			System.out.println("Bus "+ serialPortId + ":   cannot wait for thread!");
			e.printStackTrace();
		} finally {
			//System.out.println("Bus "+ serialPortId + ": </waitForMessages>");
		}
	}

	@Override
	public void run() {
//		System.out.println("Bus "+ serialPortId + ": <run>");
		while(!queue.isEmpty()) {
			HVSysCommand cmd = queue.poll();
			try {
				
				if(serialPort.isOpened()) {
					System.out.println("Bus "+ serialPortId + " is already opened :(");
					serialPort.closePort();
				}

				if(!serialPort.isOpened()) {
					serialPort.openPort();
					serialPort.setParams(SerialPort.BAUDRATE_57600, 
			                SerialPort.DATABITS_8,
			                SerialPort.STOPBITS_1,
			                SerialPort.PARITY_NONE);
					if(!serialPort.isOpened()) {
						System.out.println("Bus "+ serialPortId + " is not opened again!!!");
					}
				}
				
				String cmdString = cmd.getCommandText();

//				System.out.println("Bus "+ serialPortId + ":   request = " + cmdString);
				serialPort.writeBytes(cmdString.getBytes());
				
				// TODO: wait for the response
//				System.out.println("Bus "+ serialPortId + ":   waiting " + new Date());
				byte[] resp = serialPort.readBytes(6, 1000); // response format: 1234\r\n means 0x1234
//				System.out.println("Bus "+ serialPortId + ":   done    " + new Date());

				String respString = new String(resp).substring(0, 4);
//				System.out.println("Bus "+ serialPortId + ":   response = 0x" + respString);
				cmd.response = Integer.parseInt(respString, 16);
//				System.out.println("Bus "+ serialPortId + ":   integer  = " + cmd.response);

				cmd.onSuccess(cmd.response);
			} catch (Exception e) {
				// TODO Auto-generated catch block
				System.out.println("Bus "+ serialPortId + ": exception!");
				e.printStackTrace();
				cmd.onFail(0);
			} finally {
				if(serialPort.isOpened()) {
//					System.out.println("Bus "+ serialPortId + ": normally closing its port");
					try {
						serialPort.closePort();
					} catch (SerialPortException e) {
						// TODO Auto-generated catch block
						System.out.println("Bus "+ serialPortId + ": well, not so normally ;)");
						e.printStackTrace();
					}
				}
//				System.out.println("Bus "+ serialPortId + ": </run>");

			}
		}
	}
	
	
}
