#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



class HVsysPS:
    DESCRIPTION = "HV power source"
    pass


""" Documentation by hvsys 800e

ifboard ‐ universal InterFace BOARD ‐ 
 a constituent of different system controllers for high voltage cells. 
 
    1. Basic principles of communication. 
  Ifboard equipped with a set of input interfaces to communicate with 
controlling 
computer. They are: RS232, RS485, USB2 and Ethernet. 
Communication via RS232 and RS485 2‐wire interface is provided with 
parameters 57600 8 N 1. 
Commands to communicate with the controller are writing/reading control 
registers. 
The address in the command to access controller is 0 i.e. (aa = 00). 
 
The list of the commands : 
  "raassc\n" ‐> "ddddr\n" reads two bytes 
      from controller at subaddress "ss". 
  "waassddddc\n" ‐> "ddddr\n" write two bytes 
      of data "dddd" to cell "aa" at subaddress "ss" 
In the above commands: 
r and w ‐ ASCII characters 'r' and 'w'. 
aa      ‐ address, two hexadecimal digits in ASCII form. 
ss      ‐ subaddress, two hexadecimal digits in ASCII form. 
dddd    ‐ data, four hexadecimal digits in ASCII form. 
c ‐ CRC, Cyclic redundancy check‐ ones compliment of every DIGIT 
    (not byte) in hexadecimal form. 
All hexadecimal values presented using small letters. 
 
  Controller always include CRC value in reply. On the other hand, 
controller 
calculates and check CRC of incoming message only if "ccrc" register 
is nonzero (see below). CRC check of incoming message is disabled 
by default. 
To disable CRC check of incoming message ‐> w001700007\n . 
To enable CRC check of incoming message ‐> w001700010\n . 
On place of 'c' can be any digit but it must be present, as well 
as for all commands send to controller in case when incoming message CRC 
check is disabled. 
 
2. Addresses and description of the registers. 
Register. Subaddress. Description. 
 
10cell_id     0    (ro) controller ID ‐ constant 0x800e 
status      1    (ro) status register 
                  bit 0 ‐ Temperature status; 0‐OK 1‐Temperature 
protection. 
                   bit 1 ‐ LV error (0‐> OK) 
                   bit 2 ‐ BV error (0‐> OK) 
                   bit 3 ‐ HV protection active (0 ‐> No HV protection) 
 
BVON        2    (rw) BVON register switches ON (1) and off (0) Base 
Voltage of the controller 
Tup         3    (ro) Temperature of uP 
Tbrd        4    (ro) Temperature of board sensor 
Tps         5    (ro) Temperature of power supply sensor 
LV          6    (ro) LV (Volt*10) 
BV          7    (ro) BV (Volt*10) 
T_fan_off   0x10 (rw) T_fan_off Temperatue (grad C) to switch off the 
module FAN 
T_fan_on    0x11 (rw) T_fan_on  Temperatue (grad C) to switch on the 
module FAN 
T_shutdown  0x12 (rw) T_shutdown Temperatue (grad C) to switch off cells. 
LVll        0x13 (rw) LV absolute value lower limit (same units as 
readout from addr.0x6) 
LVul        0x14 (rw) LV absolute value upper limit 
BVll        0x15 (rw) BV absolute value lower limit (same units as 
readout from addr.0x7) 
BVul        0x16 (rw) BV absolute value upper limit 
ccrc        0x17 (rw) ccrc ‐ Check CRC ‐ perform crc check on transmitted         
data if(ccrc!=0) 
NTsens      0x18 (rw) NTsens ‐ which T sensor use for temperature 
controll (0‐>uP, 1‐>board, 2‐>Power Supply) 
CserNr      0x19 (ro) controller serial Nr. 
WrFlash     0x1f (wo) WrFlash ‐ writing to this address will store ALL 
registers with addresses  0x10‐0x19  in the last uP Flash page 
 
Abbreviations for the above table: 
(ro)  ‐ read only 
(rw)  ‐ read/write 
(wo)  ‐ write only 
BV  ‐ Base supply Voltage 
LV  ‐ Low supply Voltage 
 
Examples(CRC check disabled): 
w001700007 
r00000 
 
 
3. Nonvolatile registers. 
 
  Value of some registers are being kept in eeprom. Therefore on power on 
the cell restores last values of the following registers: 
T_fan_off, T_fan_on, T_shutdown, LVll, LVul, BVll, BVul, ccrc, NTsens and 
CserNr. 
11Приложение 2.
complex15 - complex HV cell version 15.
Commands to communicate with cell are writing/reading control registers. 
Serial line communication parameters : 57600 8 N 1. 
 
The list of the command : 
"raassc\n" ‐> "dddd_\n" reads two bytes from cell "aa" at subaddress 
"ss". 
"waassddddc\n" ‐> "dddd_\n" write two bytes of data "dddd" to cell "aa" 
at subaddress "ss" 
 
All values like "aa", "ss", "dddd" are in hexadecimal format. 
 
c ‐ CRC ‐ Cyclic redundancy check‐ ones compliment of every DIGIT 
(not byte) in hexadecimal form. 
  Cell always include CRC value in reply. On the other hand, cell 
calculate and check CRC of incoming message only if "ccrc" register 
is nonzero (see below). CRC check of incoming message is disabled 
by default. 
  To disable CRC check of incoming message ‐> waa1e0000c\n . 
For example, for cell 01 the command would be w011e0000c where 
c would be (~(0+1+1+e+0+0+0+0))&0xf ‐> f (0xf) 
i.e. for the cell 01 the command would be "w01100000f\n" 
To enable CRC check of incoming message ‐> waa1600010\n . 
On place of 'c' can be any digit but it must be present, as well 
as for all commands send to cell in case when incoming message CRC 
check is disabled. 
 
 
Addresses and descripton of registers of the HV cell: 
 
Variable/register   subaddress        Description 
name 
 
cell_id            sa=0  (rw) cell_id 
ctl_stat           sa=1  (rw) used to Control a cell(channel) and check 
its Status 
  chons            sa=1 bit 0  chanel on bit ‐ controls and reflects 
on/off state of the cell. 1‐>on 
  err              sa=1 bit 1  cell error bit; 1‐>error . 
  acerr            sa=1 bit 2  cell ACcumulated Error (since last read) 
bit 
  iovld            sa=1 bit 3  I overload bit; 0 ‐> output current is OK 
i.e. NO current limiting regime 
  bverr            sa=1 bit 4  Base Volage error 
  hwerr             sa=1 bit 5  Hardware failure error bit 
  rdab              sa=1 bit 6  ramp down active bit 
  ruab              sa=1 bit 7  ramp up active bit 
  sbyb              sa=1 bit 8  standby bit 
12  iopb              sa=1 bit 9  ioprot bit (cleared by writing [new] Vset 
and on switching on HV ) 
VsetON              sa=2  (rw) set Voltage in DAC bits (12 bit) 
Vmes                sa=3  (ro) measured output Voltage in ADC bits (12 
bit) 
Iset               sa=4  (rw) Current Limit setpoint in DAC bits (10 bit) 
Imes                sa=5  (ro) Measured Current  in ADC bits (12 bit) 
Ustdby              sa=6  (rw) Voltage value in DAC bits for STanDBY 
regime 
rupspeed            sa=7  (rw) Speed of U ramp up (Volt/sec) 
rdwnspeed           sa=8  (rw) Speed of U ramp down (Volt/sec) 
prottim             sa=9  (rw) Delay to switch STanDBY voltage after 
IOVLD 
Umin                sa=10 (rw) Real output voltage (Volt) at 0 dac data 
Umax                sa=11 (rw) Real output voltage (Volt) at maximal dac 
data 
Imax                sa=12 (rw) Real value of current threshold limit (uA) 
at maximal dac data 
Umesmax             sa=13 (rw) Calculated(calibrated) value (Volt) 
coresponding to maximal ADC value 
Imesmax             sa=14 (rw) Calculated(calibrated) value (uA) 
coresponding to maximal ADC value 
MINUS_n_BITS        sa=15 (ro) (0x8000 | 12<<8 | 10<<4 | 12) ; minus‐
>0x8000; 12<<8‐>12 ADC bits; 10<<4‐>10 I_DAC bits; 12‐>12 U_DAC bits; 
UOKmin              sa=16 (rw) Lower error threshold of the cell (do not 
change!) 
UOKmax              sa=17 (rw) Upper error threshold of the cell (do not 
change!) 
IOKmin              sa=18 (rw) Error threshold of the current limiting 
scheme (do not change!) 
BVOKmin             sa=19 (rw) Lower error threshold of the Base Voltage 
power supply for the cell (do not change!) 
ccrc                sa=20 (rw) ccrc ‐ Check CRC ‐ perform crc check on 
transmitted data if(ccrc!=0) 
keepVset            sa=21 (rw) keepVset. if(keepVset!=0) On change VsetON 
value will be stored in eeprom and restored on boot. 
ONonBOOT            sa=22 (rw) ONonBOOT ‐ if(ONonBOOT!=0) the cell turn 
on HV on power ON (used in standalone mode) 
HVOFFonIOPB         sa=23 (rw) HVOFFonIOPB ‐ the cell turn off HV if I 
overload protection fired 
Imes2               sa=24 (ro) Measured Current ‐ Second rough channel  
in ADC bits (12 bit) 
Imes2max            sa=25 (rw) calculated(calibrated) value (uA) 
coresponding to maximal ADC value for the second rough channel 
 
Abbreviations for the above table: 
(ro)  ‐ read only 
(rw)  ‐ read/write 
 
Nonvolatile memory content: 
13 
  Value of some registers are being kept in eeprom. Therefore on power on 
the cell restores their last values. 
 
eeselfaddr          Address of the cell 
eeVsetON            Defines Vset voltage to restore on boot if necessary 
(standalone mode); see eekeepVset 
eeIset              Defines Iset value to restore on boot 
eeUstdby            Defines standby voltage after protection 
eerupspeed          Defines speed of U ramp up (Volt/sec) 
eerdwnspeed         Defines speed of U ramp down (Volt/sec) 
eeprottim           Delay to switch STanDBY voltage after IOVLD; 0xffff ‐
> NEVER 
eeUmin              Stored in eeprom real output voltage (Volt) at 0 dac 
data 
eeUmax              Stored in eeprom real output voltage (Volt) at 
maximal dac data 
eeImax              Stored in eeprom real value of current threshold 
limit (uA) at maximal dac data 
eeUmesmax           Stored in eeprom calculated(calibrated) value (Volt) 
coresponding to maximal ADC value 
eeImesmax           Stored in eeprom calculated(calibrated) value (uA) 
coresponding to maximal ADC value 
eeMINUS_n_BITS      (0x8000 | 12<<8 | 10<<4 | 12);  minus‐>0x8000; 12<<8‐
>12 ADC bits; 10<<4‐>10 I_DAC bits; 12‐>12 U_DAC bits; 
eeUOKmin            Lower error threshold of the cell (do not change!) 
eeUOKmax            Upper error threshold of the cell (do not change!) 
eeIOKmin            Error threshold of the current limiting scheme (do 
not change!) 
eeBVOKmin           Lower error threshold of the Base Voltage power 
supply for the cell (do not change!) 
eeccrc              Check CRC ‐ perform crc check on transmitted data 
if(ccrc!=0) 
eekeepVset          If(eekeepVset!=0) Vset value will be stored in eeprom 
and restored on boot 
eeONonBOOT          If(eeONonBOOT!=0) the cell turn on HV on power ON 
(used in standalone mode) 
eeHVOFFonIOPB       The cell turn off HV if I overload protection fired 
eeImes2max          Stored in eeprom calculated(calibrated) value (uA) 
coresponding to maximal ADC value 
eecell_id           cell type ID 
eeKramp             Ramp up/down constant 

"""