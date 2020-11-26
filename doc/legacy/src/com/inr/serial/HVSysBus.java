package com.inr.serial;

//import java.util.Date;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.HashMap;
import java.util.Map;
import java.util.Queue;
//import java.util.concurrent.PriorityBlockingQueue;

import java.util.concurrent.ArrayBlockingQueue;

import com.inr.slowcontrol.gui.Main;

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
		//System.out.println("Bus "+ serialPortId + ": <sendCommand " + command.getCommandText().substring(0,5) + " >");
		queue.add(command);
		//System.out.println("Bus "+ serialPortId + ":   queue length = " + queue.size());
		//if(thread == null || !thread.isAlive()) {
		synchronized (this) {
			if(thread == null) {
				thread = new Thread(this);
				thread.start();
				//System.out.println("Bus "+ serialPortId + ":   starting worker thread " + thread.getId());
			}
			
		}
		//System.out.println("Wew're in " + Thread.currentThread().getId());
		//System.out.println("Bus "+ serialPortId + ": </sendCommand " + command.getCommandText().substring(0,5) + ">");
		
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
		//System.out.println("Bus "+ serialPortId + ": <run>");
		
		while(!queue.isEmpty()) {
			HVSysCommand cmd = queue.poll();
			
			try {
			  String cmdStringNew = cmd.getCommandText();
		      //System.out.println("Command to perform "+ cmdStringNew);
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
				cmd.onFail(0);
			}
			
			
            try {
				
			  String moxaServer = serialPortId;
			  //if (Main.verbose == 1) System.out.println("Connecting to MOXA server: " + moxaServer);
			  int port = 4001;
			  
			  try {
				  
               String cmdString = cmd.getCommandText();
				  
			   Socket socket = new Socket(moxaServer, port);
			   
			   socket.setSoTimeout(2000);
			   
			   DataOutputStream outStream = new DataOutputStream(socket.getOutputStream());
			   DataInputStream inStream = new DataInputStream(socket.getInputStream());
			   
			   //System.out.println("hehe1 = " + inStream.available());
			   
			   //System.out.println("cmdString = " + cmdString);
			   
			   outStream.writeBytes(cmdString);
			   
			   //try {
				//thread.sleep(1000);
			//} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				//e.printStackTrace();
			//}
			   
			   //System.out.println("hehe2 = " + inStream.available());

			   
			   String resp = inStream.readLine();
			   
			   
			   //System.out.println("resp = " + resp);
			   
				String respString = new String(resp).substring(0, 4);
				//System.out.println("Thread ID: " + Thread.currentThread().getId() + ",  Bus "+ serialPortId + ":  command = " + cmdString.substring(0,5) + ":   response = 0x" + respString);
				//System.out.println("Bus "+ serialPortId + ":  command = " + cmdString.substring(0,5) + ":   response = 0x" + respString);
				cmd.response = Integer.parseInt(respString, 16);
//				System.out.println("Bus "+ serialPortId + ":   integer  = " + cmd.response);

				cmd.onSuccess(cmd.response);
				
			   socket.close();
			   
			  } catch (UnknownHostException e) {
			   e.printStackTrace();
			  } catch (IOException e) {
			   e.printStackTrace();
			  }
			  } catch (HVSysException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			  }
			
			
			
/* Serial port connection
			
			try {
				
				//if(serialPort.isOpened()) {
				//	System.out.println("Bus "+ serialPortId + " is already opened :(");
				//	serialPort.closePort();
				//}
				

				if(!serialPort.isOpened()) {
					serialPort.openPort();
					serialPort.setParams(SerialPort.BAUDRATE_57600, 
			                SerialPort.DATABITS_8,
			                SerialPort.STOPBITS_1,
			                SerialPort.PARITY_NONE);
					if(!serialPort.isOpened()) {
						System.out.println("Bus "+ serialPortId + " is not opened again!!!");
					}
					else {
						System.out.println("Bus "+ serialPortId + " is opened"); 	
					}
				}
				
				String cmdString = cmd.getCommandText();

				//System.out.println("Bus "+ serialPortId + ":   request = " + cmdString);
				serialPort.writeBytes(cmdString.getBytes());
				
				// TODO: wait for the response
//				System.out.println("Bus "+ serialPortId + ":   waiting " + new Date());
				byte[] resp = serialPort.readBytes(6, 2000); // response format: 1234\r\n means 0x1234
//				System.out.println("Bus "+ serialPortId + ":   done    " + new Date());

				String respString = new String(resp).substring(0, 4);
				//System.out.println("Thread ID: " + Thread.currentThread().getId() + ",  Bus "+ serialPortId + ":  command = " + cmdString.substring(0,5) + ":   response = 0x" + respString);
				//System.out.println("Bus "+ serialPortId + ":  command = " + cmdString.substring(0,5) + ":   response = 0x" + respString);
				cmd.response = Integer.parseInt(respString, 16);
//				System.out.println("Bus "+ serialPortId + ":   integer  = " + cmd.response);

				cmd.onSuccess(cmd.response);
			} catch (Exception e) {
				// TODO Auto-generated catch block
				System.out.println("Bus "+ serialPortId + ": exception!");
				System.out.println("Trying to close the port. It will be open again on the next command.");
				try {
					serialPort.closePort();
					//serialPort.purgePort(SerialPort.PURGE_RXCLEAR);
				} catch (SerialPortException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				e.printStackTrace();
				cmd.onFail(0);
			} 
			
*/
			
			/*finally {
				if(serialPort.isOpened()) {
					System.out.println("Bus "+ serialPortId + ": normally closing its port");
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
			*/
		} // while
		thread = null;
		//System.out.println("Bus "+ serialPortId + ": </run>");
		//System.out.println("Bus "+ serialPortId + " queue is empty");
	}
	
	
	
}
