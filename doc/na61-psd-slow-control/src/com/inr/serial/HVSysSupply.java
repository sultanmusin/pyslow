package com.inr.serial;

import jssc.SerialPort;

/**
 * @author legrus
 *
 */
public class HVSysSupply extends HVSysUnit {

	// store the device id to return with getIdealDeviceId()
	public static int CELL_ID = 0x800c;

	// tell the base class about this device type
	static {
		DeviceIds.put(CELL_ID, "HV Supply");
	}

	public HVSysSupply(SerialPort port, int supplyId) {
		super(port, supplyId);
	}

	// Sub-addresses (register offsets) in na61ps10c memory
	public static byte ADDR_STATUS = 0x00;               // status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
	public static byte AddrSetVoltage(int chan) throws Exception {
		if((chan < 0) || (chan > 9)) throw new Exception("Cannot find address to set voltage for channel " + chan);
		return (byte) (0x02 + chan*2);
	}
	public static byte ADDR_SET_PEDESTAL_VOLTAGE = 0x16;
	public static byte ADDR_RAMP_TIME = 0x18;
	public static byte ADDR_TEMPERATURE = 0x1a;
	public static byte ADDR_CELL_ID = 0x1c;              
	public static byte ADDR_DUMMY = 0x1e;
	public static byte ADDR_RAMP_STATUS = 0x20; // for reading Ramp Up/Down STATus register - bits 0-9 RUD active on corresponding channel. 												Bit 10 RUD active on PedV.
	public static byte AddrMeasVoltage(int chan) throws Exception { 
		if((chan < 0) || (chan > 9)) throw new Exception("Cannot find address to set voltage for channel " + chan);
		return (byte) (0x22 + chan*2); 
	}
	public static byte ADDR_MEAS_PEDESTAL_VOLTAGE = 0x36;
	public static byte ADDR_VOLTAGE_CALIBRATION = 0x38; //(rw) Calibration value of channels Voltage in 10mV units, i.e. to get Volts one need Vmax/100.
	public static byte ADDR_PEDESTAL_VOLTAGE_CALIBRATION = 0x3a; //(rw) Calibration value of pedestal Voltage in 10mV units, i.e. to get Volts one need eePedVmax/100.
	public static byte ADDR_VERSION_DATE_LOW = 0x3c;
	public static byte ADDR_VERSION_DATE_HIGH = 0x3e;
	public static byte ADDR_NEW_CELL_ADDRESS = 0x41;
	public static int swapChannels(int id) { return 9 - ((id+9) % 10); }
}
