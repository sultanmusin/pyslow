package com.inr.slowcontrol.gui;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSeparator;
import javax.swing.JTextField;

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
		Error
	};
	
	private static Map<Integer, ModuleState> moduleStates;
	private static Map<Integer, JButton> moduleButtons;
	
	private static List<HVSysBus> hvsysBuses;
	private static Map<String, HVSysBus> busNames;
	private static XMLConfiguration config;
	public static XMLConfiguration getConfig() {
		return config;
	}

	private static ArrayList<Integer> moduleIds;
	private static JLabel moduleHeaderLabel;
	private static ArrayList<JTextField> moduleSetVoltageTextFields;
	public static ArrayList<JTextField> moduleMeasVoltageTextFields;
	private static ArrayList<JLabel> moduleErrorLabels;
	private static JTextField moduleSetPedestalTextField;
	public static JTextField moduleMeasPedestalTextField;
	public static JLabel modulePedestalErrorLabel;
	public static JTextField ledFrequencyTextField;
	public static JTextField ledAmplitudeTextField;
	private static int currentModuleId;
	
	private static ListeningThread listeningThread;
	
	private static HVSysSupply supply;
	public static JLabel temperatureLabel;

	public static void main(String[] args) {
		javax.swing.SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                try {
                	loadConfiguration();
	            	loadModuleStates();

	            	createAndShowGUI();
	            	clearModuleDisplay();

	            	setSelectedModule(getOnlineModules().get(0));
	            	showModuleStates();
	            	showCurrentModuleState();
	            	
	            	addGuiListeners();
	            	
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
				BigDecimal pedestalSetVoltage = Main.getPedestalSetVoltage(bus, hv, moduleId);
				BigDecimal pedestalMeasVoltage = Main.getPedestalMeasVoltage(bus, hv, moduleId);
				
				Main.moduleSetPedestalTextField.setText(pedestalSetVoltage.toString());
				Main.moduleMeasPedestalTextField.setText(pedestalMeasVoltage.toString());
				
				for(int i = 0; i < 10; i++) {
					BigDecimal v = setVoltages.get(i).add(pedestalMeasVoltage);
					//System.out.println("Module = " + moduleId + " Section = " + (i+1) + " V = " + v);
					Main.moduleSetVoltageTextFields.get(i).setText(v.toString());
				}

				for(int i = 0; i < 10; i++) {
					BigDecimal v = measVoltages.get(i).add(pedestalMeasVoltage);
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
						Main.temperatureLabel.setText("T = " + result + "(" + (-0.019*result+63.9) + ")");
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


		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	protected static void addGuiListeners() {
		for(int i = 0; i < 10; i++) {
			final JTextField textField = moduleSetVoltageTextFields.get(i);
			final int id = i;
			textField.addFocusListener(new FocusListener() {
				
				@Override public void focusLost(FocusEvent arg0) {
					try {
						HVSysBus bus = getCurrentModuleBus();
						HVSysSupply hv = getCurrentHV();

						BigDecimal totalVoltage = new BigDecimal(textField.getText());
						BigDecimal pedestalVoltage = new BigDecimal(moduleSetPedestalTextField.getText());
						BigDecimal voltage = totalVoltage.subtract(pedestalVoltage);
						setVoltage(bus, hv, id, voltage);
						System.out.println("Set channel V command queued");
						
					} catch (HVSysException e1) {
						// TODO Auto-generated catch block
						e1.printStackTrace();
					}
				}
				
				@Override public void focusGained(FocusEvent arg0) {}
			});


		}
		
		moduleSetPedestalTextField.addFocusListener(new FocusListener() {
			
			@Override public void focusLost(FocusEvent arg0) {
				try {
					HVSysBus bus = getCurrentModuleBus();
					HVSysSupply hv = getCurrentHV();

					BigDecimal voltage = new BigDecimal(moduleSetPedestalTextField.getText());
					setPedestalVoltage(bus, hv, voltage);
					System.out.println("Set ped command queued");
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
			
			@Override public void focusGained(FocusEvent arg0) {}
		});

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
					
					System.out.println("Power off command queued");
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			}
		});
        ledFrequencyTextField.addFocusListener(new FocusListener() {			
			@Override public void focusLost(FocusEvent arg0) {
				try {
					Integer value = Integer.parseInt(ledFrequencyTextField.getText());
					HVSysBus bus;
					bus = getCurrentModuleBus();
					HVSysLED led = getCurrentLED();

					setLedFrequency(bus, led, value);
					
					System.out.println("LED freq command queued");
				} catch (HVSysException e) {
					e.printStackTrace();
				}
			}
			
			@Override
			public void focusGained(FocusEvent arg0) {}
		});

        ledAmplitudeTextField.addFocusListener(new FocusListener() {			
			@Override public void focusLost(FocusEvent arg0) {
				try {
					Integer value = Integer.parseInt(ledAmplitudeTextField.getText());
					HVSysBus bus = getCurrentModuleBus();
					HVSysLED led = getCurrentLED();

					setLedAmplitude(bus, led, value);
					
					System.out.println("LED amp command queued");
					
				} catch (HVSysException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				//bus.sendCommand(hv.get);
			}

			@Override
			public void focusGained(FocusEvent e) {	}
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
	
	public static int getModuleConfigInteger(int moduleId, String key) throws HVSysException
	{
		HierarchicalConfiguration module = config.configurationAt("module[@id=" + moduleId + "]");
		
		if(!module.containsKey(key)) throw new HVSysException("Cannot find HV configuration for module " + moduleId); 
//		System.out.println("Config: moduleId = " + moduleId);
		
		return module.getInt(key);
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
        frame.setTitle("NA61 PSD Slow Control");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
 
        frame.setLayout(new BorderLayout());

        //JLabel label = new JLabel("NA61 PSD slow control");        
        //frame.getContentPane().add(label, BorderLayout.NORTH);
        
        JPanel selectorPanel = CreateSelectorPanel();
        frame.getContentPane().add(selectorPanel, BorderLayout.CENTER);
        
        JPanel modulePanel = CreateModulePanel();
        frame.getContentPane().add(modulePanel, BorderLayout.EAST);
        
        //Display the window.
        frame.pack();
        frame.setVisible(true);
    }
	
	private static JPanel CreateModulePanel() {
		JPanel modulePanel = new JPanel();
        modulePanel.setLayout(new GridLayout(23, 4));        
        modulePanel.setPreferredSize(new Dimension(400, 500));

        modulePanel.add(moduleHeaderLabel = new JLabel("Module 0"));
        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel());

        modulePanel.add(new JLabel());
        modulePanel.add(new JLabel("Set voltage"));
        modulePanel.add(new JLabel("Meas voltage"));
        modulePanel.add(new JLabel("Error"));
        
        moduleSetVoltageTextFields = new ArrayList<JTextField>();
        moduleMeasVoltageTextFields = new ArrayList<JTextField>();
        moduleErrorLabels= new ArrayList<JLabel>();
        for(int i = 0; i < 10; i++) {
        	JLabel rowLabel = new JLabel("" + (i+1));
        	rowLabel.setAlignmentX(JLabel.RIGHT_ALIGNMENT);
            modulePanel.add(rowLabel);

            JTextField vSet = new JTextField("-");
            modulePanel.add(vSet);
            moduleSetVoltageTextFields.add(vSet);
            
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

        JLabel pedestalLabel = new JLabel("Pedestal");
        pedestalLabel.setAlignmentX(JLabel.RIGHT_ALIGNMENT);
        modulePanel.add(pedestalLabel);
        modulePanel.add(moduleSetPedestalTextField =  new JTextField("-"));
        modulePanel.add(moduleMeasPedestalTextField =  new JTextField("-"));
        modulePanel.add(modulePedestalErrorLabel =  new JLabel(""));
        moduleMeasPedestalTextField.setEditable(false);
                
        hvOnButton = new JButton("HV ON");

		modulePanel.add(hvOnButton);
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));

        hvOffButton = new JButton("HV OFF");
        modulePanel.add(hvOffButton);
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        temperatureLabel = new JLabel("");
        modulePanel.add(temperatureLabel);

        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));

        modulePanel.add(new JSeparator());
        modulePanel.add(new JSeparator());
        modulePanel.add(new JSeparator());
        modulePanel.add(new JSeparator());

        modulePanel.add(new JLabel("LED"));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));

        modulePanel.add(new JLabel("Frequency"));
        modulePanel.add(ledFrequencyTextField = new JTextField("10"));
        modulePanel.add(new JButton("Set"));
        modulePanel.add(new JLabel(""));
        

        JButton setLedAmplitudeButton = new JButton("Set");
        modulePanel.add(new JLabel("Amplitude"));
        modulePanel.add(ledAmplitudeTextField = new JTextField("100"));
        modulePanel.add(setLedAmplitudeButton);
        modulePanel.add(new JLabel(""));       
        

        modulePanel.add(new JButton("LED ON"));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));

        modulePanel.add(new JButton("LED OFF"));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));
        modulePanel.add(new JLabel(""));


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

	protected static void setSelectedModule(int moduleId) {
		setCurrentModuleId(moduleId);
		moduleHeaderLabel.setText("Module " + moduleId);
		clearModuleDisplay();
    	showCurrentModuleState();
		showModuleStates();
	}


	private static void clearModuleDisplay() {
		try{
			Main.moduleSetPedestalTextField.setText("loading");
			Main.moduleMeasPedestalTextField.setText("loading");
			
			for(int i = 0; i < 10; i++) {
				Main.moduleSetVoltageTextFields.get(i).setText("loading");
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
		
		
		try {
			config.load();

			HierarchicalConfiguration global = config.configurationAt("global");
			List<HierarchicalConfiguration> modules = config.configurationsAt("module");
			
			// loop over all modules in config file
			for(HierarchicalConfiguration module : modules) {
				int moduleId = Integer.parseInt(module.getRootNode().getAttributes("id").get(0).getValue().toString());
				
				if(!isModuleOnline(moduleId)) continue; 
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
							System.out.println("LED ok! Port = " + portName + " address = " + ledAddress);
						} else { 
							System.out.println("LED bad! Port = " + portName + " address = " + ledAddress);
						} 
					}
					@Override
					public void onFail(int result) {
						System.out.println("LED failed to respond! Port = " + portName + " address = " + ledAddress);
					}
				}));
				
				final int supplyAddress = getIntegerFromConfig(module, global, "connection/hvsys/hv/id");
				supply = (HVSysSupply) bus.addDevice(DeviceType.HV_SUPPLY, supplyAddress);
				bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_CELL_ID, new HVSysCallback() {
					@Override
					public void onSuccess(int result) {
						if(result == HVSysSupply.CELL_ID) { 
							System.out.println("Supply ok! Port = " + portName + " address = " + supplyAddress);
						} else { 
							System.out.println("Supply bad! Port = " + portName + " address = " + supplyAddress);
						} 
					}
					@Override
					public void onFail(int result) {
						System.out.println("Supply failed to respond! Port = " + portName + " address = " + ledAddress);
					}
				}));
								
				bus.waitForMessages();
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

	public static ArrayList<BigDecimal> getSetVoltages(HVSysBus bus, HVSysSupply supply, int moduleId) throws HVSysException {
		System.out.println("getSetVoltages");
		readings = new ArrayList<Integer>();
		ArrayList<BigDecimal> result = new ArrayList<BigDecimal>();
		
		for(int i = 0; i < 10; i++) {
			try {
				bus.sendCommand(supply.getReadCommand(HVSysSupply.AddrSetVoltage(i), new HVSysCallback() {
					@Override public void onSuccess(int result) {
						readings.add(result);
					}
				}));
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_VOLTAGE_CALIBRATION, new HVSysCallback() {
			@Override public void onSuccess(int result) {
				calibration = result;
			}
		}));
				
		bus.waitForMessages();

		for(int i = 0; i < 10; i++) {
			BigDecimal d = new BigDecimal((readings.get(i)/4095.0)*(calibration/100.0));
			result.add(d.setScale(2, RoundingMode.HALF_UP));
			
			System.out.println("ch" + (i+1) + ": " + readings.get(i) + " / calib = " + calibration);
		}

		//System.exit(0);
		return result;
	}

	public static ArrayList<BigDecimal> getMeasVoltages(HVSysBus bus, HVSysSupply supply, int moduleId) throws HVSysException {
		System.out.println("getMeasVoltages");
		readings = new ArrayList<Integer>();
		ArrayList<BigDecimal> result = new ArrayList<BigDecimal>();
		
		for(int i = 0; i < 10; i++) {
			try {
				bus.sendCommand(supply.getReadCommand(HVSysSupply.AddrMeasVoltage(i), new HVSysCallback() {
					@Override public void onSuccess(int result) {
						readings.add(result);
					}
				}));
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_VOLTAGE_CALIBRATION, new HVSysCallback() {
			@Override public void onSuccess(int result) {
				calibration = result;
			}
		}));
				
		bus.waitForMessages();

		for(int i = 0; i < 10; i++) {
			BigDecimal d = new BigDecimal((readings.get(i)/4095.0)*(calibration/100.0));
			result.add(d.setScale(2, RoundingMode.HALF_UP));
			
			System.out.println("ch" + (i+1) + ": " + readings.get(i) + " / calib = " + calibration);
		}

		//System.exit(0);
		return result;
	}

	private static int pedestalCalibration = 0;
	private static int reading = 0;

	private static int calibration = 0;
	private static ArrayList<Integer> readings;

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
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_MEAS_PEDESTAL_VOLTAGE, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				reading = result;
			}
		}));
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_PEDESTAL_VOLTAGE_CALIBRATION, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				pedestalCalibration = result;
			}
		}));
				
		bus.waitForMessages();

		BigDecimal d = new BigDecimal(0);
		d = new BigDecimal((reading/4095.0)*(pedestalCalibration/100.0));

		System.out.println("Get ped v, calibration = " + pedestalCalibration);
		System.out.println("Get ped v, reading = " + reading);
		System.out.println("Get ped v, voltage = " + d.toString());

		return d.setScale(2, RoundingMode.HALF_UP);
	}

	public static BigDecimal getPedestalSetVoltage(HVSysBus bus, HVSysSupply supply, int moduleId) throws HVSysException {
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_SET_PEDESTAL_VOLTAGE, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				reading = result;
			}
		}));
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_PEDESTAL_VOLTAGE_CALIBRATION, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				pedestalCalibration = result;
			}
		}));
				
		bus.waitForMessages();

		BigDecimal d = new BigDecimal(0);
		d = new BigDecimal((reading/4095.0)*(pedestalCalibration/100.0));

		System.out.println("Get ped v, calibration = " + pedestalCalibration);
		System.out.println("Get ped v, reading = " + reading);
		System.out.println("Get ped v, voltage = " + d.toString());

		return d.setScale(2, RoundingMode.HALF_UP);
	}

	public static void setPedestalVoltage(HVSysBus bus, HVSysSupply supply, BigDecimal voltage) throws HVSysException {
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_PEDESTAL_VOLTAGE_CALIBRATION, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				pedestalCalibration = result;
			}
		}));
				
		bus.waitForMessages();

		
		int setV = (int) Math.round(voltage.doubleValue() / (pedestalCalibration/100.0) * 4095.0);

		System.out.println("Preparing set ped v, calibration = " + pedestalCalibration);
		System.out.println("Preparing set ped v, voltage = " + voltage.toString());
		System.out.println("Preparing set ped v, set = " + setV);

		bus.sendCommand(supply.getWriteCommand(HVSysSupply.ADDR_SET_PEDESTAL_VOLTAGE, setV, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				System.out.println("Completed set ped v");
			}
		}));
		bus.waitForMessages();
	}

	public static void setVoltage(HVSysBus bus, HVSysSupply supply, int moduleId, BigDecimal voltage) throws HVSysException {
		
		bus.sendCommand(supply.getReadCommand(HVSysSupply.ADDR_VOLTAGE_CALIBRATION, new HVSysCallback() {
			@Override
			public void onSuccess(int result) {
				calibration = result;
			}
		}));
				
		bus.waitForMessages();
		
		int setV = (int) Math.round(voltage.doubleValue() / (calibration/100.0) * 4095.0);

		System.out.println("Preparing set v, calibration = " + calibration);
		System.out.println("Preparing set v, voltage = " + voltage.toString());
		System.out.println("Preparing set v, set = " + setV);

		try {
			bus.sendCommand(supply.getWriteCommand(HVSysSupply.AddrSetVoltage(moduleId), setV, new HVSysCallback() {
				@Override
				public void onSuccess(int result) {
					System.out.println("Completed set v");
				}
			}));
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		bus.waitForMessages();
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

	private static int ledAmpReading;
	private static JButton hvOnButton;
	private static JButton hvOffButton;
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
		// loop over all modules in config file		
		try {
			List<Integer> all = getModuleIDs();
			List<Integer> online = getOnlineModules();

			for(int moduleId : all) {
				moduleStates.put(moduleId, ModuleState.Offline);
			}
			for(int moduleId : online) {
				moduleStates.put(moduleId, ModuleState.PowerOff);
			}
			
		} catch (HVSysException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
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

	public static void setModuleState(int moduleId, int hvStatusRegister) {
		ModuleState state = ModuleState.PowerOff;
		if((hvStatusRegister & 0x01) != 0) {
			state = ModuleState.PowerOn;
			if((hvStatusRegister & 0x02) != 0) 
				state = ModuleState.Error;
		}
		for(int ch = 0; ch < 10; ch++) {
			int offset = ch + 3;
			if( (hvStatusRegister & (1 << offset)) != 0 ) {
				moduleErrorLabels.get(ch).setText("ERROR");
			} else{
				moduleErrorLabels.get(ch).setText("");
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
}
