package com.inr.slowcontrol.gui;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
//import java.awt.event.ActionEvent;
//import java.awt.event.ActionListener;
//import java.awt.event.FocusEvent;
//import java.awt.event.FocusListener;
import java.awt.event.*;
import java.io.DataOutputStream;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Map.Entry;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSeparator;
import javax.swing.JTextField;
import javax.swing.JCheckBox;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.HierarchicalConfiguration;
import org.apache.commons.configuration.XMLConfiguration;
import org.apache.commons.configuration.tree.xpath.XPathExpressionEngine;

import com.inr.serial.HVSysBus;
import com.inr.serial.HVSysCallback;
import com.inr.serial.HVSysException;
import com.inr.serial.HVSysLED;
import com.inr.serial.HVSysSupply;
import com.inr.serial.HVSysUnit;
import com.inr.serial.HVSysUnit.DeviceType;

public class Main {
	public enum ModuleState {
		Offline,
		PowerOff,
		PowerOn,
		Error,
		NotReference
	};
	
	public static Map<Integer, ModuleState> moduleStates;
	public static Map<Integer, Integer> moduleErrorCounters;
	public static Map<Integer, BigDecimal> modulePedestalVoltage;
	
	private static Map<Integer, JButton> moduleButtons;
	
	private static List<HVSysBus> hvsysBuses;
	private static Map<String, HVSysBus> busNames;
	private static XMLConfiguration config;
	
	public static int verbose;
	public static int useVoiceNotifications;
	public static String voiceServer;
	public static int monitorHV;
	public static BigDecimal refTemperature;
	public static BigDecimal tempSlope;
	public static BigDecimal moduleTemperature;
	
	//public static XMLConfiguration configToDCS;
	public static XMLConfiguration getConfig() {
		return config;
	}
	
	//public static XMLConfiguration getConfigToDCS() {
	//	return configToDCS;
	//}

	private static ArrayList<Integer> moduleIds;
	private static JLabel moduleHeaderLabel;
	private static ArrayList<JTextField> moduleSetVoltageTextFields;
	private static ArrayList<JTextField> moduleCorrVoltageTextFields;
	public static ArrayList<JTextField> moduleMeasVoltageTextFields;
	public static ArrayList<JLabel> moduleErrorLabels;
	private static JTextField moduleSetPedestalTextField;
	private static JTextField moduleCorrPedestalTextField;
	public static JTextField moduleMeasPedestalTextField;
	private static JTextField moduleSetRefTempTextField;
	private static JTextField moduleRefTempTextField;
	private static JTextField moduleTempSlopeTextField;
	public static JLabel modulePedestalErrorLabel;
	public static JTextField ledFrequencyTextField;
	public static JTextField ledMeasFrequencyTextField;
	public static JTextField ledAmplitudeTextField;
	public static JTextField ledMeasAmplitudeTextField;
	//public static JButton setLedFrequencyButton;
	//public static JButton setLedAmplitudeButton;
	public static JTextField ledSetPINADCTextField;
	public static JTextField ledMeasPINADCTextField;
	public static JTextField ledMeasPINADCAvrgTextField;
	public static JTextField ledSetAveragePointsTextField;
	public static JTextField ledMeasAveragePointsTextField;
	
	public static JTextField  timeOfLastScanTextField;

	public static JCheckBox setLedAutoCheckBox;
	private static int currentModuleId;
	
	private static ListeningThread listeningThread;
	
	private static HVSysSupply supply;
	public static JLabel temperatureLabel;
	
	public static int ledTemperatureToLog;
	public static int ledAmplToLog;
	public static int ledPINADCAmplToLog;
	public static int ledPINADCAmplAvrgToLog;
	public static int statusRegisterToLog;
	
	public static boolean doWeHaveAnyProblem;
	
	private static JButton hvGlobalOnButton;
	private static JButton hvGlobalOffButton;
	
	private static JButton ledGlobalFrequencyButton;
	private static JLabel ledGlobalFrequencyLabel;
	public static JTextField ledGlobalFrequencyTextField;
	public static JTextField ledGlobalFrequencySetTextField;
	private static int ledGlobalFrequency;
	
	private static int ledAmpReading;
	private static int ledAutoModeReading;
	private static int ledPINADCReading;
	private static int ledPINADCAvrgReading;
	private static int ledAvrgPointsReading;
	private static JButton hvOnButton;
	private static JButton hvOffButton;
	private static JButton hvLoadButton;
	private static JButton hvSaveButton;
	
	public static JCheckBox activateVoiceCheckCheckBox;
	public static JCheckBox activateHVMonitorCheckBox;
	
	public static int setErrorFlag;
	public static int listeningThreadDelay;
	//private static JButton exitButton;
	
	private static JButton hvLoadOneModuleButton;

	public static void main(String[] args) {
		javax.swing.SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                try {
                	loadConfiguration();
	            	loadModuleStates();

	            	createAndShowGUI();
	            	clearModuleDisplay();
	            	
	            	hvLoadFromXMLToModules();
	            	
	            	setSelectedModule(getOnlineModules().get(0));
	            	showModuleStates();
	            	showCurrentModuleState();
	            	
	            	
	            	addGuiListeners();
	            	
	            	if (Main.activateVoiceCheckCheckBox.isSelected()) {
	            		voiceAlarm("Hello. Welcome to Pee Es Dee slow control");
	            	}
	            	
	                startListeningThread();
	                
	                memDump();
	                
				} catch (HVSysException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
            }

        });
	}

	protected static void memDump() {
		/*
		try {
			final int moduleId = getCurrentModuleId();
			HVSysBus bus = Main.getModuleBus(moduleId);
			int hvAddress = Main.getModuleHVAddress(moduleId);
			int ledAddress = Main.getModuleLEDAddress(moduleId);
			HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
			HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);
	
			for(int i = 0; i < 0x40; i+=2) {
				final int addr = i;
				bus.sendCommand(hv.getReadCommand(i, new HVSysCallback() {
					@Override public void onSuccess(int result) {
						System.out.println(String.format("%2x = %d", addr, result));
					}
				}));
			}
			bus.waitForMessages();
			System.exit(1);
			
		} catch (HVSysException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		*/
	}

	protected static void showCurrentModuleState() {
		System.out.println("showCurrentModuleState is called");
		
		moduleSetRefTempTextField.setText(refTemperature.toString());
		moduleRefTempTextField.setText(refTemperature.toString());
		
		moduleTempSlopeTextField.setText(tempSlope.toString());
		
		try{
			final int moduleId = getCurrentModuleId();
			HVSysBus bus = Main.getModuleBus(moduleId);
			int hvAddress = Main.getModuleHVAddress(moduleId);
			int ledAddress = Main.getModuleLEDAddress(moduleId);
			HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
			HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);
	
			if(hv == null) {
				System.out.println("UpdateThread: no supply");
			} else {
				ArrayList<BigDecimal> setVoltages = Main.getSetVoltages(bus, hv, moduleId);
				ArrayList<BigDecimal> measVoltages = Main.getMeasVoltages(bus, hv, moduleId);
				BigDecimal pedestalPureSetVoltage = Main.modulePedestalVoltage.get(moduleId);
				BigDecimal pedestalSetVoltage = Main.getPedestalSetVoltage(bus, hv, moduleId);//correction already included
				BigDecimal pedestalMeasVoltage = Main.getPedestalMeasVoltage(bus, hv, moduleId);

				Main.moduleSetPedestalTextField.setText(pedestalPureSetVoltage.setScale(2, RoundingMode.HALF_UP).toString());
				Main.moduleCorrPedestalTextField.setText(pedestalSetVoltage.toString());
				Main.moduleMeasPedestalTextField.setText(pedestalMeasVoltage.toString());
				
				
				// get status register
				bus.sendCommand(hv.getReadCommand(HVSysSupply.ADDR_STATUS, new HVSysCallback() {
					@Override public void onSuccess(int result) {
						Main.setModuleState(moduleId, result, 1);
					}
				}));
				
				bus.waitForMessages();
							
				
				// get temperature register
				bus.sendCommand(hv.getReadCommand(HVSysSupply.ADDR_TEMPERATURE, new HVSysCallback() {
					@Override public void onSuccess(int result) {
						//Main.temperatureLabel.setText("T = " + result + "(" + (-0.019*result+63.9) + ")");
						BigDecimal temperature = new BigDecimal(63.9-0.019*result);
						Main.temperatureLabel.setText("T = " + temperature.setScale(2, RoundingMode.HALF_UP));
						Main.moduleTemperature = temperature;
					}
				}));
				
				bus.waitForMessages();
				//
                //BigDecimal d = new BigDecimal(1000.);
				//BigDecimal pedestalCorrVoltage = pedestalSetVoltage.add(moduleTemperature.subtract(refTemperature).multiply(tempSlope).divide(d));
				//Main.moduleCorrPedestalTextField.setText(pedestalSetVoltage.setScale(2, RoundingMode.HALF_UP).toString());
				
				System.out.println("Module = " + moduleId);
				System.out.print("[ ");
				for(int i = 0; i < 10; i++) {
					BigDecimal v = pedestalPureSetVoltage.subtract(setVoltages.get(i));
					BigDecimal vCorr = pedestalSetVoltage.subtract(setVoltages.get(i));
					float voltage = v.floatValue();
					float voltageCorr = vCorr.floatValue();
					System.out.print(voltage + ", ");
					//String voltageStr = String.format(Locale.ROOT, "%.2f", voltage - 1.6);
					String voltageStr = String.format(Locale.ROOT, "%.2f", voltage);
					String voltageCorrStr = String.format(Locale.ROOT, "%.2f", voltageCorr);
					Main.moduleSetVoltageTextFields.get(i).setText(voltageStr);
					Main.moduleCorrVoltageTextFields.get(i).setText(voltageCorrStr);
					
					BigDecimal vToSetFromXML = Main.getModuleConfigFloat(moduleId, "settings/hv/channel[@id=" + (i+1) + "]");
			        
			        if (Main.activateHVMonitorCheckBox.isSelected() && Math.abs(vToSetFromXML.floatValue() - v.floatValue()) > 0.1) {
			        	Main.setModuleState(moduleId, Main.ModuleState.NotReference);
			        	Main.moduleErrorLabels.get(i).setText("NOT REF HV!");
			        }
			        
					
				}
				System.out.println("]");
				
				for(int i = 0; i < 10; i++) {
					BigDecimal v = pedestalMeasVoltage.subtract(measVoltages.get(i));
					float voltage = v.floatValue();
					//String voltageStr = String.format(Locale.ROOT, "%.2f", voltage - 1.6);
					String voltageStr = String.format(Locale.ROOT, "%.2f", voltage);
					Main.moduleMeasVoltageTextFields.get(i).setText(voltageStr);
				}

				


				
				// get temperature register
				bus.sendCommand(hv.getReadCommand(HVSysSupply.ADDR_TEMPERATURE, new HVSysCallback() {
					@Override public void onSuccess(int result) {
						//Main.temperatureLabel.setText("T = " + result + "(" + (-0.019*result+63.9) + ")");
						BigDecimal temperature = new BigDecimal(63.9-0.019*result);
						Main.temperatureLabel.setText("T = " + temperature.setScale(2, RoundingMode.HALF_UP));
					}
				}));


			}
			
			// get LED state						
			if(led == null) {
				System.out.println("UpdateThread: no LED");
			} else {
				// get LED freq.
				Integer ledFrequency = Main.getLedFrequency(bus, led);							
				Main.ledMeasFrequencyTextField.setText(ledFrequency.toString());
				Main.ledFrequencyTextField.setText(ledFrequency.toString());
				
				// get LED DAC 
				Integer ledAmplitude = Main.getLedAmplitude(bus, led);							
				Main.ledMeasAmplitudeTextField.setText(ledAmplitude.toString());
				Main.ledAmplitudeTextField.setText(ledAmplitude.toString());
				
				// get LED PIN ADC 
				Integer ledPINADCAmplitude = Main.getPINADCAmplitude(bus, led);							
				Main.ledMeasPINADCTextField.setText(ledPINADCAmplitude.toString());
				Main.ledSetPINADCTextField.setText(ledPINADCAmplitude.toString());
				
				// get LED PIN ADC Averaged Reading
				Integer ledPINADCAvrgAmplitude = Main.getPINADCAvrgAmplitude(bus, led);							
				Main.ledMeasPINADCAvrgTextField.setText(ledPINADCAvrgAmplitude.toString());
				
				// get LED Average Points
				Integer ledPINADCAvrgPoints = Main.getPINADCAvrgPoints(bus, led);							
				Main.ledMeasAveragePointsTextField.setText(ledPINADCAvrgPoints.toString());
				Main.ledSetAveragePointsTextField.setText(ledPINADCAvrgPoints.toString());
				
				// get auto-mode register
				Integer ledAuto = getLedAutoMode(bus, led);
				if (ledAuto==0) setLedAutoCheckBox.setSelected(false);
				else if (ledAuto==1)setLedAutoCheckBox.setSelected(true);

			}

			
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		
		
		System.out.println("showCurrentModuleState is finished");
	}

	protected static void addGuiListeners() {
		for(int i = 0; i < 10; i++) {
			final JTextField textField = moduleSetVoltageTextFields.get(i);
			final int id = i;
			
			textField.addKeyListener(new KeyListener() {
				
				public void keyTyped(KeyEvent e) {
			      if (e.getKeyChar()=='\n') {
					try {
						HVSysBus bus = getCurrentModuleBus();
						HVSysSupply hv = getCurrentHV();

						BigDecimal totalVoltage = new BigDecimal(textField.getText());
						BigDecimal pedestalVoltage = new BigDecimal(moduleSetPedestalTextField.getText());
						BigDecimal vSub = new BigDecimal(1.6);
						//BigDecimal vSub = new BigDecimal(0);
						BigDecimal voltage = totalVoltage.subtract(pedestalVoltage).add(vSub);
						setVoltage(bus, hv, id, voltage);
						//System.out.println("Set channel " + id + " to V = " + voltage.toString() + " V command queued");
						
					} catch (HVSysException e1) {
						// TODO Auto-generated catch block
						e1.printStackTrace();
					}
				 }
			   }
			   public void keyPressed(KeyEvent e) {};
			   public void keyReleased(KeyEvent e) {};
			});
			

		}
		moduleSetPedestalTextField.addKeyListener(new KeyListener(){
			 public void keyTyped(KeyEvent e) {
			 if (e.getKeyChar()=='\n') {
					try {
						HVSysBus bus = getCurrentModuleBus();
						HVSysSupply hv = getCurrentHV();
						
						int moduleId = getCurrentModuleId();
						
						BigDecimal voltage = new BigDecimal(moduleSetPedestalTextField.getText());
						Main.modulePedestalVoltage.put(moduleId, voltage);
						setPedestalVoltage(bus, hv, voltage); //correction included
						voltage = getPedestalSetVoltage(bus, hv, moduleId);
						Main.moduleCorrPedestalTextField.setText(voltage.setScale(2, RoundingMode.HALF_UP).toString());
						
						//System.out.println("Set ped command queued");
						
					} catch (HVSysException e1) {
						// TODO Auto-generated catch block
						e1.printStackTrace();
					}
  			   //System.out.println("Typed = " + moduleSetPedestalTextField.getText());
			 }
			 }
			 public void keyPressed(KeyEvent e) {};
		     public void keyReleased(KeyEvent e) {};
		     
			 });
		
		moduleSetRefTempTextField.addKeyListener(new KeyListener(){
			 public void keyTyped(KeyEvent e) {
			 if (e.getKeyChar()=='\n') {

			   BigDecimal newRefTemp = new BigDecimal(moduleSetRefTempTextField.getText());
			   moduleRefTempTextField.setText(newRefTemp.toString());
			   System.out.println("Set new reference temperature to " + newRefTemp.toString());
			   refTemperature = newRefTemp;

			 }
			 }
			 public void keyPressed(KeyEvent e) {};
		     public void keyReleased(KeyEvent e) {};
		     
			 });
		
		/*
        exitButton.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
				
				System.out.println("Exiting application..");
				System.exit(0);
				
			}
		});
        */
		
        hvOnButton.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
				try {
					HVSysBus bus = getCurrentModuleBus();
					HVSysSupply hv = getCurrentHV();

					bus.sendCommand(hv.getWriteCommand(HVSysSupply.ADDR_STATUS, HVSysSupply.POWER_ON, new HVSysCallback(){
						@Override public void onSuccess(int result) {
							System.out.println("Power ON!");
						};
					}));
					bus.waitForMessages();
					showCurrentModuleState();
					
					System.out.println("Power on command queued");
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			}
		});
        
        hvOffButton.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
				try {
					HVSysBus bus = getCurrentModuleBus();
					HVSysSupply hv = getCurrentHV();

					bus.sendCommand(hv.getWriteCommand(HVSysSupply.ADDR_STATUS, HVSysSupply.POWER_OFF, new HVSysCallback(){
						@Override public void onSuccess(int result) {
							System.out.println("Power OFF!");
						};
					}));
					bus.waitForMessages();
					showCurrentModuleState();
					
					System.out.println("Power off command queued");
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			}
		});
        
        
        
        hvLoadOneModuleButton.addActionListener(new ActionListener() {			
 			@Override public void actionPerformed(ActionEvent e) {
 				
 		      int moduleId = getCurrentModuleId();
		    		
 		      System.out.println("Update HV settings from XML file for module :  " + moduleId);
 			  try {
 					
 				   
 					HVSysBus bus = Main.getModuleBus(moduleId);
 					int hvAddress = Main.getModuleHVAddress(moduleId);
 					HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);


 						if(hv == null) {
 							System.out.println("UpdateThread: no supply");
 						} else {
 							BigDecimal pedestalVoltage = getModuleConfigFloat(moduleId, "settings/hv/pedestal");
 							//System.out.println("Load XML Config HV: moduleId = " + moduleId + ",  Ped = " + pedestalVoltage);
 							Main.setPedestalVoltage(bus, hv, pedestalVoltage); //correction included
 							
 							for(int i = 0; i < 10; i++) {								
 								BigDecimal vToSet = getModuleConfigFloat(moduleId, "settings/hv/channel[@id=" + (i+1) + "]");
 								vToSet = vToSet.subtract(pedestalVoltage);
 								Main.setVoltage(bus, hv, i, vToSet);
 							}

 						}
 						
 					 bus.waitForMessages();
 					 showCurrentModuleState();

 				
 			   } catch (Exception e3) {
 					e3.printStackTrace();
 			   }

 			}
 		});
        
        
        hvLoadButton.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
				
		    hvLoadFromXMLToModules();
		    
			}
		});
        
        hvSaveButton.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
			
				hvSaveToXML();
				
			}
		});
        
        
        hvGlobalOffButton.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
				try {
					
					System.out.println("Global Power OFF: looping over online modules " + Main.getOnlineModules());

					for(final int moduleId : Main.getOnlineModules()) {
						HVSysBus bus = Main.getModuleBus(moduleId);
						int hvAddress = Main.getModuleHVAddress(moduleId);
						//int ledAddress = Main.getModuleLEDAddress(moduleId);
						HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
						//HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);

					    bus.sendCommand(hv.getWriteCommand(HVSysSupply.ADDR_STATUS, HVSysSupply.POWER_OFF, new HVSysCallback(){
						    @Override public void onSuccess(int result) {
							    System.out.println("Power OFF!");
						    };
					    }));
					    
					    bus.waitForMessages();
					}
					
					
					System.out.println("Global Power OFF command queued");
					getModuleStates();
					showModuleStates();
					showCurrentModuleState();
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			}
		});
        
        hvGlobalOnButton.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
				try {
					
					System.out.println("Global Power ON: looping over online modules " + Main.getOnlineModules());

					for(final int moduleId : Main.getOnlineModules()) {
						HVSysBus bus = Main.getModuleBus(moduleId);
						int hvAddress = Main.getModuleHVAddress(moduleId);
						//int ledAddress = Main.getModuleLEDAddress(moduleId);
						HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
						//HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);

					    bus.sendCommand(hv.getWriteCommand(HVSysSupply.ADDR_STATUS, HVSysSupply.POWER_ON, new HVSysCallback(){
						    @Override public void onSuccess(int result) {
							    System.out.println("Power ON!");
						    };
					    }));
					    
					    bus.waitForMessages();
					}
					
					
					System.out.println("Global Power ON command queued");
					getModuleStates();
					showModuleStates();
					showCurrentModuleState();
					
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			}
		});
        
        
        ledFrequencyTextField.addKeyListener(new KeyListener() {
        	public void keyTyped(KeyEvent e) {
   			  if (e.getKeyChar()=='\n') {
		        try {
					Integer value = Integer.parseInt(ledFrequencyTextField.getText());
					HVSysBus bus;
					bus = getCurrentModuleBus();
					HVSysLED led = getCurrentLED();

					setLedFrequency(bus, led, value);
					System.out.println("LED freq command queued");
					
					Integer ledFrequency = Main.getLedFrequency(bus, led);							
					Main.ledMeasFrequencyTextField.setText(ledFrequency.toString());
					
				} catch (HVSysException e1) {
					e1.printStackTrace();
				}
			  }
        	}
        	public void keyPressed(KeyEvent e) {};
		    public void keyReleased(KeyEvent e) {};
		});
        
        ledAmplitudeTextField.addKeyListener(new KeyListener() {			
        	public void keyTyped(KeyEvent e) {
   			  if (e.getKeyChar()=='\n') {
				try {
					Integer value = Integer.parseInt(ledAmplitudeTextField.getText());
					HVSysBus bus = getCurrentModuleBus();
					HVSysLED led = getCurrentLED();

					setLedAmplitude(bus, led, value);
					System.out.println("LED set PIN ADC command queued");
					Integer ledAmplitude = Main.getLedAmplitude(bus, led);							
					Main.ledMeasAmplitudeTextField.setText(ledAmplitude.toString());
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			  }
        	}
        	public void keyPressed(KeyEvent e) {};
		    public void keyReleased(KeyEvent e) {};
		});
        
        ledSetPINADCTextField.addKeyListener(new KeyListener() {
        	public void keyTyped(KeyEvent e) {
   			  if (e.getKeyChar()=='\n') {
		        try {
					Integer value = Integer.parseInt(ledSetPINADCTextField.getText());
					HVSysBus bus;
					bus = getCurrentModuleBus();
					HVSysLED led = getCurrentLED();

					setPINADCAmplitude(bus, led, value);
					
					Integer ledPINADCAmplitude = Main.getPINADCAmplitude(bus, led);							
					Main.ledMeasPINADCTextField.setText(ledPINADCAmplitude.toString());
					
					System.out.println("LED set PIN ADC command queued");
				} catch (HVSysException e1) {
					e1.printStackTrace();
				}
			  }
        	}
        	public void keyPressed(KeyEvent e) {};
		    public void keyReleased(KeyEvent e) {};
		});
        
        ledSetAveragePointsTextField.addKeyListener(new KeyListener() {
        	public void keyTyped(KeyEvent e) {
   			  if (e.getKeyChar()=='\n') {
		        try {
					Integer value = Integer.parseInt(ledSetAveragePointsTextField.getText());
					HVSysBus bus;
					bus = getCurrentModuleBus();
					HVSysLED led = getCurrentLED();

					setPINADCAvrgPoints(bus, led, value);
					Integer ledPINADCAmplitude = Main.getPINADCAvrgPoints(bus, led);							
					Main.ledMeasAveragePointsTextField.setText(ledPINADCAmplitude.toString());
					
					System.out.println("LED set Average Points command queued");
				} catch (HVSysException e1) {
					e1.printStackTrace();
				}
			  }
        	}
        	public void keyPressed(KeyEvent e) {};
		    public void keyReleased(KeyEvent e) {};
		});
        
        setLedAutoCheckBox.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
				try {
					
					Integer value = 0;
					if (setLedAutoCheckBox.isSelected()) value = 1;
					HVSysBus bus = getCurrentModuleBus();
					HVSysLED led = getCurrentLED();

					setLedAutoMode(bus, led, value);
					
					System.out.println("LED amp command queued");
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			}
		});
        
        
        ledGlobalFrequencyTextField.addKeyListener(new KeyListener() {
        	public void keyTyped(KeyEvent e) {
   			  if (e.getKeyChar()=='\n') {
					Integer value = Integer.parseInt(ledGlobalFrequencyTextField.getText());
					ledGlobalFrequencySetTextField.setText(value.toString());
					ledGlobalFrequency = value;					
					System.out.println("LED Global Frequency is set to: " + value);

			  }
        	}
        	public void keyPressed(KeyEvent e) {};
		    public void keyReleased(KeyEvent e) {};
		});
        
        
        ledGlobalFrequencyButton.addActionListener(new ActionListener() {			
			@Override public void actionPerformed(ActionEvent e) {
				try {
					
					System.out.println("Global Power ON: looping over online modules " + Main.getOnlineModules());

					for(final int moduleId : Main.getOnlineModules()) {
						HVSysBus bus = Main.getModuleBus(moduleId);
						int ledAddress = Main.getModuleLEDAddress(moduleId);
						HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);

						setLedFrequency(bus, led, ledGlobalFrequency);
					    
					    bus.waitForMessages();
					}
					
					
					System.out.println("Global LED ON command queued");
					//getModuleStates();
					//showModuleStates();
					showCurrentModuleState();
					
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			}
		});
		
	}

	public static HVSysBus getCurrentModuleBus() throws HVSysException 
	{
		return getModuleBus(getCurrentModuleId());
	}
	
	public static HVSysBus getModuleBus(int moduleId) throws HVSysException 
	{
		int address = getModuleHVAddress(moduleId);
		
		for(HVSysBus bus: hvsysBuses) {
			if(bus.hasDevice(address)) {
				return bus;
			}
		}
		
		return null;
	}
	
	public static int getModuleHVAddress(int moduleId) throws HVSysException
	{
		return getModuleConfigInteger(moduleId, "connection/hvsys/hv/id");
	}
	
	public static int getModuleLEDAddress(int moduleId) throws HVSysException
	{
		return getModuleConfigInteger(moduleId, "connection/hvsys/led/id");
	}
	
	public static ArrayList<Integer> getModuleIDs() throws HVSysException
	{
		List<HierarchicalConfiguration> modules = config.configurationsAt("module");
		ArrayList<Integer> ids = new ArrayList<Integer>();
		// loop over all modules in config file
		for(HierarchicalConfiguration module : modules) {
			int moduleId = Integer.parseInt(module.getRootNode().getAttributes("id").get(0).getValue().toString());
			ids.add(moduleId);
		}
		/*
			if(!module.containsKey("connection/hvsys/hv/id")) continue; 
*/
		return ids;
	}
	
	public static boolean getModuleConfigBoolean(int moduleId, String key) throws HVSysException
	{
		HierarchicalConfiguration module = config.configurationAt("module[@id=" + moduleId + "]");
		
		if(!module.containsKey(key)) throw new HVSysException("Cannot find HV configuration for module " + moduleId); 
//		System.out.println("Config: moduleId = " + moduleId);
		
		return module.getBoolean(key);
	}
	
	public static void setModuleConfigInteger(int moduleId, String key, int value) throws HVSysException
	{
		HierarchicalConfiguration module = config.configurationAt("module[@id=" + moduleId + "]");
		
		if(!module.containsKey(key)) throw new HVSysException("Cannot find HV configuration for module " + moduleId);
		module.setProperty(key,value);
	}
	
	public static int getModuleConfigInteger(int moduleId, String key) throws HVSysException
	{
		HierarchicalConfiguration module = config.configurationAt("module[@id=" + moduleId + "]");
		
		if(!module.containsKey(key)) throw new HVSysException("Cannot find HV configuration for module " + moduleId); 
//		System.out.println("Config: moduleId = " + moduleId);
		
		return module.getInt(key);
	}
	
	
	public static void setModuleConfigFloat(int moduleId, String key, float value) throws HVSysException
	{
		HierarchicalConfiguration module = config.configurationAt("module[@id=" + moduleId + "]");
		
		if(!module.containsKey(key)) throw new HVSysException("Cannot find HV configuration for module " + moduleId);
		module.setProperty(key,value);
	}
	
	public static BigDecimal getModuleConfigFloat(int moduleId, String key) throws HVSysException
	{
		HierarchicalConfiguration module = config.configurationAt("module[@id=" + moduleId + "]");
		
		if(!module.containsKey(key)) throw new HVSysException("Cannot find HV configuration for module " + moduleId); 
		BigDecimal result = new BigDecimal(module.getProperty(key).toString());
		return result;
	}
	
	public static boolean isModuleOnline(int moduleId) throws HVSysException
	{
		//HierarchicalConfiguration module = config.configurationAt("module[@id=" + moduleId + "]");
		//return module.containsKey("connection/hvsys/hv/id");
		return getOnlineModules().contains(moduleId);
	}
	
	private static void createAndShowGUI() throws HVSysException {
        //Create and set up the window.
        JFrame frame = new JFrame("HelloWorldSwing");
        frame.setTitle("FHCAL NICA Slow Control");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
 
        frame.setLayout(new BorderLayout());

        //JLabel label = new JLabel("NA61 PSD slow control");        
        //frame.getContentPane().add(label, BorderLayout.NORTH);
        
        JPanel selectorPanel = CreateSelectorPanel();
        frame.getContentPane().add(selectorPanel, BorderLayout.CENTER);
        
        JPanel modulePanel = CreateModulePanel();
        frame.getContentPane().add(modulePanel, BorderLayout.EAST);
        
        JPanel globalControlPanel = CreateGlobalControlPanel();
        frame.getContentPane().add(globalControlPanel, BorderLayout.SOUTH);
        
        //Display the window.
        frame.pack();
        frame.setVisible(true);
    }
	
	private static JPanel CreateModulePanel() {
		JPanel modulePanel = new JPanel();
        modulePanel.setLayout(new GridLayout(26, 5));        
        modulePanel.setPreferredSize(new Dimension(500, 500));

        modulePanel.add(moduleHeaderLabel = new JLabel("Module 0"));
        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());

        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel("Set voltage"));
        modulePanel.add(new JLabel("Corr voltage"));
        modulePanel.add(new JLabel("Meas voltage"));
        modulePanel.add(new JLabel("Error"));
        
        moduleSetVoltageTextFields = new ArrayList<JTextField>();
        moduleCorrVoltageTextFields = new ArrayList<JTextField>();
        moduleMeasVoltageTextFields = new ArrayList<JTextField>();
        moduleErrorLabels= new ArrayList<JLabel>();
        for(int i = 0; i < 10; i++) {
        	JLabel rowLabel = new JLabel("" + (i+1));
        	rowLabel.setAlignmentX(JLabel.RIGHT_ALIGNMENT);
            modulePanel.add(rowLabel);

            JTextField vSet = new JTextField("-");
            modulePanel.add(vSet);
            moduleSetVoltageTextFields.add(vSet);
            
        	JTextField vCorr = new JTextField("-");
        	vCorr.setEditable(false);
            modulePanel.add(vCorr);
            moduleCorrVoltageTextFields.add(vCorr);
            
            JTextField vMeas = new JTextField("-");
        	vMeas.setEditable(false);
            modulePanel.add(vMeas);
            moduleMeasVoltageTextFields.add(vMeas);
            
        	JLabel error = new JLabel("");
            modulePanel.add(error);
            moduleErrorLabels.add(error);
        }

        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());

        JLabel pedestalLabel = new JLabel("Pedestal");
        pedestalLabel.setAlignmentX(JLabel.RIGHT_ALIGNMENT);
        modulePanel.add(pedestalLabel);
        modulePanel.add(moduleSetPedestalTextField =  new JTextField("-"));
        modulePanel.add(moduleCorrPedestalTextField =  new JTextField("-"));
        moduleCorrPedestalTextField.setEditable(false);
        modulePanel.add(moduleMeasPedestalTextField =  new JTextField("-"));
        modulePanel.add(modulePedestalErrorLabel =  new JLabel(""));
        moduleMeasPedestalTextField.setEditable(false);
                
        //modulePanel.add(new JLabel(""));
        hvOnButton = new JButton("HV ON");

		modulePanel.add(hvOnButton);
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));

        hvOffButton = new JButton("HV OFF");
        modulePanel.add(hvOffButton);
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        temperatureLabel = new JLabel("");
        modulePanel.add(temperatureLabel);

        modulePanel.add(new JLabel(""));
        
        hvLoadOneModuleButton = new JButton("HV LOAD");
        modulePanel.add(hvLoadOneModuleButton);
        //modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));

        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel("Ref. temperature"));
        modulePanel.add(moduleSetRefTempTextField =  new JTextField("-"));
        modulePanel.add(moduleRefTempTextField =  new JTextField("-"));
        moduleRefTempTextField.setEditable(false);

        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel("dV/dT"));
        modulePanel.add(moduleTempSlopeTextField =  new JTextField("-"));
        moduleTempSlopeTextField.setEditable(false);
        modulePanel.add(new JLabel("mV/deg"));
        
        modulePanel.add(new JSeparator());
        modulePanel.add(new JSeparator());
        modulePanel.add(new JSeparator());
        modulePanel.add(new JSeparator());
        modulePanel.add(new JSeparator());

        modulePanel.add(new JLabel("LED"));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));

        modulePanel.add(new JLabel("Frequency"));
        modulePanel.add(ledFrequencyTextField = new JTextField("loading"));
        //modulePanel.add(setLedFrequencyButton = new JButton("Set"));
        modulePanel.add(ledMeasFrequencyTextField = new JTextField("loading"));
        ledMeasFrequencyTextField.setEditable(false);
        
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel("Amplitude"));
        modulePanel.add(ledAmplitudeTextField = new JTextField("loading"));
        //modulePanel.add(setLedAmplitudeButton = new JButton("Set"));
        
        modulePanel.add(ledMeasAmplitudeTextField = new JTextField("loading"));
        ledMeasAmplitudeTextField.setEditable(false);      

        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        //modulePanel.add(new JButton("LED ON"));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));

        modulePanel.add(new JLabel(""));
        //modulePanel.add(new JButton("LED OFF"));
        modulePanel.add(new JLabel(""));
        //modulePanel.add(new JLabel(""));
        //modulePanel.add(new JLabel(""));
        
        modulePanel.add(new JLabel("PIN ADC Ampl"));
        modulePanel.add(ledSetPINADCTextField = new JTextField("loading"));
        modulePanel.add(ledMeasPINADCTextField = new JTextField("loading"));
        ledMeasPINADCTextField.setEditable(false);
        modulePanel.add(ledMeasPINADCAvrgTextField = new JTextField("loading"));
        ledMeasPINADCAvrgTextField.setEditable(false);
        
        modulePanel.add(new JLabel(""));
        
        modulePanel.add(new JLabel("Avrg. Points"));
        modulePanel.add(ledSetAveragePointsTextField = new JTextField("loading"));
        modulePanel.add(ledMeasAveragePointsTextField = new JTextField("loading"));
        ledMeasAveragePointsTextField.setEditable(false);
        //modulePanel.add(new JLabel(""));
        modulePanel.add(setLedAutoCheckBox = new JCheckBox("Auto"));
        
        return modulePanel;
	}

	protected static HVSysSupply getCurrentHV() throws HVSysException {
		return (HVSysSupply) getCurrentModuleBus().getDevice(getModuleHVAddress(getCurrentModuleId()));
	}

	protected static HVSysLED getCurrentLED() throws HVSysException {
		return (HVSysLED) getCurrentModuleBus().getDevice(getModuleLEDAddress(getCurrentModuleId()));
	}

	private static JPanel CreateSelectorPanel() throws HVSysException {
		JPanel selectorPanel = new JPanel();
		moduleButtons = new HashMap<Integer, JButton>(); 
		selectorPanel.setPreferredSize(new Dimension(500, 500));
		selectorPanel.setMaximumSize(new Dimension(500, 500));
		selectorPanel.setMinimumSize(new Dimension(500, 500));
        selectorPanel.setLayout(new GridBagLayout()); // TODO GridBagLayout
        System.out.println("Module IDs in config: " + getModuleIDs());
        for(int i : getModuleIDs()) {
        	GridBagConstraints c = new GridBagConstraints();
        	c.gridx = (i-1)%4;
        	c.gridy = (i-1)/4;
        	c.fill = GridBagConstraints.BOTH;
        	//boolean test = config.containsKey("module[@id=16]/connection/hvsys/hv/id");
        	if(config.containsKey("module[@id=" + i + "]/geometry/x")) {
        		c.gridx = config.getInt("module[@id=" + i + "]/geometry/x");
        		c.gridy = config.getInt("module[@id=" + i + "]/geometry/y");
        		c.gridheight = config.getInt("module[@id=" + i + "]/geometry/size");
        		c.gridwidth = config.getInt("module[@id=" + i + "]/geometry/size");
        		c.weightx = config.getInt("module[@id=" + i + "]/geometry/size");
        		c.weighty = config.getInt("module[@id=" + i + "]/geometry/size");
        	}
        	JButton moduleButton = new JButton("" + i);
        	moduleButtons.put(i, moduleButton);        	
        	moduleButton.addActionListener(new ActionListener() {				
				@Override
				public void actionPerformed(ActionEvent e) {
					setSelectedModule(Integer.parseInt(e.getActionCommand()));
				}
			});
        	selectorPanel.add(moduleButton, c);
        }
		return selectorPanel;
	}
	
	private static JPanel CreateGlobalControlPanel() throws HVSysException {
		JPanel globalControlPanel = new JPanel();
		
		globalControlPanel.setLayout(new GridLayout(7, 4)); 
		
		globalControlPanel.setPreferredSize(new Dimension(500, 150));
		globalControlPanel.setMaximumSize(new Dimension(500, 150));
		globalControlPanel.setMinimumSize(new Dimension(500, 150));

		globalControlPanel.add(new JSeparator());
		globalControlPanel.add(new JSeparator());
		globalControlPanel.add(new JSeparator());
		globalControlPanel.add(new JSeparator());

        
		globalControlPanel.add(new JLabel("Global control"));
		ledGlobalFrequencyLabel = new JLabel("Global LED frequency  ");
		ledGlobalFrequencyLabel.setHorizontalAlignment(JLabel.RIGHT);
		globalControlPanel.add(ledGlobalFrequencyLabel);
		ledGlobalFrequencyTextField = new JTextField("0");
		globalControlPanel.add(ledGlobalFrequencyTextField);
		ledGlobalFrequencySetTextField = new JTextField("0");
		ledGlobalFrequencySetTextField.setEditable(false);
		globalControlPanel.add(ledGlobalFrequencySetTextField);
		ledGlobalFrequency = 0;
        
		hvGlobalOnButton = new JButton("Global HV ON");
		globalControlPanel.add(hvGlobalOnButton);
		globalControlPanel.add(new JLabel(""));
		globalControlPanel.add(new JLabel(""));
		ledGlobalFrequencyButton = new JButton("Global LED Frequency Set");
		globalControlPanel.add(ledGlobalFrequencyButton);
		        
		
        hvGlobalOffButton = new JButton("Global HV OFF");
		globalControlPanel.add(hvGlobalOffButton);
		globalControlPanel.add(new JLabel(""));
		globalControlPanel.add(new JLabel(""));
		globalControlPanel.add(new JLabel(""));
		
        
		globalControlPanel.add(new JLabel(""));
        globalControlPanel.add(new JLabel(""));
        globalControlPanel.add(new JLabel(""));
        //globalControlPanel.add(new JLabel(""));
		activateVoiceCheckCheckBox = new JCheckBox("  Activate voice notifications       ");
		activateVoiceCheckCheckBox.setHorizontalAlignment(JCheckBox.LEFT);
		globalControlPanel.add(activateVoiceCheckCheckBox);
		
		if (useVoiceNotifications == 1) activateVoiceCheckCheckBox.setSelected(true);
		else activateVoiceCheckCheckBox.setSelected(false);
        
        
        globalControlPanel.add(new JLabel(""));
		hvLoadButton = new JButton("XML Config LOAD");
        globalControlPanel.add(hvLoadButton);
        globalControlPanel.add(new JLabel(""));
        //globalControlPanel.add(new JLabel(""));
        activateHVMonitorCheckBox = new JCheckBox("  Activate HV monitor       ");
		activateHVMonitorCheckBox.setHorizontalAlignment(JCheckBox.LEFT);
		globalControlPanel.add(activateHVMonitorCheckBox);
		
		if (monitorHV == 1) activateHVMonitorCheckBox.setSelected(true);
		else activateHVMonitorCheckBox.setSelected(false);
		
		
        
        globalControlPanel.add(new JLabel(""));
        hvSaveButton = new JButton("XML Config SAVE");
        globalControlPanel.add(hvSaveButton);
        
        //exitButton = new JButton("Close and exit");
        //exitButton.setBackground(Color.RED);
        //exitButton.setForeground(Color.WHITE);
        //globalControlPanel.add(exitButton);
        //globalControlPanel.add(new JLabel(""));
        
        globalControlPanel.add(new JLabel("   Last update has been done at:"));
        //globalControlPanel.add(new JLabel(""));
        globalControlPanel.add(timeOfLastScanTextField = new JTextField("loading"));
        timeOfLastScanTextField.setEditable(false);
        
		
		return globalControlPanel;
		
	}

	protected static void setSelectedModule(int moduleId) {
		setCurrentModuleId(moduleId);
		moduleHeaderLabel.setText("Module " + moduleId);
		clearModuleDisplay();
    	showCurrentModuleState();
		//showModuleStates();
	}


	private static void clearModuleDisplay() {
		try{
			Main.moduleSetPedestalTextField.setText("loading");
			Main.moduleCorrPedestalTextField.setText("loading");
			Main.moduleMeasPedestalTextField.setText("loading");
			Main.moduleSetRefTempTextField.setText("loading");
			Main.moduleRefTempTextField.setText("loading");
			Main.moduleTempSlopeTextField.setText("loading");
			
			for(int i = 0; i < 10; i++) {
				Main.moduleSetVoltageTextFields.get(i).setText("loading");
				Main.moduleCorrVoltageTextFields.get(i).setText("loading");
				Main.moduleMeasVoltageTextFields.get(i).setText("loading");
			}

			Main.temperatureLabel.setText("loading");

			Main.ledFrequencyTextField.setText("loading");
			Main.ledAmplitudeTextField.setText("loading");

		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	protected static void startListeningThread() {
		listeningThread = new ListeningThread(config);
		System.out.println("Starting listening thread");
		new Thread(listeningThread).start();
	}

	
	protected static void loadConfiguration() {
		hvsysBuses = new ArrayList<HVSysBus>();
		busNames = new HashMap<String, HVSysBus>();
		moduleIds = new ArrayList<Integer>();
		
		config = new XMLConfiguration();
		config.setFileName("PsdSlowControlConfig.xml");
//		config.setSchemaValidation(true); // TODO cannot validate xsd
		config.setExpressionEngine(new XPathExpressionEngine()); 
		
		/*
		configToDCS = new XMLConfiguration();
		configToDCS.setFileName("slowControlToDCS.xml");
//		config.setSchemaValidation(true); // TODO cannot validate xsd
		configToDCS.setExpressionEngine(new XPathExpressionEngine()); 
		*/
		
		try {
			config.load();
			//configToDCS.load();

			HierarchicalConfiguration global = config.configurationAt("global");
			List<HierarchicalConfiguration> modules = config.configurationsAt("module");
			
			//verbose = getIntegerFromConfig(module, global, "connection/hvsys/led/id");
			verbose = Main.getConfig().getInt("global/flags/verbose", 1);
			useVoiceNotifications = Main.getConfig().getInt("global/flags/useVoiceNotifications", 1);
			voiceServer = Main.getConfig().getString("global/flags/voiceServer");
			monitorHV = Main.getConfig().getInt("global/flags/monitorHV");
			refTemperature = new BigDecimal(global.getProperty("flags/refTemp").toString());
			tempSlope = new BigDecimal(global.getProperty("flags/tempSlope").toString());
			
			
			// loop over all modules in config file
			for(HierarchicalConfiguration module : modules) {
				int moduleId = Integer.parseInt(module.getRootNode().getAttributes("id").get(0).getValue().toString());
				
				if(!isModuleOnline(moduleId)) continue; 

				
				/*
				HierarchicalConfiguration moduleToDCS = Main.configToDCS.configurationAt("module[@id=" + moduleId + "]");
				if(!isModuleOnline(moduleId)) {
				  moduleToDCS.setProperty("isOnline",0);
				  continue; 
				}
				moduleToDCS.setProperty("isOnline",1);
				*/
				
				System.out.println("Config: moduleId = " + moduleId);
				
				moduleIds.add(moduleId);
				final String portName = getStringFromConfig(module, global, "connection/hvsys/port");
				System.out.println("Config: port = " + portName);

				// creating buses only once
				if(!busNames.containsKey(portName)) {
					HVSysBus bus = new HVSysBus(portName);
					hvsysBuses.add(bus);
					busNames.put(portName, bus);
				}
				HVSysBus bus = busNames.get(portName);
				
				
				final int ledAddress = getIntegerFromConfig(module, global, "connection/hvsys/led/id");
				HVSysLED led = (HVSysLED) bus.addDevice(DeviceType.LED_SOURCE, ledAddress);
				bus.sendCommand(led.getReadCommand(HVSysLED.ADDR_CELL_ID, new HVSysCallback() {
					@Override
					public void onSuccess(int result) {
						if(result == HVSysLED.CELL_ID) { 
							if (Main.verbose == 1) System.out.println("LED ok! Port = " + portName + " address = " + ledAddress);
						} else { 
							if (Main.verbose == 1) System.out.println("LED bad! Port = " + portName + " address = " + ledAddress);
						} 
					}
					@Override
					public void onFail(int result) {
						if (Main.verbose == 1) System.out.println("LED failed to respond! Port = " + portName + " address = " + ledAddress);
					}
				}));
				bus.waitForMessages();
				
				final int supplyAddress = getIntegerFromConfig(module, global, "connection/hvsys/hv/id");
				supply = (HVSysSupply) bus.addDevice(DeviceType.HV_SUPPLY, supplyAddress);
				bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_CELL_ID, new HVSysCallback() {
					@Override
					public void onSuccess(int result) {
						if(result == HVSysSupply.CELL_ID) { 
							if (Main.verbose == 1) System.out.println("Supply ok! Port = " + portName + " address = " + supplyAddress);
						} else { 
							if (Main.verbose == 1) System.out.println("Supply bad! Port = " + portName + " address = " + supplyAddress);
						} 
					}
					@Override
					public void onFail(int result) {
						if (Main.verbose == 1) System.out.println("Supply failed to respond! Port = " + portName + " address = " + ledAddress);
					}
				}));								
				bus.waitForMessages();
				
				//System.out.println("supplyAddress = " + supplyAddress);
				//System.out.println("supply.getDeviceId() = " + supply.getDeviceId());
				//System.out.println("HVSysSupply.CELL_ID = " + HVSysSupply.CELL_ID);
				
				if (supply.getDeviceId() == HVSysSupply.CELL_ID ) {
					if (supply.PED_CALIB_MIN == 0 ) {
						  bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_PEDESTAL_VOLTAGE_CALIBRATION_MIN, new HVSysCallback() {
							  @Override public void onSuccess(int result) {
								  calibration = result;
							  }
						  }));	
						  bus.waitForMessages();
						  
						  supply.PED_CALIB_MIN = calibration;
				    }
					
					if (supply.PED_CALIB_MAX == 0 ) {
						  bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_PEDESTAL_VOLTAGE_CALIBRATION_MAX, new HVSysCallback() {
							  @Override public void onSuccess(int result) {
								  calibration = result;
							  }
						  }));	
						  bus.waitForMessages();
						  
						  supply.PED_CALIB_MAX = calibration;
				    }
					
					
					if (supply.CHAN_CALIB == 0) {
						  bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_VOLTAGE_CALIBRATION, new HVSysCallback() {
							  @Override public void onSuccess(int result) {
								  calibration = result;
							  }
						  }));	
						  bus.waitForMessages();
						  
						  supply.CHAN_CALIB = calibration;
				    }
				}
			}
			
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			try {
				for(HVSysBus bus : hvsysBuses) {
					bus.closePort();
				}
			} catch(Exception e){
				e.printStackTrace();
			}finally {
				
			}
		}
	}
	
	
    public static void hvLoadFromXMLToModules() {			
		
    	System.out.println("Update HV and LED settings from XML file");
		  try {
				
			
			for(final int moduleId : Main.getOnlineModules()) {
				HVSysBus bus = Main.getModuleBus(moduleId);
				int hvAddress = Main.getModuleHVAddress(moduleId);
				int ledAddress = Main.getModuleLEDAddress(moduleId);
				HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
				HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);
				
				System.out.println("Load XML Config HV: moduleId = " + moduleId);

					if(hv == null) {
						System.out.println("UpdateThread: no supply");
					} else {
						BigDecimal pedestalVoltage = getModuleConfigFloat(moduleId, "settings/hv/pedestal");
						Main.modulePedestalVoltage.put(moduleId, pedestalVoltage);
						Main.setPedestalVoltage(bus, hv, pedestalVoltage); //correction included
						
						for(int i = 0; i < 10; i++) {								
							BigDecimal vToSet = getModuleConfigFloat(moduleId, "settings/hv/channel[@id=" + (i+1) + "]");
							vToSet = vToSet.subtract(pedestalVoltage);
							Main.setVoltage(bus, hv, i, vToSet);
						}

					}
					
				 bus.waitForMessages();
				 
				 System.out.println("Load XML Config LED: moduleId = " + moduleId);

					if(led == null) {
						System.out.println("UpdateThread: no supply");
					} else {

						int ledAutoTune = getModuleConfigInteger(moduleId, "settings/led/autoTune");
						Main.setLedAutoMode(bus, led, ledAutoTune);
						
						int ledBrightness = getModuleConfigInteger(moduleId, "settings/led/brightness");
						Main.setLedAmplitude(bus, led, ledBrightness);
						
						int ledFrequency = getModuleConfigInteger(moduleId, "settings/led/frequency");
						Main.setLedFrequency(bus, led, ledFrequency);
						
						int ledPinADCSet = getModuleConfigInteger(moduleId, "settings/led/pinADCSet");
						Main.setPINADCAmplitude(bus, led, ledPinADCSet);

					}
					
				 bus.waitForMessages();
				
			} // for(final int moduleId : Main.getOnlineModules())
			
		   } catch (Exception e3) {
				e3.printStackTrace();
		   }
    
    	
	}

    
public static void hvSaveToXML() {			
		
    	System.out.println("Save HV and LED settings to XML file");
	    
		  try {
				
			
			for(final int moduleId : Main.getOnlineModules()) {
				HVSysBus bus = Main.getModuleBus(moduleId);
				int hvAddress = Main.getModuleHVAddress(moduleId);
				int ledAddress = Main.getModuleLEDAddress(moduleId);
				HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
				HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);
				
				System.out.println("UpdateThread: moduleId = " + moduleId);

					if(hv == null) {
						System.out.println("UpdateThread: no supply");
					} else {
						ArrayList<BigDecimal> voltages = Main.getSetVoltages(bus, hv, moduleId);
						BigDecimal pedestalVoltage = Main.getPedestalSetVoltage(bus, hv, moduleId);
						
						for(int i = 0; i < 10; i++) {
							BigDecimal v = voltages.get(i).add(pedestalVoltage);
							//System.out.println("Module = " + moduleId + " Section = " + (i+1) + " V = " + v);
							setModuleConfigFloat(moduleId, "settings/hv/pedestal", pedestalVoltage.floatValue());
							setModuleConfigFloat(moduleId, "settings/hv/channel[@id=" + (i+1) + "]", v.floatValue());
						}

					}
					
				 bus.waitForMessages();

					if(led == null) {
						System.out.println("UpdateThread: no supply");
					} else {

						setModuleConfigInteger(moduleId, "settings/led/autoTune", getLedAutoMode(bus, led));
		    			setModuleConfigInteger(moduleId, "settings/led/brightness", getLedAmplitude(bus, led));
						setModuleConfigInteger(moduleId, "settings/led/frequency", getLedFrequency(bus, led));
						setModuleConfigInteger(moduleId, "settings/led/pinADCSet", getPINADCAmplitude(bus, led));

					}
					
				 bus.waitForMessages();
				
			} // for(final int moduleId : Main.getOnlineModules())
			
		   } catch (Exception e3) {
				e3.printStackTrace();
		   }
				
				try {
				  config.save("PsdSlowControlConfig_new.xml");
				
				} catch (Exception e1) {
					e1.printStackTrace();
				}


	}

	public static ArrayList<BigDecimal> getSetVoltages(HVSysBus bus, HVSysSupply supply, int moduleId) throws HVSysException {
		System.out.println("getSetVoltages called for moduleId = " + moduleId);
		final ArrayList<Integer> readings = new ArrayList<Integer>();
		ArrayList<BigDecimal> result = new ArrayList<BigDecimal>();
		
		//System.out.println("The bus is clear (?)");
		for(int i = 0; i < 10; i++) {
			try {
				//System.out.println("getSetVoltages try Chan = " + i);
				bus.sendCommand(supply.getReadCommand(HVSysSupply.AddrSetVoltage(i), new HVSysCallback() {
					@Override public void onSuccess(int r) {
						//System.out.println("onSuccess in getSetVoltages returns: " + r);
						readings.add(r);
					}
				}));
				
			} catch (Exception e) {
				System.out.println("getMeasVoltages WARNING!!! Chan = " + i);
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		bus.waitForMessages();
		
		calibration = supply.CHAN_CALIB;
		
		if (Main.verbose == 1) System.out.println("(getSetVoltages) supply.CHAN_CALIB = " + calibration);
		if (Main.verbose == 1) System.out.println("(getSetVoltages) readings = " + readings);
		
		for(int i = 0; i < 10; i++) {
			BigDecimal d = new BigDecimal((readings.get(i)/4095.0)*(calibration/100.0) - 1.6);
			result.add(d.setScale(2, RoundingMode.HALF_UP));
			
			//System.out.println("ch" + (i+1) + ": " + readings.get(i) + " / calib = " + calibration);
		}

		//System.exit(0);
		return result;
	}

	public static ArrayList<BigDecimal> getMeasVoltages(HVSysBus bus, HVSysSupply supply, int moduleId) throws HVSysException {
		System.out.println("getMeasVoltages is called for moduleId = " + moduleId);
		final ArrayList<Integer> readings = new ArrayList<Integer>();
		ArrayList<BigDecimal> result = new ArrayList<BigDecimal>();
		
		//System.out.println("The bus is clear (?)");
		for(int i = 0; i < 10; i++) {
			try {
				//System.out.println("getMeasVoltages try Chan = " + i + " Addr =" + HVSysSupply.AddrMeasVoltage(i));
				bus.sendCommand(supply.getReadCommand(HVSysSupply.AddrMeasVoltage(i), new HVSysCallback() {
					@Override public void onSuccess(int r) {
						//System.out.println("onSuccess in getMeasVoltages returns: " + r);
						readings.add(r);
					}
				}));
				
				
			} catch (Exception e) {
				System.out.println("getMeasVoltages WARNING!!! Chan = " + i);
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		bus.waitForMessages();
		
		calibration = supply.CHAN_CALIB;
		
		System.out.println("(getMeasVoltages) supply.CHAN_CALIB = " + calibration);
		System.out.println("(getMeasVoltages) readings = " + readings);
		
		for(int i = 0; i < 10; i++) {
			BigDecimal d = new BigDecimal((readings.get(i)/4095.0)*(calibration/100.0) - 1.6);
			result.add(d.setScale(2, RoundingMode.HALF_UP));
			
			//System.out.println("ch" + (i+1) + ": " + readings.get(i) + " / calib = " + calibration);
		}

		//System.exit(0);
		return result;
	}

	
	private static int pedestalCalibrationMin = 0;
	private static int pedestalCalibrationMax = 0;
	private static int reading = 0;
	
	private static int readingPedSet = 0;
	private static int readingPedMeas = 0;

	private static int calibration = 0;
	//private static ArrayList<Integer> readings;

	public static int getValue(HVSysBus bus, HVSysUnit unit, int moduleId, int subAddress) throws HVSysException {
		
		bus.sendCommand(unit.getReadCommand(subAddress, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				reading = result;
			}
		}));	
		bus.waitForMessages();

		return reading;
	}
	
	public static BigDecimal getPedestalMeasVoltage(HVSysBus bus, HVSysSupply supply, int moduleId) throws HVSysException {
		System.out.println("getPedestalMeasVoltage is called for moduleId = " + moduleId);
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_MEAS_PEDESTAL_VOLTAGE, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				readingPedMeas = result;
			}
		}));
		bus.waitForMessages();
		
		pedestalCalibrationMin = supply.PED_CALIB_MIN;
		pedestalCalibrationMax = supply.PED_CALIB_MAX;
			
		BigDecimal d = new BigDecimal(0);
		//d = new BigDecimal((readingPedMeas/4095.0)*((pedestalCalibrationMax - pedestalCalibrationMin)/100.0 + 1.6) + pedestalCalibrationMin/100.0);
		d = new BigDecimal((readingPedMeas/4095.0)*((pedestalCalibrationMax - pedestalCalibrationMin)/100.0) + pedestalCalibrationMin/100.0 - 1.6);
		
		if (Main.verbose == 1) System.out.println("Get pedMeas v, calibration = " + pedestalCalibrationMin + ", " + pedestalCalibrationMax
				          + ", reading = " + readingPedMeas + ", voltage = " + d.setScale(2, RoundingMode.HALF_UP));
		//System.out.println("Get ped v, reading = " + reading);
		//System.out.println("Get ped v, voltage = " + d.toString());

		return d.setScale(2, RoundingMode.HALF_UP);
	}

	public static BigDecimal getPedestalSetVoltage(HVSysBus bus, HVSysSupply supply, int moduleId) throws HVSysException {
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_SET_PEDESTAL_VOLTAGE, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				readingPedSet = result;
			}
		}));
		bus.waitForMessages();
		
		pedestalCalibrationMin = supply.PED_CALIB_MIN;
		pedestalCalibrationMax = supply.PED_CALIB_MAX;
			
		BigDecimal d = new BigDecimal(0);
		d = new BigDecimal((readingPedSet/4095.0)*((pedestalCalibrationMax - pedestalCalibrationMin)/100.0) + pedestalCalibrationMin/100.0 - 1.6);
		
		if (Main.verbose == 1) System.out.println("Get pedSet v, calibration = " + pedestalCalibrationMin + ", " + pedestalCalibrationMax
		          + ", reading = " + readingPedSet + ", voltage = " + d.setScale(2, RoundingMode.HALF_UP));
		//System.out.println("Get ped v, calibration = " + pedestalCalibration);
		//System.out.println("Get ped v, reading = " + reading);
		//System.out.println("Get ped v, voltage = " + d.toString());

		return d.setScale(2, RoundingMode.HALF_UP);
	}

	public static void setPedestalVoltage(HVSysBus bus, HVSysSupply supply, BigDecimal voltage) throws HVSysException {
		
		// get temperature register
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_TEMPERATURE, new HVSysCallback() {
			@Override public void onSuccess(int result) {
				//Main.temperatureLabel.setText("T = " + result + "(" + (-0.019*result+63.9) + ")");
				BigDecimal temperature = new BigDecimal(63.9-0.019*result);
				Main.temperatureLabel.setText("T = " + temperature.setScale(2, RoundingMode.HALF_UP));
				Main.moduleTemperature = temperature;
			}
		}));
		
		bus.waitForMessages();
		
        BigDecimal d2 = new BigDecimal(1000.);
		BigDecimal pedestalCorrection = moduleTemperature.subtract(refTemperature).multiply(tempSlope).divide(d2);
		
		System.out.println("Temperature correction = " + pedestalCorrection.setScale(2, RoundingMode.HALF_UP).toString());
		
		voltage = voltage.add(pedestalCorrection);
		
		pedestalCalibrationMin = supply.PED_CALIB_MIN;
		pedestalCalibrationMax = supply.PED_CALIB_MAX;
		
		int setV = (int) Math.round((voltage.doubleValue() - pedestalCalibrationMin/100.0 + 1.6) / ((pedestalCalibrationMax - pedestalCalibrationMin)/100.0) * 4095.0);		
		
		if (Main.verbose == 1) {
		  System.out.print("Preparing set ped v");
		  System.out.print(", calibration = " + pedestalCalibrationMin + ", " + pedestalCalibrationMax);
		  System.out.print(", voltage = " + voltage.setScale(2, RoundingMode.HALF_UP).toString());
		  System.out.println(", set = " + setV);
		}
		bus.sendCommand(supply.getWriteCommand(HVSysSupply.ADDR_SET_PEDESTAL_VOLTAGE, setV, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				System.out.println("Completed set ped v");
			}
		}));
		bus.waitForMessages();
	}

	public static void setVoltage(HVSysBus bus, HVSysSupply supply, int moduleId, BigDecimal voltage) throws HVSysException {
		
		calibration = supply.CHAN_CALIB;
		
		double voltsToset = voltage.doubleValue();
		if (voltsToset < -1.6) voltsToset = -1.6;
		if (voltsToset > 1.6) voltsToset = 1.6;
		
		voltsToset = 1.6 - voltsToset;
			
		int setV = (int) Math.round( voltsToset / (calibration/100.0) * 4095.0);

		if (Main.verbose == 1) {
	      System.out.print("Preparing set v, calibration = " + calibration);
		  System.out.print(", voltage = " + voltage.toString());
		  System.out.println(", set = " + setV);
		}
		try {
			bus.sendCommand(supply.getWriteCommand(HVSysSupply.AddrSetVoltage(moduleId), setV, new HVSysCallback() {
				@Override
				public void onSuccess(int result) {
					if (Main.verbose == 1) System.out.println("Completed set v");
				}
			}));
			bus.waitForMessages();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private static int ledFreqReading;
	public static int getLedFrequency(HVSysBus bus, HVSysLED led) throws HVSysException {
		
		bus.sendCommand(led.getReadCommand(HVSysLED.ADDR_FREQ, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledFreqReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledFreqReading;
	}

	public static int setLedFrequency(HVSysBus bus, HVSysLED led, int value) throws HVSysException {
		
		bus.sendCommand(led.getWriteCommand(HVSysLED.ADDR_FREQ, value, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
			}
		}));		
		bus.waitForMessages();
		return ledFreqReading;
	}
	
	public static int getLedAmplitude(HVSysBus bus, HVSysLED led) throws HVSysException {
		
		bus.sendCommand(led.getReadCommand(HVSysLED.ADDR_DAC_VALUE, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledAmpReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledAmpReading;
	}

	public static int setLedAmplitude(HVSysBus bus, HVSysLED led, int value) throws HVSysException {
		
		bus.sendCommand(led.getWriteCommand(HVSysLED.ADDR_DAC_VALUE, value, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledAmpReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledAmpReading;
	}

	public static int setPINADCAmplitude(HVSysBus bus, HVSysLED led, int value) throws HVSysException {
		
		bus.sendCommand(led.getWriteCommand(HVSysLED.ADDR_ADC_SET_POINT, value, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledPINADCReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledPINADCReading;
	}

	public static int getPINADCAmplitude(HVSysBus bus, HVSysLED led) throws HVSysException {
		
		bus.sendCommand(led.getReadCommand(HVSysLED.ADDR_ADC_SET_POINT, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledPINADCReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledPINADCReading;
	}

	
	public static int setPINADCAvrgPoints(HVSysBus bus, HVSysLED led, int value) throws HVSysException {
		
		bus.sendCommand(led.getWriteCommand(HVSysLED.ADDR_AVERAGE_POINTS, value, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledAvrgPointsReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledAvrgPointsReading;
	}

	public static int getPINADCAvrgPoints(HVSysBus bus, HVSysLED led) throws HVSysException {
		
		bus.sendCommand(led.getReadCommand(HVSysLED.ADDR_AVERAGE_POINTS, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledAvrgPointsReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledAvrgPointsReading;
	}
	
	public static int getPINADCAvrgAmplitude(HVSysBus bus, HVSysLED led) throws HVSysException {
		
		bus.sendCommand(led.getReadCommand(HVSysLED.ADDR_AVERAGE_ADC, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledPINADCAvrgReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledPINADCAvrgReading;
	}
	public static int setLedAutoMode(HVSysBus bus, HVSysLED led, int value) throws HVSysException {
		
		bus.sendCommand(led.getWriteCommand(HVSysLED.ADDR_AUTOREG, value, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledAmpReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledAmpReading;
	}

	public static int getLedAutoMode(HVSysBus bus, HVSysLED led) throws HVSysException {

		bus.sendCommand(led.getReadCommand(HVSysLED.ADDR_AUTOREG, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				ledAutoModeReading = result;
			}
		}));		
		bus.waitForMessages();
		return ledAutoModeReading;
	}
	public static int getIntegerFromConfig(HierarchicalConfiguration node,
			HierarchicalConfiguration defaultNode, String key) throws ConfigurationException {
		
		if(node.containsKey(key)) return node.getInt(key);
		if(defaultNode.containsKey(key)) return defaultNode.getInt(key);
		
		throw new ConfigurationException("Configuration key " + key + " not found.");
	}

	public static String getStringFromConfig(HierarchicalConfiguration node,
			HierarchicalConfiguration defaultNode, String key) throws ConfigurationException {
		
		if(node.containsKey(key)) return node.getString(key);
		if(defaultNode.containsKey(key)) return defaultNode.getString(key);
		
		throw new ConfigurationException("Configuration key " + key + " not found.");
	}

	public static void loadModuleStates() {
		moduleStates = new HashMap<Integer, Main.ModuleState>();
		moduleErrorCounters = new HashMap<Integer, Integer>();
		modulePedestalVoltage = new HashMap<Integer, BigDecimal>();
		// loop over all modules in config file		
		try {
			List<Integer> all = getModuleIDs();
			List<Integer> online = getOnlineModules();
			
			BigDecimal bigDecimalZero = new BigDecimal(0);

			for(int moduleId : all) {
				moduleStates.put(moduleId, ModuleState.Offline);
				moduleErrorCounters.put(moduleId,0);
				modulePedestalVoltage.put(moduleId, bigDecimalZero);
			}
			for(int moduleId : online) {
				moduleStates.put(moduleId, ModuleState.PowerOff);
			}
			
		} catch (HVSysException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
	}

public static void getModuleStates() {	
	
	for(final int moduleId : Main.getOnlineModules()) {
		
	  if(Main.moduleStates.get(moduleId) ==  Main.ModuleState.Offline) continue;
		
	  try {
		
		HVSysBus bus = Main.getModuleBus(moduleId);
		int hvAddress = Main.getModuleHVAddress(moduleId);
		//int ledAddress = Main.getModuleLEDAddress(moduleId);
		HVSysSupply hv = (HVSysSupply) bus.getDevice(hvAddress);
		//HVSysLED led = (HVSysLED) bus.getDevice(ledAddress);
		
		if (Main.verbose == 1) System.out.println("UpdateThread: moduleId = " + moduleId);
		if(hv == null) {
			  System.out.println("UpdateThread: no supply");
		} else {
			// get status register
			bus.sendCommand(hv.getReadCommand(HVSysSupply.ADDR_STATUS, new HVSysCallback() {
				@Override public void onSuccess(int result) {
					Main.setModuleState(moduleId, result, 0);
					Main.statusRegisterToLog = result;
				}
			}));    	
		}
		
	  }
      catch (Exception e) {
		e.printStackTrace();
      }
	} //for(final int moduleId : Main.getOnlineModules()) {
}
			
	public static void showModuleStates() {
		for(Entry<Integer, ModuleState> entry : moduleStates.entrySet()) {
			int id = entry.getKey();
			ModuleState state = entry.getValue();
			JButton button = moduleButtons.get(id);
			if(button == null) {
				System.out.println("No button" + id);
			} else {
				button.setEnabled(state != ModuleState.Offline);
				button.setBackground(getModuleColor(state));
				button.setBorderPainted(getCurrentModuleId() != id);
			}
		}
	}

	private static Color getModuleColor(ModuleState state) {
		//if(isActive) {
			switch(state) {
			case Offline:
				return Color.GRAY;
			case Error:
				return Color.RED;
			case PowerOff:
				return Color.YELLOW;
			case PowerOn:
				return Color.GREEN;
			case NotReference:
				return Color.MAGENTA;
			}
		/*} else {
			switch(state) {
			case Offline:
				return Color.GRAY;
			case Error:
				return Color.RED;
			case PowerOff:
				return new Color(128,128,128);
			case PowerOn:
				return Color.GREEN;
			}
		}*/
		return null;
	}
	
	public static void setModuleState(int moduleId, ModuleState state) {
		Main.moduleStates.put(moduleId, state);
		showModuleStates();
	}
	
	public static ModuleState getModuleState(int moduleId) {
		return Main.moduleStates.get(moduleId);
	}

	public static void setModuleState(int moduleId, int hvStatusRegister, int showChannels) {
		
		int  errorMask = 65532;
		
		try {
			errorMask = getModuleConfigInteger(moduleId, "settings/hv/errorMask");
		} catch (HVSysException e) {
			// TODO Auto-generated catch block
			//e.printStackTrace();
			if (Main.verbose == 1) System.out.println("No errorMask found for module: " + moduleId);
			
		}
		
		ModuleState state = ModuleState.PowerOff;
		if((hvStatusRegister & 0x01) != 0) {
			state = ModuleState.PowerOn;
			if( (hvStatusRegister & 0x02) != 0) {
				if ((hvStatusRegister & errorMask) != 0 )
				state = ModuleState.Error;
			}
		}
		if (showChannels == 1) {
		  for(int ch = 0; ch < 10; ch++) {
			  int offset = ch + 5;
			  if( (hvStatusRegister & (1 << offset)) != 0 ) {
				  moduleErrorLabels.get(ch).setText("ERROR:" + hvStatusRegister);
			  } else{
				  moduleErrorLabels.get(ch).setText("");
			  }  
		  }
		}
		Main.setModuleState(moduleId, state);
	}

	public static List<Integer> getOnlineModules() {
		String[] list = config.getStringArray("global/flags/onlineModules");
		List<Integer> result = new ArrayList<Integer>();
		for(String s : list) {
			result.add(Integer.parseInt(s));
		}
		return result;
	}

	public static int getCurrentModuleId() {
		return currentModuleId;
	}

	public static void setCurrentModuleId(int currentModuleId) {
		Main.currentModuleId = currentModuleId;
	}
	
	public static void voiceAlarm(String what) {
		  //String host = "na61pc006";
		  if (Main.verbose == 1) System.out.println("Connecting to voice server: " + voiceServer);
		  int port = 1314;
		  try {
		   Socket socket = new Socket(voiceServer, port);
		   DataOutputStream stream = new DataOutputStream(socket.getOutputStream());
		   stream.writeBytes("(SayText \""+ what +"\")");
		   socket.close();
		  } catch (UnknownHostException e) {
		   e.printStackTrace();
		  } catch (IOException e) {
		   e.printStackTrace();
		  }
    }
}
