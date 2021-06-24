package com.inr.slowcontrol.gui;

import java.io.FileWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Date;
import org.apache.commons.configuration.XMLConfiguration;

import com.inr.serial.HVSysBus;
import com.inr.serial.HVSysCallback;
import com.inr.serial.HVSysLED;
import com.inr.serial.HVSysSupply;

public class ListeningThread implements Runnable {

	XMLConfiguration config;
	
	public ListeningThread(XMLConfiguration config) {
		this.config = config;
	}

	@Override
	public void run() {
		try {
			while(true) {
				// loop over all online modules in config file

				System.out.println("UpdateThread: looping over online modules " + Main.getOnlineModules());
				for(final int moduleId : Main.getOnlineModules()) {
					HVSysBus bus = Main.getModuleBus(moduleId);
					int hvAddress = Main.getModuleHVAddress(moduleId);
					int ledAddress = Main.getModuleLEDAddress(moduleId);
					HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
					HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);
					
					System.out.println("UpdateThread: moduleId = " + moduleId);
					if(Main.getCurrentModuleId() == moduleId) {
						System.out.println("UpdateThread: module is active");

						if(hv == null) {
							System.out.println("UpdateThread: no supply");
						} else {
							ArrayList<BigDecimal> voltages = Main.getMeasVoltages(bus, hv, moduleId);
							BigDecimal pedestalVoltage = Main.getPedestalMeasVoltage(bus, hv, moduleId);
							
							Main.moduleMeasPedestalTextField.setText(pedestalVoltage.toString());
							
							for(int i = 0; i < 10; i++) {
								BigDecimal v = voltages.get(i).add(pedestalVoltage);
								//System.out.println("Module = " + moduleId + " Section = " + (i+1) + " V = " + v);
								Main.moduleMeasVoltageTextFields.get(i).setText(v.toString());
							}
							// get status register
							bus.sendCommand(hv.getReadCommand(HVSysSupply.ADDR_STATUS, new HVSysCallback() {
								@Override public void onSuccess(int result) {
									Main.setModuleState(moduleId, result);
								}
							}));

							// get temperature register
							bus.sendCommand(hv.getReadCommand(HVSysSupply.ADDR_TEMPERATURE, new HVSysCallback() {
								@Override public void onSuccess(int result) {
									showAndLogModuleTemperature(moduleId, result);
								}
							}));
						}
						
						// get LED state						
						if(led == null) {
							System.out.println("UpdateThread: no LED");
						} else {
							Integer ledFrequency = Main.getLedFrequency(bus, led);							
							Main.ledFrequencyTextField.setText(ledFrequency.toString());
							Integer ledAmplitude = Main.getLedAmplitude(bus, led);							
							Main.ledAmplitudeTextField.setText(ledAmplitude.toString());

						}
						
					}
					

					bus.waitForMessages();
				}
				
				
				Thread.sleep(getConfigQueryDelay() * 1000);
			}			
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	protected Date lastLoggedDate;
	
	protected int getConfigQueryDelay() {
		return Main.getConfig().getInt("global/flags/queryDelay", 1);
	}
	
	protected void showAndLogModuleTemperature(int moduleId, int result) {
		Main.temperatureLabel.setText("T = " + result + "(" + (-0.019*result+63.9) + ")");

		Date now = new Date();
		if((lastLoggedDate == null) || (now.getTime() - lastLoggedDate.getTime() > 1000 * 60)) {
			try
			{
			    String filename= "temperature.csv";
			    FileWriter fw = new FileWriter(filename,true); //the true will append the new data
			    fw.write(new Date().toString());
			    fw.write(", " + moduleId + ", " + result + ", ");
			    fw.write(new Double(-0.019*result+63.9).toString());
			    fw.write(", \n");
			    fw.close();
			}
			catch(IOException ioe)
			{
			    System.err.println("IOException: " + ioe.getMessage());
			}
			lastLoggedDate = now;
		}
	}

}
