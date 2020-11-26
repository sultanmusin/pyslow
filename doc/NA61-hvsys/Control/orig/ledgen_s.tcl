#!/bin/sh
# the next line restarts using wish \
exec wish "$0" "$@"

proc init_vars { } {
 set ::debug 0
 set ::dos 0; set ::portbasename /dev/ttyUSB      ;# assume os platform is LINUX
 if {[string equal "Windows NT" $::tcl_platform(os)]} {set ::dos 1; set ::portbasename com}
 wm title . "HVSys LED generator"
 focus -force .; if {$::debug!=0 && $::dos==1} {console show; update}
 wm protocol . WM_DELETE_WINDOW {exit}
 set ::font -adobe-helvetica-*-r-*-*-12-*-*-*-*-*-*-*

 set ::cell 0       ;# LED Cell number on rs485 branch
 set ::portname ""  ;# serial port name
 set ::portmin 0    ;# first serial port in scan
 set ::portmax 8    ;# last serial port in scan
 set ::cellmin 1    ;# first cell address in scan
 set ::cellmax 255  ;# last cell address in scan
 set ::FREQfl 0; set ::PINspfl 0; set ::AVptsfl 0; set ::ONfl 0; set ::OFFfl 0; set ::DACfl 0; set ::AUTOfl 0;# flags to set the values
 set ::PINsp  0     ;# PIN ADC setpoint
 set ::ePINsp 0     ;# entry PIN ADC setpoint to be set
 set ::rADC 0       ;# value readed from PIN ADC
 set ::AVpts 0      ;# number of averaging points for ADC
 set ::eAVpts 0     ;# entry number of averaging points for ADC to be set
 set ::DAC 0        ;# DAC value
 set ::eDAC 0       ;# entry DAC value to be set 
 set ::FREQ 0       ;# variable corresponding to "FREQ" enry
 set ::eFREQ 0      ;# entry FREQ that was set to generator
 set ::df ""
 set ::clist ""     ;# list of active cells found
 set ::amax 17      ;# max number of attempts to communicate with cell
} ;# end of init_vars

proc scan_for_ledgen { } {                                              ;# find out the FIRST ledgen cell number on branch
  focus -force .; wm geometry . 500x20+40+20; set title [wm title .]    ;# resize window and save current title
  wm protocol . WM_DELETE_WINDOW { exit }                               ;# needed for clean exit without TCL messages
  if { [winfo exists .noconn] } { destroy .noconn }                     ;# delete popup if it is already exists
  if {$::argc == 2 && [string is integer [lindex $::argv 0]] && [string is integer [lindex $::argv 1]]} \
    {set ::portmin [lindex $::argv 0]; set ::portmax [lindex $::argv 0] ;# restrict port/cell scan to command line parameters
    set ::cellmin [lindex $::argv 1]; set ::cellmax [lindex $::argv 1];
    }
  if {$::argc == 3 && [string is integer [lindex $::argv 0]] && [string is integer [lindex $::argv 1]] && [string is integer [lindex $::argv 2]]} \
    {set ::portmin [lindex $::argv 0]; set ::portmax [lindex $::argv 0] ;# restrict port/cell scan to command line parameters
    set ::cellmin [lindex $::argv 1]; set ::cellmax [lindex $::argv 2];
    }
  set ::conn ""; set scanned ""                                         ;# here we will keep list of scanned ports
  for {set i $::portmin} {$i <= $::portmax} {incr i} {                  ;# cycle through com ports and try to connect
    update
    if {[catch {set ::conn [open $::portbasename$i r+]} err]} {continue};# try to open com port, if err continue with next port
    fconfigure $::conn -blocking 0 -buffering none -mode 57600,n,8,1
    for {set c $::cellmin} {$c <= $::cellmax} {incr c} {
      wm title . "HVSys - looking for ledgen cell on $::portbasename$i $c "; update ;update idletasks;# set tempopary title
      cellreadID $c                                                     ;# try to read ID of ledgen cell
      ##if {$::debug!=0} {puts "$c [string first "8006" $::reply 0] __$::reply "};
      if { [string first "8006" $::reply 0] >= 0 } {
        set ::portname $::portbasename$i;
        lappend ::clist $c                                              ;# update list of active cells found
        }
      }  ;# end for {set c 1} {$c < 256}
    if {[llength $::clist] > 0} {
      set ::cell [lindex $::clist 0];                                    ;# if something found make first found cell active ...
      wm resizable . 0 0; wm geometry . "" ; wm title . $title; update  ;# restore original title
      return;}                                                          ;# ... and exit from scan_for_ledgen if we found some cells on the current port
    set scanned "$scanned $::portbasename$i "                           ;# go to next port
    }  ;# end for cycle for ports
                                                                        ;# if we couldn't connect to ctl on any port ....
  toplevel .noconn -bg moccasin ; label .noconn.nc  -bg moccasin -text "Can not connect to ledgen cell on ports $scanned" -font {-size -18}
  button .noconn.d -bg salmon1 -text "Dismiss" -command "exit" -font {-size -18}; pack .noconn.nc;  pack .noconn.d ;
  bind .noconn <KeyPress-Return> { exit }                               ;# inform user if there is no available controller
  wm title .noconn "connection failure"; focus -force .noconn;
  for {set d 0} {$d < 200} {incr d} {
    after 100
    update idletasks; update;}
  scan_for_ledgen;                                                      ;# rescan ports in 20 seconds
} ;# end of scan_for_ledgen

proc get_r232ch { nch } { ;# get $nch chars, NOT !!! including trailing LF, (or timeout~50ms) from RS232 
  set ::reply ""; set answ "";
  for {set i 0} {$i < 25} {incr i} {
    if {$i==100 && [string compare "" $::reply] == 0} {return -1}    ;# if there is NO data for 200ms-> stop waiting (needed to speed up scan for cell)
    catch {set answ [read $::conn]} err; set ::reply "$::reply$answ"
    if {[string length $::reply]==$nch && [string index $::reply end]=="\n"} {return 0}
    after 2
    }
  return -1;                                                        ;# Timeout error
};#end get_r232ch

proc get_r232 { } { ;# wait LF (or timeout~50ms) from RS232
 set ::reply "";    set answ ""
 for {set i 0} {$i < 25} {incr i} {
   if {$i==10 && [string compare "" $::reply] == 0} {return}          ;# if there is NO data for 12ms-> stop waiting (needed to speed up scan for cell)
   after 4
   catch {set answ [read $::conn]} err; set alen [string length $answ]; set ::reply "$::reply$answ"
   set ch ""; if { $alen != 0 } { set ch [string range $answ end end] }
   if { $ch == "\n" } { break } }
 if { [string compare "" $::reply] == 0} {  ;# Error RS232 connection - let user know this
   wm title . "LEDgen - NO RS232 connection" } ;
 update
};#end get_r232

proc create_and_pack { } {                 ;# create gui
pack [frame .mf -bd 1] -side top -fill both -expand 1                   ;# This is the main frame - .mf
bind . <Key-Escape> { exit }                                            ;# q -quick exit
if {[llength $::clist] > 1} {                                           ;# if we have more than 1 LED cell
  pack [frame .mf.bf -bd 1] -side top -pady 10 -fill both  -expand 1              ;# Buttons field frame
  foreach {c} $::clist \
    {pack [button .mf.bf.c$c -activebackground white -relief raised -bd 5 -padx 0 -width 3 -command [list set ::cell $c] -text $c;] \
      -side left -padx 0 -expand 1 -fill x}
  }
pack [frame .mf.up -bd 1] -side top -fill both  -expand 1              ;#control PIN ADC setpoint frame
pack [label .mf.up.lu -width 12 -font $::font -relief groove -text "PIN setpoint"] -side left
pack [entry .mf.up.u -width 6 -textvariable ::ePINsp -font $::font -bg white -relief groove] -side left
bind  .mf.up.u <KeyPress-Return> {set ::PINspfl 1}
pack [button .mf.up.su -width 14 -text "Set PIN setpoint" -bg CadetBlue2 -font $::font -command {set ::PINspfl 1}] -side left -padx 2
pack [label .mf.up.setu -widt 6 -font $::font -relief groove -textvariable ::PINsp] -side left
pack [label .mf.up.ru -width 6 -font $::font -textvariable ::rADC -relief groove -bg PaleGreen1] -side right
pack [label .mf.up.lru -width 14 -font $::font -relief groove -bg PaleGreen1 -text "read PIN ADC"] -side right

pack [frame .mf.ap -bd 1] -side top -fill both  -expand 1 -pady 3      ;# avpts control frame
pack [label .mf.ap.lf -width 12 -font $::font -relief groove -text "Avrg. Points"] -side left
pack [entry .mf.ap.f -width 6 -textvariable ::eAVpts -font $::font -relief groove -bg white -relief groove] -side left
bind  .mf.ap.f <KeyPress-Return> {set ::AVptsfl 1}
pack [button .mf.ap.sf -width 14 -text "Set Avrg. Points" -bg CadetBlue2 -font $::font -command {set ::AVptsfl 1;}] -side left -padx 2
pack [label .mf.ap.rf -width 6 -font $::font -textvariable ::AVpts -bg OliveDrab2 -relief groove] -side right
pack [label .mf.ap.lrf -width 14 -font $::font -relief groove -bg OliveDrab2 -text "Avrg. Points"] -side right

pack [frame .mf.fp -bd 1] -side top -fill both  -expand 1 -pady 3      ;# FREQ control frame
pack [label .mf.fp.lf -width 12 -font $::font -relief groove -text "LED freq.(Hz)"] -side left
pack [entry .mf.fp.f -width 6 -textvariable ::eFREQ -font $::font -relief groove -bg white -relief groove] -side left
bind  .mf.fp.f <KeyPress-Return> {set ::FREQfl 1}
pack [button .mf.fp.sf -width 14 -text "Set LED freq." -bg CadetBlue2 -font $::font -command {set ::FREQfl 1;}] -side left -padx 2
pack [label .mf.fp.rf -width 6 -font $::font -textvariable ::FREQ -bg SeaGreen2 -relief groove] -side right
pack [label .mf.fp.lrf -width 14 -font $::font -relief groove -bg SeaGreen2 -text "freq. (Hz)"] -side right

pack [frame .mf.v -relief groove -bd 1] -side top -fill both  -expand 1  -pady 3       ;# DAC frame
pack [label .mf.v.lf -width 12 -font $::font -relief groove -text "LED DAC"] -side left
pack [entry .mf.v.d -width 6 -textvariable eDAC -font $::font -relief groove -bg white -relief groove] -side left
bind  .mf.v.d <KeyPress-Return> {set ::DACfl 1}
pack [button .mf.v.sf -width 14 -text "Set LED DAC" -bg CadetBlue2 -font $::font -command {set ::DACfl 1;}] -side left -padx 2
pack [label .mf.v.rf -width 6 -font $::font -textvariable ::DAC -bg DarkSeaGreen3 -relief groove] -side right
pack [label .mf.v.lrf -width 14 -font $::font -relief groove -bg DarkSeaGreen3 -text "LED DAC"] -side right

pack [frame .mf.a -relief groove -bd 1] -side top -fill both  -expand 1  -pady 3       ;# Autoreg file frame
pack [checkbutton .mf.a.auto -width 10 -text "AUTO control" -bg lightblue -font $::font -relief groove] -side left -fill both -expand 1
pack [label .mf.a.stat -width 8 -font $::font -textvariable ::stat -bg SeaShell -relief groove] -side left -fill y;# -expand 1
bind .mf.a.auto <ButtonPress-1> {set ::AUTOfl 1}
pack [checkbutton .mf.a.log -width 10 -text "Log to file" -bg lightgreen -font $::font -relief groove] -side left
pack [label .mf.a.lf -width 19 -font $::font -textvariable ::fname -bg SeaShell -relief groove] -side left -fill both -expand 1
proc logfile { } {if {!$::log} {set ::fname "led_[clock format [clock seconds] -format %d%m%y_%H%M%S]"; set ::df [open $::fname w]} else {after 100 close $::df;};}
bind .mf.a.log <ButtonPress-1> logfile

pack [frame .mf.oc -bd 1] -side top -fill both -expand 1 -pady 3       ;# GEN Output Control frame
pack [button .mf.oc.on -text "LED generator ON" -bg green3 -font $::font -command {set ::ONfl 1}] -side left -fill both  -expand 1
pack [button .mf.oc.off -text "LED generator OFF" -bg red3 -font $::font -command {set ::OFFfl 1}] -side left -fill both  -expand 1
} ;# end of create_and_pack

proc new_data { } {
 if {$::FREQfl} {                                   ;# let's have a look on flags - do we need to set new parameters?
    set ::FREQ $::eFREQ; set ::FREQfl 0;
    cellwritefreq
    cellreadfreq; set ::FREQ [scan [string range $::reply 0 3 ] "%4x"]  ;# reread real freq value back from the cell
    }
 if {$::DACfl} {
    set ::DAC $::eDAC; set ::DACfl 0;
    cellwritedac 
    cellreaddac; set ::DAC [scan [string range $::reply 0 3 ] "%4x"]    ;# reread real DAC value back from the cell
    }
 if {$::PINspfl} {
    set ::PINsp $::ePINsp; set ::PINspfl 0;
    cellwritepinsp 
    cellreadpinsp; set ::PINsp [scan [string range $::reply 0 3 ] "%4x"];# reread real PINsp value back from the cell
    }
 if {$::AVptsfl} {
    set ::AVpts $::eAVpts; set ::AVptsfl 0;
    cellwriteavpts 
    cellreadavpts; set ::AVpts [scan [string range $::reply 0 3 ] "%4x"];# reread real AVpts value back from the cell
    }
 if {$::AUTOfl} {set ::AUTOfl 0;  
  cellwriteauto                                                         ;# send auutoref flag to the cell
  cellreadauto; set ::auto [scan [string range $::reply 0 3 ] "%4x"]    ;# reread real auto value back from the cell
  }
 if {$::ONfl} {set ::FREQ $::eFREQ; set ::ONfl 0; cellwritefreq         ;# switch ON ledgen by puting $FREQ to it
    cellreadfreq; set ::FREQ [scan [string range $::reply 0 3 ] "%4x"]} ;# reread real freq value back from the cell
 if {$::OFFfl} {set ::FREQ 0; set ::OFFfl 0; cellwritefreq }            ;# switch OFF ledgen by puting 0 frequency to it to it

 # after flags processing lets reread ::cell (may be changed one) values  
 cellreadpinadc                                     ;# command to read ADC channel E(i.e.PIN diod) from module
 set tmp_rADC [scan [string range $::reply 0 3] "%4x"];# get readed value
 if { $tmp_rADC != 0xffff } \
    {set ::rADC $tmp_rADC                           ;# display readed value ...
    cellclearpinadc                                 ;# and set it to 0 in the cell as indication of value was readed
    cellreaddac; set ::DAC [scan [string range $::reply 0 3 ] "%4x"]                            ;# in case of successful reading of rADC read also DAC
    cellreadstat $::cell
    ##if {$::debug!=0} {puts "____$::reply "};
    set tmp [scan [string range $::reply 0 3 ] "%4x"] ;# read also stat i.e. regulation error 
    if { $tmp&0x8000 } {set ::stat [expr -(65536-$tmp)]} else {set ::stat $tmp}                 ;# ... and convet hex back to signed
    if { [expr abs($::stat)]>2 } {.mf.a.stat configure -bg red} else {.mf.a.stat configure -bg green} ;# colorise the label by red/green
    cellreadpinsp; set ::PINsp [scan [string range $::reply 0 3 ] "%4x"]                        ;# read real PINsp value from the cell
    cellreadavpts; set ::AVpts [scan [string range $::reply 0 3 ] "%4x"]                        ;# read real AVpts value from the cell
    cellreadfreq; set ::FREQ [scan [string range $::reply 0 3 ] "%4x"]                          ;# read real freq value from the cell
    cellreadauto; set ::auto [scan [string range $::reply 0 3 ] "%4x"]                          ;# read real auto value from the cell
    set ::lsup [clock format [clock seconds] -format "Last Updated:\r %H:%M:%S"]                ;# last updated label correspons to the last readed value
    wm title . "HVSys LED generator. $::portname Cell=$::cell $::lsup"                          ;# in case title was changed (::cell change or rs232 problems)
    if {$::log && $::df!=""} {puts $::df "[clock seconds] $::cell $::rADC $::DAC $::PINsp "}
    }
 # cycle through all cells and display their status
 if {[llength $::clist] > 1} {                                           ;# if we have more than 1 LED cell
  foreach {c} $::clist \
    {cellreadstat $c
    set tmp [scan [string range $::reply 0 3 ] "%4x"] ;# read also stat i.e. regulation error 
    if {$tmp&0x8000} {set tmp [expr -(65536-$tmp)]}                                             ;# ... and convet hex back to signed
    if {[expr abs($tmp)]>2} {.mf.bf.c$c configure -bg red} else {.mf.bf.c$c configure -bg green};# colorise the label by red/green
    .mf.bf.c$c configure -bd 5
    if {$c==$::cell} {.mf.bf.c$c configure -bd 10}
    }
   } 
 update; update idletasks
 after 500 new_data
} ;# end of new_data

# Cell communication subroutines
proc cellwritefreq { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "w%02x04%04x_\r" $::cell [expr $::FREQ&0xffff]]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}   ;# set new FREQency
# remember freq in range (1-1000) -> internal gen; freq out of range (1-1000) (for example -1) -> external gen/sync. IF freq=0 -> LED disabled    
proc cellreadfreq { }  {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "r%02x04_\r" $::cell]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}               ;# read FREQency
proc cellwritedac { }  {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "w%02x08%04x_\r" $::cell $::DAC]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}    ;# set LED setting to DAC
proc cellreaddac { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "r%02x08_\r" $::cell]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}               ;# read LED DAC setting 
proc cellwritepinsp { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "w%02x0a%04x_\r" $::cell $::PINsp]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}  ;# set new PIN ADC setpoint
proc cellreadpinsp { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "r%02x0a_\r" $::cell ]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}              ;# read PIN ADC setpoint
proc cellreadpinadc { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "r%02x0e_\r" $::cell]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}               ;# read PIN diode ADC from the cell
proc cellclearpinadc { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "w%02x0effff_\r" $::cell]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}           ;# write ffff to location of PIN diode ADC 
proc cellwriteavpts { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "w%02x06%04x_\r" $::cell $::AVpts]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}  ;# set number of points to average ADC readings
proc cellreadavpts { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "r%02x06_\r" $::cell]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}               ;# read number of points to average ADC readings
proc cellwriteauto { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "w%02x02%04x_\r" $::cell $::auto]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}   ;# send autoreg flag to the cell
proc cellreadauto { } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "r%02x02_\r" $::cell]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}               ;# read autoreg flag from the cell
proc cellreadstat { c } {for {set a 0} {$a<$::amax} {incr a} \
  {puts -nonewline $::conn [format "r%02x00_\r" $c]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}                    ;# read stat from the cell
proc cellreadID { c } {for {set a 0} {$a<2} {incr a} \
  {puts -nonewline $::conn [format "r%02x0c_\r" $c]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}                    ;# read ledgen ID 
##proc cellreadID { c } {puts -nonewline $::conn [format "r%02x0c_\r" $c]; get_r232;}                    ;# read ledgen ID 

#----------------------- MAIN PROCEDURE --------------------------
init_vars                         ;# some global vars
scan_for_ledgen                   ;# find out the FIRST ledgen cell number on branch
create_and_pack                   ;# create gui
cellreadfreq; set ::eFREQ [scan [string range $::reply 0 3 ] "%4x"]; set ::FREQ $::eFREQ 
cellreaddac; set ::eDAC [scan [string range $::reply 0 3 ] "%4x"]; set ::DAC $::eDAC 
cellreadpinsp; set ::ePINsp [scan [string range $::reply 0 3 ] "%4x"]; set ::PINsp $::ePINsp 
cellreadavpts; set ::eAVpts [scan [string range $::reply 0 3 ] "%4x"]; set ::AVpts $::eAVpts 
cellreadauto; set ::auto [scan [string range $::reply 0 3 ] "%4x"]
new_data                          ;# recursive - communicate to cell and put/get new data