package com.inr.serial;

import jssc.SerialPort;

/**
 * @author legrus
 *
 */
public class HVSysSupply extends HVSysUnit {

	// store the device id to return with getIdealDeviceId()
	public static int CELL_ID = 0x8013;
	
	@Override
	public int getDeviceId() {
		return CELL_ID;
	}
	

	// tell the base class about this device type
	static {
		DeviceIds.put(CELL_ID, "HV Supply");
	}

	public HVSysSupply(SerialPort port, int supplyId) {
		super(port, supplyId);
	}
	
	public int PED_CALIB_MIN = 0;
	public int PED_CALIB_MAX = 0;
	public int CHAN_CALIB = 0;

	// Sub-addresses (register offsets) in na61ps10c memory
	public static byte ADDR_STATUS = 0x02;               // status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
	public static byte AddrSetVoltage(int chan) throws Exception {
		if((chan < 0) || (chan > 9)) throw new Exception("Cannot find address to set voltage for channel " + chan);
		return (byte) (0x04 + chan*2);
	}
	public static byte ADDR_SET_PEDESTAL_VOLTAGE = 0x18;
	public static byte ADDR_RAMP_TIME = 0x26;
	public static byte ADDR_TEMPERATURE = 0x28;
	public static byte ADDR_CELL_ID = 0x00;              
	public static byte ADDR_DUMMY = 0x1e;
	public static byte ADDR_RAMP_STATUS = 0x2c;
	public static byte AddrMeasVoltage(int chan) throws Exception { 
		if((chan < 0) || (chan > 9)) throw new Exception("Cannot find address to set voltage for channel " + chan);
		return (byte) (0x2e + chan*2); 
	}
	public static byte ADDR_MEAS_PEDESTAL_VOLTAGE = 0x42;
	public static byte ADDR_VOLTAGE_CALIBRATION = 0x50;
	public static byte ADDR_PEDESTAL_VOLTAGE_CALIBRATION_MIN = 0x54;
	public static byte ADDR_PEDESTAL_VOLTAGE_CALIBRATION_MAX = 0x52;
	public static byte ADDR_VERSION_DATE_LOW = 0x56;
	public static byte ADDR_VERSION_DATE_HIGH = 0x58;
	public static byte ADDR_NEW_CELL_ADDRESS = 0x5c;
	public static int swapChannels(int id) { return 9 - ((id+9) % 10); }
}
