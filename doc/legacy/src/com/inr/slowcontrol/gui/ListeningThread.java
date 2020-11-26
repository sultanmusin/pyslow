package com.inr.slowcontrol.gui;

import java.io.FileWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;

import jssc.SerialPortTimeoutException;







//import org.apache.commons.configuration.HierarchicalConfiguration;
import org.apache.commons.configuration.XMLConfiguration;

import com.inr.serial.HVSysBus;
import com.inr.serial.HVSysCallback;
import com.inr.serial.HVSysLED;
import com.inr.serial.HVSysSupply;
import com.inr.slowcontrol.gui.Main.ModuleState;

public class ListeningThread implements Runnable {

	XMLConfiguration config;

public static BigDecimal moduleTemperatureLT;
	
	public ListeningThread(XMLConfiguration config) {
		this.config = config;
	}

	@Override
	public void run() {
		
			while(true) {
				// loop over all online modules in config file
				
				Main.listeningThreadDelay = Main.getConfig().getInt("global/flags/queryDelay", 1);

				System.out.println("UpdateThread: looping over online modules " + Main.getOnlineModules());
				
				Main.doWeHaveAnyProblem = false;
				
				for(final int moduleId : Main.getOnlineModules()) {
					
					if(Main.moduleStates.get(moduleId) ==  Main.ModuleState.Offline) continue;
					
				try {
					//HierarchicalConfiguration module = Main.configToDCS.configurationAt("module[@id=" + moduleId + "]");
					
					HVSysBus bus = Main.getModuleBus(moduleId);
					int hvAddress = Main.getModuleHVAddress(moduleId);
					int ledAddress = Main.getModuleLEDAddress(moduleId);
					HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
					HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);
					
					System.out.println("UpdateThread: moduleId = " + moduleId);
					
					ArrayList<BigDecimal> voltages = null;
					//ArrayList<BigDecimal> setVoltages = null;
					BigDecimal pedestalVoltage = null;
					BigDecimal pedestalSetVoltage = null;

				    if(hv == null) {
					  System.out.println("UpdateThread: no supply");
				    } else {
				    	
				    	Main.setErrorFlag = 0;
				    
						// get status register
						bus.sendCommand(hv.getReadCommand(HVSysSupply.ADDR_STATUS, new HVSysCallback() {
							@Override public void onSuccess(int result) {
								if(Main.getCurrentModuleId() == moduleId) {
                                  Main.setModuleState(moduleId, result, 1);
								}
								else Main.setModuleState(moduleId, result, 0);
								Main.statusRegisterToLog = result;
							}
							@Override public void onFail(int result) {
                                Main.setErrorFlag = 1;
							}
							
						}));
						
						bus.waitForMessages();
						
						if (Main.setErrorFlag == 1) throw new SerialPortTimeoutException(null, null, moduleId);
						
						// get temperature register
						bus.sendCommand(hv.getReadCommand(HVSysSupply.ADDR_TEMPERATURE, new HVSysCallback() {
							@Override public void onSuccess(int result) {
								//showAndLogModuleTemperature(moduleId, result);
								BigDecimal temperature = new BigDecimal(63.9-0.019*result);
								if(Main.getCurrentModuleId() == moduleId) {
								  Main.temperatureLabel.setText("T = " + temperature.setScale(2, RoundingMode.HALF_UP));
								}
								Main.ledTemperatureToLog = result;
								ListeningThread.moduleTemperatureLT = temperature;
							}
						}));
						
						bus.waitForMessages();
						
						
						//correct for temperature
						
						BigDecimal d = new BigDecimal(1000.);
						BigDecimal corrVoltage = ListeningThread.moduleTemperatureLT.subtract(Main.refTemperature).multiply(Main.tempSlope).divide(d);
						//Main.moduleCorrPedestalTextField.setText(pedestalCorrVoltage.setScale(2, RoundingMode.HALF_UP).toString());
						
						pedestalSetVoltage = Main.modulePedestalVoltage.get(moduleId);
						System.out.println("pedestalSetVoltage = " + pedestalSetVoltage.setScale(2, RoundingMode.HALF_UP).toString());
						System.out.println("New pedestal voltage correction = " + corrVoltage.setScale(2, RoundingMode.HALF_UP).toString());
						
						
						//pedestalSetVoltage = pedestalSetVoltage.add(corrVoltage);
						Main.setPedestalVoltage(bus, hv, pedestalSetVoltage); //correction included
						

					    voltages = Main.getMeasVoltages(bus, hv, moduleId);
					    //setVoltages = Main.getSetVoltages(bus, hv, moduleId);
						pedestalVoltage = Main.getPedestalMeasVoltage(bus, hv, moduleId);
						BigDecimal pedestalPureVoltage = Main.modulePedestalVoltage.get(moduleId);

						bus.waitForMessages();
						

						
						if(Main.getCurrentModuleId() == moduleId) {
						  Main.showCurrentModuleState();
						  //Main.moduleMeasPedestalTextField.setText(pedestalVoltage.toString());
						}
					    
				        if (Main.getModuleState(moduleId) == Main.ModuleState.Error) {
				        	
							//log error to file
							String filename= "slowControl_errors.txt";    
							try
							  {
								FileWriter fw = new FileWriter(filename,true); //the true will append the new data

								Date date = new Date();
								DateFormat df = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
								// Get the date today using Calendar object.
								String reportDate = df.format(date);
								fw.write(reportDate);
		                        fw.write(", moduleId "  + moduleId + " has Error status, statusRegister = " + Main.statusRegisterToLog + "\n");		    

								fw.close();
							  }
							catch(IOException ioe)
							  {
						        System.err.println("IOException: " + ioe.getMessage());
						      }
								
				        	//Main.doWeHaveAnyProblem = true;
				        }
				        
				        
						System.out.println("Listening thread, module = " + moduleId);
						System.out.print("[ ");
						
						for(int i = 0; i < 10; i++) {
							BigDecimal v = pedestalVoltage.subtract(voltages.get(i));
							float voltage = v.floatValue();
							//String voltageStr = String.format(Locale.ROOT, "%.2f", voltage - 1.6);
							String voltageStr = String.format(Locale.ROOT, "%.2f", voltage);
							Main.moduleMeasVoltageTextFields.get(i).setText(voltageStr);
							System.out.print(voltage + ", ");
						}
						System.out.println("]");
						
        
		/*		        
						  for(int i = 0; i < 10; i++) {
					        BigDecimal v = voltages.get(i).add(pedestalVoltage);
					        BigDecimal vToSet = setVoltages.get(i).add(pedestalSetVoltage);
					        BigDecimal vToSetFromXML = Main.getModuleConfigFloat(moduleId, "settings/hv/channel[@id=" + (i+1) + "]");
					        
					        if (Main.activateHVMonitorCheckBox.isSelected() && Math.abs(vToSetFromXML.floatValue() - vToSet.floatValue()) > 0.1) {
					        	Main.setModuleState(moduleId, Main.ModuleState.NotReference);
					        	if(Main.getCurrentModuleId() == moduleId) {
					        	  Main.moduleErrorLabels.get(i).setText("NOT REF HV!");
					        	}
					        	
								//log error to file
								String filename= "slowControl_errors.txt";    
								try
								  {
									FileWriter fw = new FileWriter(filename,true); //the true will append the new data

									Date date = new Date();
									DateFormat df = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
									// Get the date today using Calendar object.
									String reportDate = df.format(date);
									fw.write(reportDate);
			                        fw.write(", moduleId "  + moduleId + ", channel " + i + " has not REF HV " + "\n");		    
			                        fw.write("HV set = " + vToSetFromXML.floatValue() + ",  HV read = " + v.floatValue() + "\n");
									fw.close();
								  }
								catch(IOException ioe)
								  {
							        System.err.println("IOException: " + ioe.getMessage());
							      }
									
					        	Main.doWeHaveAnyProblem = true;
					        }
					        
					        
					        if(Main.getCurrentModuleId() == moduleId) {
						      //module.setProperty("channel[@id=" + (i+1) + "]",v.floatValue());
					          Main.moduleMeasVoltageTextFields.get(i).setText(v.toString());
					        }
					      }
			*/			
						

						} //else if(hv == null)
						
						// get LED state						
						if(led == null) {
							System.out.println("UpdateThread: no LED");
						} else {
							
							Integer ledFrequency = Main.getLedFrequency(bus, led);
							if(Main.getCurrentModuleId() == moduleId) {
							  Main.ledMeasFrequencyTextField.setText(ledFrequency.toString());
							}
							
							Integer ledAmplitude = Main.getLedAmplitude(bus, led);
							Main.ledAmplToLog = ledAmplitude;
							if(Main.getCurrentModuleId() == moduleId) {
							  Main.ledMeasAmplitudeTextField.setText(ledAmplitude.toString());
							}
							
							Integer ledPINADCAmplitude = Main.getPINADCAmplitude(bus, led);
							if(Main.getCurrentModuleId() == moduleId) {
							  Main.ledMeasPINADCTextField.setText(ledPINADCAmplitude.toString());
							}
						
							// get LED PIN ADC Averaged Reading						
							Integer ledPINADCAvrgAmplitude = Main.getPINADCAvrgAmplitude(bus, led);
							if(Main.getCurrentModuleId() == moduleId) {
							 Main.ledMeasPINADCAvrgTextField.setText(ledPINADCAvrgAmplitude.toString());
							}
							 Main.ledPINADCAmplAvrgToLog = ledPINADCAvrgAmplitude;							
							
							
							// get LED Average Points
							Integer ledPINADCAvrgPoints = Main.getPINADCAvrgPoints(bus, led);
							if(Main.getCurrentModuleId() == moduleId) {
							  Main.ledMeasAveragePointsTextField.setText(ledPINADCAvrgPoints.toString());
							}
						}
						
					
					 bus.waitForMessages();
					 logModuleParameters(moduleId, Main.ledTemperatureToLog, Main.ledAmplToLog, 
							             Main.ledPINADCAmplAvrgToLog, pedestalVoltage, voltages );
					 
					 Date date = new Date();
					 DateFormat df = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
					 // Get the date today using Calendar object.
					 String reportDate = df.format(date);
					 Main.timeOfLastScanTextField.setText(reportDate);
					 
					 //BigDecimal temperature = new BigDecimal(63.9-0.019*Main.ledTemperatureToLog);
					 //module.setProperty("temperature",temperature.setScale(2, RoundingMode.HALF_UP));
					 //module.setProperty("ledAmplitude",Main.ledAmplToLog);
					 //module.setProperty("pinADCAmplitude",Main.ledPINADCAmplAvrgToLog);
					 //module.setProperty("statusRegister",Main.statusRegisterToLog);
					 
				     //Main.configToDCS.save();
					 //clear error counter
				     Main.moduleErrorCounters.put(moduleId,0);
				     
				} catch (Exception e) {
					e.printStackTrace();
					//increment error counter
					Main.moduleErrorCounters.put(moduleId,Main.moduleErrorCounters.get(moduleId)+1);
					//if module is not responding 3 times - put it as Offline
					if(Main.moduleErrorCounters.get(moduleId)>2) {
					  System.out.println("Listening thread: moduleId "  + moduleId + " is not responding, set status to Offline ");
					
					  //log error to file
					  String filename= "slowControl_errors.txt";    
						try
						{
						    FileWriter fw = new FileWriter(filename,true); //the true will append the new data

						    Date date = new Date();
							DateFormat df = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
							// Get the date today using Calendar object.
							String reportDate = df.format(date);
						    fw.write(reportDate + "\n");
                            fw.write("moduleId "  + moduleId + " is not responding, set status to Offline " + "\n");		    

						    fw.close();
						}
						catch(IOException ioe)
						{
						    System.err.println("IOException: " + ioe.getMessage());
						}
					  
					  
					  Main.setModuleState(moduleId, ModuleState.Offline);
					  Main.doWeHaveAnyProblem = true;
					}
					
					Main.listeningThreadDelay = 30; // set delay to 30 sec
				}
				
				} // for(final int moduleId : Main.getOnlineModules())
				
				if (Main.doWeHaveAnyProblem & Main.activateVoiceCheckCheckBox.isSelected()) {
					Main.voiceAlarm("War ning. Pee Es Dee slow control has a problem.");
				}
				
				try {
					Thread.sleep(Main.listeningThreadDelay * 1000);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}			

	}

	//protected Date lastLoggedDate;

	
	
	
	protected void logModuleParameters(int moduleId, int moduleTemp, int ledAmpl, 
			                           int ledPINADCAmplAvrg, BigDecimal pedestalVoltage, 
			                           ArrayList<BigDecimal> voltages) {
		//Main.temperatureLabel.setText("T = " + result + "(" + (-0.019*result+63.9) + ")");
		BigDecimal temperature = new BigDecimal(63.9-0.019*moduleTemp);
	
	    String filename= "slowControl.csv";
	    
	    
		try
		{
		    FileWriter fw = new FileWriter(filename,true); //the true will append the new data

		    Date date = new Date();
		    long millis = date.getTime();
		    fw.write(String.valueOf(millis));

		    fw.write(", " + moduleId + ", " + temperature.setScale(2, RoundingMode.HALF_UP) + ", ");
		    fw.write(ledAmpl + ", " + ledPINADCAmplAvrg);
		    fw.write(", " + pedestalVoltage.toString());
		    for (int i=0; i<10; i++) {
		      BigDecimal v = pedestalVoltage.subtract(voltages.get(i));
		      fw.write(", " + v.toString());
		    }		    
		    
		    fw.write("\n");
		    fw.close();
		}
		catch(IOException ioe)
		{
		    System.err.println("IOException: " + ioe.getMessage());
		} 



	}
	
}
