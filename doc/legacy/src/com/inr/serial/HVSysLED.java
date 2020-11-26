/**
 * 
 */
package com.inr.serial;

import jssc.SerialPort;

/**
 * @author legrus
 *
 */
public class HVSysLED extends HVSysUnit {

	// store the device id to return with getIdealDeviceId()
	public static int CELL_ID = 0x8006;

	// tell the base class about this device type
	static {
		DeviceIds.put(CELL_ID, "LED Driver");
	}

	public HVSysLED(SerialPort port, int ledId) {
		super(port, ledId);
	}

	// Sub-addresses (register offsets) in na61ps10c memory
	public static byte ADDR_STATUS = 0x00;               // status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
	public static byte ADDR_AUTOREG = 0x02;              // autoreg - 1 - cell will autoregulate LED output to keep ADC readings at ADCsetpt
	public static byte ADDR_FREQ = 0x04;                 // 2 freq - generator frequency (Hz)
	                                                       // remember freq in range (1-1000) -> internal gen; freq out of range (1-1000) (for example -1 from TCL) -> external gen/sync. IF freq=0 -> LED disabled
	                                                       // should be 0 for normal triggered operation
	public static byte ADDR_AVERAGE_POINTS = 0x06;       // number of adc measurement points to average in regulation process
	public static byte ADDR_DAC_VALUE = 0x08;            // 4 DACval - will be written to LED DAC
	public static byte ADDR_ADC_SET_POINT = 0x0a;        // 5 PIN ADC setpt - cell will autoregulate LED output to keep ADC readings at ADCsetpt
	public static byte ADDR_CELL_ID = 0x0c;              // 6 new cell ID
	public static byte ADDR_AVERAGE_ADC = 0x0e;          // 7 avADC - averaged ADC readings 
	public static byte ADDR_DAC_MAX = 0x10;              // 8 Maximal DAC value during autoregulation (in steps of 100) while ADC is not saturated yet (not 
	public static byte ADDR_NEW_CELL_ADDRESS = 0x0c;     // 6 new cell ID

	
	/*
	/// Serial communication logic
	@Override
	public int getDeviceId() {
		return readShort(ADDR_CELL_ID);
	}
	
	
	@Override
	public int getIdealDeviceId() {
		return CELL_ID;
	}
	
	public int getFrequency() {
		return readShort(ADDR_FREQ);
	}
	
	public void setFrequency(int freq) {
		writeShort(ADDR_FREQ, freq);
	}
	
	public void printStatus() {
		
		int statusRegister = readShort(ADDR_STATUS);
		System.out.println("HV is                " + ((statusRegister & STATUS_ON) > 0 ? " ON" : "OFF") );
		System.out.println("Global error flag is " + ((statusRegister & STATUS_ERROR) > 0 ? " ON" : "OFF") );
		System.out.println("Ramping up/down      " + ((statusRegister & STATUS_RUD) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  1  " + ((statusRegister & STATUS_ERROR_CH1) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  2  " + ((statusRegister & STATUS_ERROR_CH2) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  3  " + ((statusRegister & STATUS_ERROR_CH3) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  4  " + ((statusRegister & STATUS_ERROR_CH4) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  5  " + ((statusRegister & STATUS_ERROR_CH5) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  6  " + ((statusRegister & STATUS_ERROR_CH6) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  7  " + ((statusRegister & STATUS_ERROR_CH7) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  8  " + ((statusRegister & STATUS_ERROR_CH8) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel  9  " + ((statusRegister & STATUS_ERROR_CH9) > 0 ? "YES" : " NO") );
		System.out.println("Error on channel 10  " + ((statusRegister & STATUS_ERROR_CH10) > 0 ? "YES" : " NO") );
		System.out.println("Supply voltage error " + ((statusRegister & STATUS_ERROR_BASE) > 0 ? "YES" : " NO") );
	}	
	*/
}
