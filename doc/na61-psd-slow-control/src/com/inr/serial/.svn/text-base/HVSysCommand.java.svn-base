package com.inr.serial;

public class HVSysCommand implements Comparable<HVSysCommand>
{
	public enum CommandType {
		READ_BYTE,
		READ_SHORT,
		WRITE_SHORT
	}
	
	public int cellAddress;		// to find a HVSysUnit
	public int registerAddress;	
	public CommandType commandType;
	public int value; 		// e.g. "w05040000\n" or "1"
	public int priority;  		// less is better
	
	public int response;
	
	private HVSysCallback callback;
	
	@Override
	public int compareTo(HVSysCommand o) {
		Integer p = priority;
		return p.compareTo(o.priority);
	}
	
	public HVSysCommand(int _cellAddress, int _registerAddress, CommandType _commandType, int _value, int _priority, HVSysCallback _callback)
	{
		cellAddress = _cellAddress;
		registerAddress = _registerAddress;
		commandType = _commandType;
		value = _value;
		priority = _priority;
		callback = _callback;
		
		response = 0;
	}
	
	public String getCommandText() throws HVSysException {
		switch(commandType) {
		case READ_BYTE: 
			return String.format("<%02x%02x_\n", cellAddress, registerAddress);
		case READ_SHORT: 
			return String.format("r%02x%02x_\n", cellAddress, registerAddress);
		case WRITE_SHORT: 
			return String.format("w%02x%02x%04x_\n", cellAddress, registerAddress, value);
		default:
			throw new HVSysException("Bad command type");
		}
		
	}
	
	public void onSuccess(int result) {
		if(null != callback) callback.onSuccess(result);
	}

	public void onFail(int result) {
		if(null != callback) callback.onFail(result);
	}
}
