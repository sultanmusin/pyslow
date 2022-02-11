#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from __future__ import annotations   # For neat recursive type hints

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"

import bisect
import logging
import sys
sys.path.append('.')
sys.path.append('lib/hvsys')
from message import Message

class HVsysWall:

    CELL_ID = 0x8013

    DESCRIPTION = "HV Supply 16 (ScintWall)"

    MAX_CHANNEL_COUNT = 16

    PEDESTAL_VOLTAGE_BIAS = 1.6         # volts. Set real ped V this much HIGHER so the per-channel voltage settings can tune both ways up and down. Set to zero for 800c boards.
    PEDESTAL_RESOLUTION = 4096        # counts
    VOLTAGE_RESOLUTION = 4096         # counts
    VOLTAGE_DECIMAL_PLACES = 2        # to 0.01 V

    POWER_OFF = 0
    POWER_ON = 1

    capabilities = {
        "CELL_ID": 0x00,         
        "STATUS": 0x02,               # status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
        "1/SET_VOLTAGE": 0x04,
        "2/SET_VOLTAGE": 0x06,
        "3/SET_VOLTAGE": 0x08,
        "4/SET_VOLTAGE": 0x0a,
        "5/SET_VOLTAGE": 0x0c,
        "6/SET_VOLTAGE": 0x0e,
        "7/SET_VOLTAGE": 0x10,
        "8/SET_VOLTAGE": 0x12,
        "9/SET_VOLTAGE": 0x14,
        "10/SET_VOLTAGE": 0x16,
        "11/SET_VOLTAGE": 0x18,
        "12/SET_VOLTAGE": 0x1a,
        "13/SET_VOLTAGE": 0x1c,
        "14/SET_VOLTAGE": 0x1e,
        "15/SET_VOLTAGE": 0x20,
        "16/SET_VOLTAGE": 0x22,
        "SET_PEDESTAL_VOLTAGE": 0x24,
        "RAMP_TIME": 0x26,
        "TEMPERATURE": 0x28,
        "CHECK_CRC": 0x2a,
        "MEAS_PEDESTAL_VOLTAGE": 0x4e,
        "VOLTAGE_CALIBRATION": 0x50,           # Calibration value of channels Voltage in 10mV units, i.e. to get Volts one need Vmax/100.
        "PEDESTAL_VOLTAGE_CALIBRATION_MAX": 0x52,   # Calibration value of MAX pedestal Voltage in 10mV units, i.e. to get Volts one need PedVmax/100
        "PEDESTAL_VOLTAGE_CALIBRATION_MIN": 0x54,   # Calibration value of MAX pedestal Voltage in 10mV units, i.e. to get Volts one need PedVmax/100
        "VERSION_DATE_LOW": 0x56,              # Response = 8212 (0x2014)
        "VERSION_DATE_HIGH": 0x58,             # Response = 5121 (0x1401)
        "FAULTY_CHANNELS": 0x5a,
        "CELL_ADDRESS": 0x5c
    }

    capabilities_by_subaddress = {val: key for key, val in capabilities.items()}

    # poll these first so the voltages can be translated to string using the calibrations
    priority_capabilities = [
        "TEMPERATURE",
        "PEDESTAL_VOLTAGE_CALIBRATION_MAX", 
        "PEDESTAL_VOLTAGE_CALIBRATION_MIN", 
        "SET_PEDESTAL_VOLTAGE",
        "MEAS_PEDESTAL_VOLTAGE",
        "VOLTAGE_CALIBRATION"
    ]


    volatile = [
        "STATUS",
        "TEMPERATURE",
        "RAMP_STATUS",
    ]


    def __init__(self, config):
        self.config = config
        self.state = {}
        for cap in HVsysWall.capabilities:
            self.state[cap] = None

        self.state['REF_PEDESTAL_VOLTAGE'] = self.config.hv_pedestal
        for ch in range(1,self.config.n_channels+1):
            self.state[f"{ch}/REF_VOLTAGE"] = self.config.hv[str(ch)]
        
        if hasattr(config, 'temperature_sensor'):
            self.temperature_sensor = config.temperature_sensor
        else:
            self.temperature_sensor = self

    # set another module (can be any object with state['TEMPERATURE'] property) as the source for this module temp correction
    def set_temperature_sensor(self, temperature_sensor):
        self.temperature_sensor = temperature_sensor

    def reference_voltage_caps(self):
        return [f"{ch}/REF_VOLTAGE" for ch in range(1, self.config.n_channels+1)] + ['REF_PEDESTAL_VOLTAGE']


    def updateState(self, cap, value):
        self.state[cap] = value # TODO checks 

    def pedestalVoltsToCounts(self, volts: str) -> int:                       # also can accept float value
        volts_to_set = float(volts) + HVsysWall.PEDESTAL_VOLTAGE_BIAS       # Set real ped V this much HIGHER so the per-channel voltage settings can tune both ways up and down
                                                                              # May be DANGEROUS to set ped V before per-channel V with HV ON
        calib_ped_high = self.state["PEDESTAL_VOLTAGE_CALIBRATION_MAX"] / 100.0     # 6248 -> 62.48 V
        calib_ped_low = self.state["PEDESTAL_VOLTAGE_CALIBRATION_MIN"] / 100.0      # 4953 -> 49.53 V

        if volts_to_set < calib_ped_low:
            print("HVsysWall: trying to set invalid voltage, %2.2f < %2.2f (lower bound), setting lower bound"%(volts_to_set, calib_ped_low))
            volts_to_set = calib_ped_low

        # we can set values more than higher calibration so I comment out this check.
        # this_is_ok.jpg

        #if volts_to_set > calib_ped_high:
        #    print("HVsysWall: trying to set invalid voltage, %2.2f > %2.2f (upper bound), setting upper bound"%(volts_to_set, calib_ped_high))
        #    volts_to_set = calib_ped_high

        return int((HVsysWall.PEDESTAL_RESOLUTION - 1) * (volts_to_set - calib_ped_low) / (calib_ped_high - calib_ped_low))


    def pedestalCountsToVolts(self, counts: int) -> float:
        if counts < 0: # or counts >= HVsysWall.PEDESTAL_RESOLUTION:
            raise ValueError("HVsysWall: invalid pedestal counts %d >= PEDESTAL_RESOLUTION"%(counts))

        calib_ped_high = self.state["PEDESTAL_VOLTAGE_CALIBRATION_MAX"] / 100.0     # 5270 -> 52.70 V
        calib_ped_low = self.state["PEDESTAL_VOLTAGE_CALIBRATION_MIN"] / 100.0      # 3180 -> 31.80 V

        volts = calib_ped_low + counts * (calib_ped_high - calib_ped_low) / (HVsysWall.PEDESTAL_RESOLUTION - 1) - HVsysWall.PEDESTAL_VOLTAGE_BIAS
        return round(volts, HVsysWall.VOLTAGE_DECIMAL_PLACES)

    def voltsToCounts(self, volts: str) -> int:
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysWall: cannot translate volts to counts without knowing VOLTAGE_CALIBRATION")
        if "REF_PEDESTAL_VOLTAGE" not in self.state or self.state["REF_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysWall: cannot translate volts to counts without knowing REF_PEDESTAL_VOLTAGE")
        pedestal_voltage = float(self.state["REF_PEDESTAL_VOLTAGE"])
        volts_to_set = pedestal_voltage + HVsysWall.PEDESTAL_VOLTAGE_BIAS - float(volts)  # e.g. -0.5V means we need to go 0.5V lower than pedestal (with positive counts)       

        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 

        if volts_to_set < 0:
            logging.warning(f"HVsysWall id={self.config.id}: trying to set invalid voltage, {volts_to_set} < 0 (lower bound), setting lower bound")
            volts_to_set = 0

        if volts_to_set > calib_voltage_slope:
            print(f"HVsysWall id={self.config.id}: trying to set invalid voltage, {volts_to_set} > {calib_voltage_slope} (upper bound), setting upper bound")
            volts_to_set = calib_voltage_slope

        return int((HVsysWall.VOLTAGE_RESOLUTION - 1) * volts_to_set / calib_voltage_slope)

    def measVoltsToCounts(self, volts: str) -> int:
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysWall: cannot translate volts to counts without knowing VOLTAGE_CALIBRATION")
        if "MEAS_PEDESTAL_VOLTAGE" not in self.state or self.state["MEAS_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysWall: cannot translate volts to counts without knowing MEAS_PEDESTAL_VOLTAGE")
        pedestal_voltage = self.pedestalCountsToVolts(self.state["MEAS_PEDESTAL_VOLTAGE"])
        volts_to_set = -(float(volts) - pedestal_voltage - HVsysWall.PEDESTAL_VOLTAGE_BIAS)  # e.g. -0.5V means we need to go 0.5V lower than pedestal (with positive counts)       
        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 

        if volts_to_set < 0:
            print("HVsysWall: trying to set invalid voltage, %2.2f < %2.2f (lower bound), setting lower bound"%(volts_to_set, 0))
            volts_to_set = 0

        if volts_to_set > calib_voltage_slope:
            print("HVsysWall: trying to set invalid voltage, %2.2f > %2.2f (upper bound), setting upper bound"%(volts_to_set, calib_voltage_slope))
            volts_to_set = calib_voltage_slope

        return int((HVsysWall.VOLTAGE_RESOLUTION - 1) * volts_to_set / calib_voltage_slope)

    def countsToVolts(self, counts: int) -> str:
        if counts < 0 or counts >= HVsysWall.VOLTAGE_RESOLUTION:
            raise ValueError("HVsysWall: invalid voltage counts %d >= VOLTAGE_RESOLUTION"%(counts))
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysWall: cannot translate counts to volts without knowing VOLTAGE_CALIBRATION")
        if "SET_PEDESTAL_VOLTAGE" not in self.state or self.state["SET_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysWall: cannot translate counts to volts without knowing SET_PEDESTAL_VOLTAGE")

        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 
        pedestal_voltage = self.pedestalCountsToVolts(self.state["SET_PEDESTAL_VOLTAGE"])

        tmp = float( self.valueToString('TEMPERATURE', self.temperature_sensor.state['TEMPERATURE']) )
        tmp_corr = -(tmp - self.config.reference_temperature) * self.config.temperature_slope / 1000 # minus for normal termerature correction, e.g. config value 60 means "-60mV/C"

        volts = pedestal_voltage - counts * calib_voltage_slope / (HVsysWall.VOLTAGE_RESOLUTION - 1) + HVsysWall.PEDESTAL_VOLTAGE_BIAS + tmp_corr
        return round(volts, HVsysWall.VOLTAGE_DECIMAL_PLACES)

    def measCountsToVolts(self, counts: int) -> str:
        if counts < 0 or counts >= HVsysWall.VOLTAGE_RESOLUTION:
            raise ValueError("HVsysWall: invalid voltage counts %d >= VOLTAGE_RESOLUTION"%(counts))
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysWall: cannot translate counts to volts without knowing VOLTAGE_CALIBRATION")
        if "SET_PEDESTAL_VOLTAGE" not in self.state or self.state["MEAS_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysWall: cannot translate counts to volts without knowing MEAS_PEDESTAL_VOLTAGE")

        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 
        pedestal_voltage = self.pedestalCountsToVolts(self.state["MEAS_PEDESTAL_VOLTAGE"])

        volts = pedestal_voltage - counts * calib_voltage_slope / (HVsysWall.VOLTAGE_RESOLUTION - 1) + HVsysWall.PEDESTAL_VOLTAGE_BIAS
        return round(volts, HVsysWall.VOLTAGE_DECIMAL_PLACES)

    def tempCountsToDegrees(self, counts: int) -> float:
        if self.config.temperature_from_module == 'FAKE':
            return self.config.reference_temperature - 1
        else:
            return round(63.9-0.019*counts, HVsysWall.VOLTAGE_DECIMAL_PLACES)

    """ 
    Table calculations for ERTJ1VV104J : NTC Thermistor 
    See table https://industrial.panasonic.com/cdbs/www-data/pdf2/AUA0000/AUA0000AE276.pdf
    ADC counts to resistance (kOhms): Rt = adcv * 100 / (4096 - adcv)
    Difference between old method and this one:
    ADC counts / old / this
    1500, 35.4, 36.84
    1550, 34.45, 35.79
    1600, 33.5, 34.75
    1650, 32.55, 33.72
    1700, 31.6, 32.71
    1750, 30.65, 31.72
    1800, 29.7, 30.74
    1850, 28.75, 29.77
    1900, 27.8, 28.81
    1950, 26.85, 27.85
    2000, 25.9, 26.91
    2050, 24.95, 25.96
    2100, 24.0, 25.04
    2150, 23.05, 24.09
    2200, 22.1, 23.17
    2250, 21.15, 22.25
    2300, 20.2, 21.33
    2350, 19.25, 20.4
    2400, 18.3, 19.47
    2450, 17.35, 18.54
    """
    def tempCountsToDegreesPanasonic(self, counts: int) -> float:
        if self.config.temperature_from_module == 'FAKE':
            return self.config.reference_temperature - 1

        r = counts * 100 / (4096 - counts)
        r_from_0_to_125 = [405.0, 381.5, 359.6, 339.0, 319.7, 301.5, 284.5, 268.5, 253.5, 239.4, 226.2, 213.8, 202.1, 191.1, 180.7, 171.0, 161.8, 153.2, 145.1, 137.5, 130.3, 123.5, 117.1, 111.0, 105.4, 100.0, 94.94, 90.16, 85.64, 81.38, 77.34, 73.53, 69.92, 66.51, 63.28, 60.23, 57.33, 54.59, 52.00, 49.54, 47.21, 44.99, 42.90, 40.91, 39.02, 37.23, 35.53, 33.91, 32.38, 30.92, 29.54, 28.22, 26.97, 25.77, 24.64, 23.56, 22.53, 21.55, 20.62, 19.73, 18.89, 18.08, 17.32, 16.59, 15.89, 15.23, 14.60, 14.00, 13.43, 12.88, 12.36, 11.86, 11.39, 10.94, 10.50, 10.09, 9.696, 9.319, 8.959, 8.614, 8.284, 7.968, 7.666, 7.377, 7.099, 6.834, 6.579, 6.335, 6.101, 5.877, 5.662, 5.456, 5.258, 5.068, 4.886, 4.712, 4.544, 4.383, 4.229, 4.081, 3.939, 3.802, 3.671, 3.545, 3.425, 3.308, 3.197, 3.089, 2.986, 2.887, 2.791, 2.699, 2.610, 2.525, 2.443, 2.364, 2.287, 2.214, 2.143, 2.075, 2.009, 1.945, 1.884, 1.825, 1.768, 1.712]
        neg_map = [-x for x in r_from_0_to_125]
        position = bisect.bisect(neg_map, -r)
        if position == 0:
            return (405 - r) / (405-381)    # winter is coming
        elif position == len(r_from_0_to_125):
            return 125                      # the roof the roof
        else:
            low = r_from_0_to_125[position-1]
            high = r_from_0_to_125[position]
            return round(position + (r - low) / (high - low), HVsysWall.VOLTAGE_DECIMAL_PLACES)


    def tempDegreesToCounts(self, degrees: float) -> int:
        # we'll probably never need setting the temperature...
        return int((63.9-degrees)/0.019)


    def voltage_correction(self): 
        if "TEMPERATURE" not in self.temperature_sensor.state or self.temperature_sensor.state["TEMPERATURE"] is None: 
            raise ValueError(f"HVsysWall id={self.config.id} addr={self.config.address('hv')}: cannot calculate correction without knowing TEMPERATURE (sensor id={self.temperature_sensor.config.id} addr={self.temperature_sensor.config.address('hv')})")
        tmp = self.tempCountsToDegrees(self.temperature_sensor.state['TEMPERATURE'])
        tmp_corr = (tmp - self.config.reference_temperature) * self.config.temperature_slope / 1000 # minus for normal termerature correction, e.g. config value 60 means "-60mV/C"

        #logging.debug(round(tmp_corr, HVsysWall.VOLTAGE_DECIMAL_PLACES))
        return round(tmp_corr, HVsysWall.VOLTAGE_DECIMAL_PLACES)

    convertorsFromString = {
        "TEMPERATURE": tempDegreesToCounts,
        "1/REF_VOLTAGE": voltsToCounts,
        "2/REF_VOLTAGE": voltsToCounts,
        "3/REF_VOLTAGE": voltsToCounts,
        "4/REF_VOLTAGE": voltsToCounts,
        "5/REF_VOLTAGE": voltsToCounts,
        "6/REF_VOLTAGE": voltsToCounts,
        "7/REF_VOLTAGE": voltsToCounts,
        "8/REF_VOLTAGE": voltsToCounts,
        "9/REF_VOLTAGE": voltsToCounts,
        "10/REF_VOLTAGE": voltsToCounts,
        "11/REF_VOLTAGE": voltsToCounts,
        "12/REF_VOLTAGE": voltsToCounts,
        "13/REF_VOLTAGE": voltsToCounts,
        "14/REF_VOLTAGE": voltsToCounts,
        "15/REF_VOLTAGE": voltsToCounts,
        "16/REF_VOLTAGE": voltsToCounts,
        "REF_PEDESTAL_VOLTAGE": pedestalVoltsToCounts,
        "1/SET_VOLTAGE": voltsToCounts,
        "2/SET_VOLTAGE": voltsToCounts,
        "3/SET_VOLTAGE": voltsToCounts,
        "4/SET_VOLTAGE": voltsToCounts,
        "5/SET_VOLTAGE": voltsToCounts,
        "6/SET_VOLTAGE": voltsToCounts,
        "7/SET_VOLTAGE": voltsToCounts,
        "8/SET_VOLTAGE": voltsToCounts,
        "9/SET_VOLTAGE": voltsToCounts,
        "10/SET_VOLTAGE": voltsToCounts,
        "11/SET_VOLTAGE": voltsToCounts,
        "12/SET_VOLTAGE": voltsToCounts,
        "13/SET_VOLTAGE": voltsToCounts,
        "14/SET_VOLTAGE": voltsToCounts,
        "15/SET_VOLTAGE": voltsToCounts,
        "16/SET_VOLTAGE": voltsToCounts,
        "SET_PEDESTAL_VOLTAGE": pedestalVoltsToCounts,
        "1/MEAS_VOLTAGE": measVoltsToCounts,
        "2/MEAS_VOLTAGE": measVoltsToCounts,
        "3/MEAS_VOLTAGE": measVoltsToCounts,
        "4/MEAS_VOLTAGE": measVoltsToCounts,
        "5/MEAS_VOLTAGE": measVoltsToCounts,
        "6/MEAS_VOLTAGE": measVoltsToCounts,
        "7/MEAS_VOLTAGE": measVoltsToCounts,
        "8/MEAS_VOLTAGE": measVoltsToCounts,
        "9/MEAS_VOLTAGE": measVoltsToCounts,
        "10/MEAS_VOLTAGE": measVoltsToCounts, 
        "11/MEAS_VOLTAGE": measVoltsToCounts, 
        "12/MEAS_VOLTAGE": measVoltsToCounts, 
        "13/MEAS_VOLTAGE": measVoltsToCounts, 
        "14/MEAS_VOLTAGE": measVoltsToCounts, 
        "15/MEAS_VOLTAGE": measVoltsToCounts, 
        "16/MEAS_VOLTAGE": measVoltsToCounts, 
        "MEAS_PEDESTAL_VOLTAGE": pedestalVoltsToCounts,
    }

    convertorsToString = {
        "TEMPERATURE": tempCountsToDegrees,
        "1/REF_VOLTAGE": countsToVolts,
        "2/REF_VOLTAGE": countsToVolts,
        "3/REF_VOLTAGE": countsToVolts,
        "4/REF_VOLTAGE": countsToVolts,
        "5/REF_VOLTAGE": countsToVolts,
        "6/REF_VOLTAGE": countsToVolts,
        "7/REF_VOLTAGE": countsToVolts,
        "8/REF_VOLTAGE": countsToVolts,
        "9/REF_VOLTAGE": countsToVolts,
        "10/REF_VOLTAGE": countsToVolts,
        "11/REF_VOLTAGE": countsToVolts,
        "12/REF_VOLTAGE": countsToVolts,
        "13/REF_VOLTAGE": countsToVolts,
        "14/REF_VOLTAGE": countsToVolts,
        "15/REF_VOLTAGE": countsToVolts,
        "16/REF_VOLTAGE": countsToVolts,
        "REF_PEDESTAL_VOLTAGE": pedestalCountsToVolts,
        "1/SET_VOLTAGE": measCountsToVolts,
        "2/SET_VOLTAGE": measCountsToVolts,
        "3/SET_VOLTAGE": measCountsToVolts,
        "4/SET_VOLTAGE": measCountsToVolts,
        "5/SET_VOLTAGE": measCountsToVolts,
        "6/SET_VOLTAGE": measCountsToVolts,
        "7/SET_VOLTAGE": measCountsToVolts,
        "8/SET_VOLTAGE": measCountsToVolts,
        "9/SET_VOLTAGE": measCountsToVolts,
        "10/SET_VOLTAGE": measCountsToVolts,
        "11/SET_VOLTAGE": measCountsToVolts,
        "12/SET_VOLTAGE": measCountsToVolts,
        "13/SET_VOLTAGE": measCountsToVolts,
        "14/SET_VOLTAGE": measCountsToVolts,
        "15/SET_VOLTAGE": measCountsToVolts,
        "16/SET_VOLTAGE": measCountsToVolts,
        "SET_PEDESTAL_VOLTAGE": pedestalCountsToVolts,
        "1/MEAS_VOLTAGE": measCountsToVolts,
        "2/MEAS_VOLTAGE": measCountsToVolts,
        "3/MEAS_VOLTAGE": measCountsToVolts,
        "4/MEAS_VOLTAGE": measCountsToVolts,
        "5/MEAS_VOLTAGE": measCountsToVolts,
        "6/MEAS_VOLTAGE": measCountsToVolts,
        "7/MEAS_VOLTAGE": measCountsToVolts,
        "8/MEAS_VOLTAGE": measCountsToVolts,
        "9/MEAS_VOLTAGE": measCountsToVolts,
        "10/MEAS_VOLTAGE": measCountsToVolts, 
        "11/MEAS_VOLTAGE": measCountsToVolts, 
        "12/MEAS_VOLTAGE": measCountsToVolts, 
        "13/MEAS_VOLTAGE": measCountsToVolts, 
        "14/MEAS_VOLTAGE": measCountsToVolts, 
        "15/MEAS_VOLTAGE": measCountsToVolts, 
        "16/MEAS_VOLTAGE": measCountsToVolts, 
        "MEAS_PEDESTAL_VOLTAGE": pedestalCountsToVolts,
    }

    def valueToString(self, cap:str, value:int) -> str:
        if cap in HVsysWall.convertorsToString:
            method = self.convertorsToString[cap]
            result = method(self, value)
            return str(result)
        else:
            return str(value)

    def valueFromString(self, cap:str, string:str) -> int:
        if cap in HVsysWall.convertorsToString:
            result = self.convertorsFromString[cap](self, string)
            return result
        else:
            return int(string)


    def has_reference_voltage(self):
        return True


    def request_voltage_change(self, cap, new_voltage) -> Message:
        # cap should be one of N/REF_VOLTAGE or REF_PEDESTAL_VOLTAGE
        if cap not in self.reference_voltage_caps(): 
            return None

        old_voltage = float(self.state[cap])
        self.state[cap] = new_voltage
        corrected_voltage = float(new_voltage) + self.voltage_correction()

        logging.info(f"Request {cap} change (id={self.config.id}) old={old_voltage} new={new_voltage} corrected={corrected_voltage}")

        if cap == 'REF_PEDESTAL_VOLTAGE':     # also update all the channel voltages
            for ch in range(1, self.config.n_channels+1):
                self.state[f'{ch}/REF_VOLTAGE'] += (float(new_voltage) - old_voltage)
        
        set_cap = cap.replace('REF', 'SET')     # 4/REF_VOLTAGE -> 4/SET_VOLTAGE to construct the command
        set_value = self.valueFromString(set_cap, corrected_voltage if cap == 'REF_PEDESTAL_VOLTAGE' else new_voltage) # apply correction ONLY to pedestal
        command = Message(Message.WRITE_SHORT, self.config.addr['hv'], self, set_cap, set_value)
        return command

    def request_voltage_correction(self) -> Message:
        set_value = self.valueFromString('SET_PEDESTAL_VOLTAGE', self.state['REQ_PEDESTAL_VOLTAGE'])
        command = Message(Message.WRITE_SHORT, self.config.addr['hv'], self, 'SET_PEDESTAL_VOLTAGE', set_value)
        return command


""" Doc

volatile uint16_t NEWCELL_ID @0x200;  // NEWCELL_ID (ro)
volatile uint16_t statcmd    @0x202;  // bit0(rw)-ON; bit1(ro)-error; bit2(rw) AccErr-Accumulated Error bit3(ro)-Pedestal RUP/RDWN
volatile uint8_t statcmdl    @0x203;  //   lsb of statcmd - compiler uses Big Endian addressing scheme
volatile uint16_t V[nch]     @0x204;  // nch V - 10-bit set voltages (0-255) for channels; in ISR on Timer4 V compared with Vcur to conduct RUP/RDWN
volatile uint16_t PedV       @0x224;  // PedV - PedV is keept in eeprom and in ISR on Timer4 PedV compared to PedVcur to conduct RUP/RDWN; gap in addresses intensionally left here
volatile uint16_t RUDtime    @0x226;  // RUDtime=1 corresponds to rampup time of Base Voltage (1023 bit) equal to 1023ms; RUDtime=0 -> immediate ON/OFF
volatile uint16_t Tmes       @0x228;  // Tmes - measured temperature (ro)
volatile int16_t  ccrc       @0x22a;  // ccrc - Check CRC - perform crc check on transmitted data if(ccrc!=0)
volatile uint16_t PedVcur    @0x24e;  // current PedV during RUP/RDN process in DAC bits; gap in addresses intensionally left here
volatile uint16_t Vmax       @0x250;  // Calibration value of channels Voltage in 10mV units, i.e. to get Volts one need eeVmax/100
volatile uint16_t PedVmax    @0x252;  // Calibration value of MAX pedestal Voltage in 10mV units, i.e. to get Volts one need PedVmax/100
volatile uint16_t PedVmin    @0x254;  // Calibration value of MIN pedestal Voltage in 10mV units, i.e. to get Volts one need PedVmin/100
volatile int16_t vers_date_l @0x256;  // for reference - version date - LS bytes
volatile int16_t vers_date_h @0x258;  // for reference - version date - MS bytes
volatile int16_t faultychs   @0x25a;  // bit=0 -> active (I2C) channel; bit =1 -> faulty channel
uint16_t neweeselfaddr       @0x25c;  // (wo) new address of the cell (will be active on next power on)
uint16_t errthrl             @0x262;  // error threshold Low Level
uint16_t errthrh             @0x264;  // error threshold High Level
uint16_t pwrONcnt            @0x266;  // (ro) counter of the cell power ON resets (times)
uint16_t IWDGcnt             @0x268;  // (ro) counter of the cell IWDG resets (times)
uint16_t Tint                @0x26a;  // (ro) internal uP Temperature T(grad.C)=Tint*0.488-273
uint16_t keepVset            @0x26c;  // (rw) keepVset - if(keepVset!=0) Vset value on change will be stored in eeprom
uint16_t restoreVset         @0x26e;  // (rw) restoreVset - if(restoreVset!=0) Vset value will be restored from eeprom on boot
uint16_t keepPedV            @0x270;  // (rw) keepPedV - if(keepPedV!=0) PedV value on change will be stored in eeprom
uint16_t restorePedV         @0x272;  // (rw) restorePedV - if(restorePedV!=0) PedV value will be restored from eeprom on boot
uint16_t commspeed           @0x274;  // (rw) 115 - 115200; any other -57600
uint16_t clraccerr           @0x276;  // (wo) writing to this address will clear AccErr bit in status
uint16_t snr1                @0x278;  // (rw) reprogrammable Serial Nr1
uint16_t snr2                @0x27a;  // (rw) reprogrammable Serial Nr2
uint16_t pnr1                @0x27c;  // (ro) programmable only ONCE Production Nr1
uint16_t pnr2                @0x27e;  // (ro) programmable only ONCE Production Nr2
uint16_t i2cret              @0x280;  // (ro) result of the last i2c transaction
uint16_t cell_reset          @0x282;  // (wo) enter endless loop and wait for IWDG restart on specific datum
"""
