package com.inr.slowcontrol;

import java.net.URL;
import java.io.File;

import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.HierarchicalConfiguration;
import org.apache.commons.configuration.XMLConfiguration;

public class PrettyXMLConfiguration extends XMLConfiguration {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	public PrettyXMLConfiguration() {
		super();
	}

	public PrettyXMLConfiguration(HierarchicalConfiguration c) {
		super(c);
	}

	public PrettyXMLConfiguration(String fileName)
			throws ConfigurationException {
		super(fileName);
	}

	public PrettyXMLConfiguration(File file) throws ConfigurationException {
		//throws ConfigurationException {
	
		super(file);
	}

	public PrettyXMLConfiguration(URL url) throws ConfigurationException  {
		super(url);
	}

    @Override
    protected Transformer createTransformer() throws TransformerException {
        Transformer transformer = super.createTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.setOutputProperty("{http://xml.apache.org/xslt}indent-amount", "4");
        return transformer;
    }
}
