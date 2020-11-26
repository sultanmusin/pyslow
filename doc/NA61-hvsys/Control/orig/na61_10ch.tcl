#!/bin/sh
# the next line restarts using wish \
exec wish "$0" "$@"

proc init_vars { } {
  set ::debug 0; interp alias {} ? {} set ErrorInfo;
  set ::demo 0
  set ::win 0; set ::portbasename /dev/tty      ;# assume os platform is LINUX; 
  if {[string equal "Windows NT" $::tcl_platform(os)]} {set ::win 1; set ::portbasename com}
  set ::portnum 5     ;# com port number
  set ::cellmin 1     ;# range to search
  set ::cellmax 255   ;
  set ::celllist {}   ;# List of HV Cells on rs485 branch
  set ::cell 0        ;# HV Cell number on rs485 branch ; AUTODETECT is working now
  set ::activecell "" ;# active cell
  set ::nch 11        ;# number of channels in cell including pedestal channel
  set ::Umin 0.0;
  set ::tempcnt -1    ;# counter for averaging TEMPerature
  set ::tc 0          ;# Thermocompensation
  set ::lsup ""       ;# last updated
  set ::activeRUDS 10 ;# Ramp up/down speed
  set ::activerdRUDS "";# current ramp up/down speed
  set ::setGENfl 0    ;# flag to switch on GEN
  set ::setRUDSfl 0   ;# flag to set Ramp up/down speed
  for {set n 0} {$n < $::nch} {incr n} { set ::setUfl($n) 0 } ;# flags to set U and enbl/disabl corresp. chanel
  set ::dacmax 4095   ;# inspite of DAC itself is 10 bit it uses 12bit data !!! Two LSBits would be ignored in the chip.
  set ::font {-size 12} 
  set ::er232 0
  set ::amax 31       ;# max number of attempts to communicate with cell
  set ::amax_id 3     ;# max number of attempts to communicate with cell during scan, i.e. rading ID
}

proc demo { } {
	exit
  set ::demo 1; set ::celllist {2 3 4};
  set ::activecell [lindex $::celllist 0]                     ;# starting active cell number
  }

proc detectcell { } {                                         ;# find out the FIRST cell number
  wm protocol . WM_DELETE_WINDOW {wsf; exit}
  if {$::debug!=0 && $::win!=0} {after 200 console show}; after 300 focus -force .;
  if {$::argc != 0 } {set ::portnum [lindex $::argv 0]}       ;# set port number to the first command line parameter
  if {$::argc >= 3 && [string is integer [lindex $::argv 1]] && [string is integer [lindex $::argv 2]] } \
    {set ::cellmin [lindex $::argv 1]; set ::cellmax [lindex $::argv 2]}                ;# restrict cells scan to command line parameters

  if {[catch {set ::conn [open $::portbasename$::portnum r+]} err]} {demo; return}      ;# try to open com port
  fconfigure $::conn -blocking 0 -buffering none -translation binary -mode 57600,n,8,2  ;# if connect OK

  pack [label .sc  -bg moccasin -font {-size -18}]; update    ;# temporary title
  for {set c $::cellmin} {$c<$::cellmax} {incr c} {
    .sc configure -text "Detecting cell $c on port $::portbasename$::portnum"; update
    cellreadID  $c                                            ;# try to read status of the cell
    if { [string first "8005" $::reply] >= 0 } {
      lappend ::celllist $c                                   ;# and form the list of existing modules
    }
  } ;# end for
  destroy .sc
  set ::activecell [lindex $::celllist 0]                     ;# starting active cell number
  if {$::activecell==""} {demo}
  foreach c $::celllist { for {set n 0} {$n < $::nch} {incr n} {set ::U($c,$n) 0;} }
}

proc get_r232ch { nch } {                                     ;# get $nch chars, NOT !!! including trailing LF, (or timeout~50ms) from RS232 
  if {$::demo} {set ::reply "0001_\n"; return}                ;# if NO com port open or cells found
  set ::reply ""; set answ "";                    
  for {set i 0} {$i < 100} {incr i} {                         ;# 100 -> 200 ms timeout
    if {$i==20 && [string compare "" $::reply]==0} {return -1};# if there is NO data for 20*2=40ms-> stop waiting (needed to speed up scan for cell)
    catch {set answ [read $::conn]} err; set ::reply "$::reply$answ";
    if {[string length $::reply]==$nch && [string index $::reply end]=="\n"} {return 0} ;# OK
    after 2
    }
  return -1;                                                        ;# Timeout error
};#end get_r232ch

proc get_r232 { } { ;# wait LF (or timeout~1sec) from RS232
  if {$::demo} {set ::reply "0001_\n"; return}  ;# if NO com port open or cells found
  set ::reply ""; set answ ""; set ::er232 0;
  for {set i 0} {$i<250} {incr i} {
    if {$i==25 &&  [string compare "" $::reply]==0} {set ::er232 1; return}     ;# return after 100ms if nothing come
    update idletasks ; update;
    after 4
    catch {set answ [read $::conn]} err; set alen [string length $answ]; set ::reply "$::reply$answ"
    set ch ""; if {$alen != 0} { set ch [string range $answ end end]; if { $ch == "\n" } { return} }
    }
  if { [string compare "" $::reply] == 0} {  ; #ERROR RS232 CONNECTION - let user know this
    wm title . "HVSys APD HV - NO RS232 connection" } else {wm title . "HVSys APD HV"} ;
};#end get_r232

proc validReal {win event X oldX min max bg_on_change} { ;# Allow valid reals, empty strings, sign without number. Reject Octal numbers, but allow a single "0"
 if {$min > $max} {set tmp $min; set min $max; set max $tmp} ;  # Make sure min<=max
 # Which signes are allowed ?
 if {($min < 0) && ($max >= 0)} { set pattern {^[+-.]?(()|([0-9.]*))$}  ;# positive & negative sign
 } elseif {$max < 0} { set pattern {^[-.]?(()|([0-9.]*))$}              ;# negative sign
 } else { set pattern {^[+.]?(()|([0-9.]*))$} }                         ;# positive sign (+)
 set weakCheck [regexp $pattern $X] ;# Weak integer checking: allow empty string, empty sign, reject octals
 if {! $weakCheck} {set X $oldX}    ;# if weak check fails, continue with old value
 # next comes Strong real(double) checking with range OR emty string!!! Empty string will be checked and not allowed in bind
 set strongCheck [expr {([string is double -strict $X] && ($X >= $min) && ($X <= $max) ) || ([string length $X]==0) }]
 switch $event {
   key { $win configure -bg [expr {$strongCheck ? $bg_on_change : "yellow"}] ; return $strongCheck }
   focusout { if {! $strongCheck} {$win configure -bg red} ; return $strongCheck }
   default { return 1 } }
} ;# end of proc validReal

proc validInt {win event X oldX min max} { ;# Allow valid integers, empty strings, sign without number. Reject Octal numbers, but allow a single "0"
 if {$min > $max} {set tmp $min; set min $max; set max $tmp} ;  # Make sure min<=max
 # Which signes are allowed ?
 if {($min <= 0) && ($max >= 0)} { set pattern {^[+-]?(()|0|([1-9][0-9]*))$}  ;# positive & negative sign
 } elseif {$max < 0} { set pattern {^[-]?(()|0|([1-9][0-9]*))$}               ;# negative sign
 } else { set pattern {^[+]?(()|0|([1-9][0-9]*))$} }                          ;# positive sign
 set weakCheck [regexp $pattern $X] ;# Weak integer checking: allow empty string, empty sign, reject octals
 if {! $weakCheck} {set X $oldX}    ;# if weak check fails, continue with old value
 set strongCheck [expr {[string is int -strict $X] && ($X >= $min) && ($X <= $max)}] ;# Strong integer checking with range
 switch $event {
   key { $win configure -bg [expr {$strongCheck ? "SkyBlue1" : "yellow"}] ; return $weakCheck }
   focusout { if {! $strongCheck} {$win configure -bg red} ; return $strongCheck }
   default { return 1 } }
} ;# end of proc validInt

proc create_and_pack { } {
  wm title . "HVSys APD HV" ;
  if {$::demo} {
    if {[info exists ::conn]} {set txt "DEMO mode. No APD HV modules found on port $::portbasename$::portnum"} \
    else {set txt "DEMO mode. Can not open port $::portbasename$::portnum"}
    grid [label .demo -bg moccasin -text $txt -font {-size -18}] -sticky nswe;#-side top -expand 1 -fill both; }

  grid [label .lm -text "Cells" -font $::font]
  grid [frame .cells] -sticky nswe
  foreach c $::celllist {                                   ;# create buttons for detected cells
    grid [button .cells.$c -width 3 -bg white -relief raised -bd 3 -font $::font -text C$c] -sticky nsew -column $c -row 1 -padx 1
    grid columnconfigure .cells $c -weight 1
    bind .cells.$c <ButtonPress-1> [list newactivecell $c]  ;# change active cell on click
    }
 grid [frame .st -relief groove -bd 1] -sticky nswe;
 set ::lsup "Last Updated:\r ";
 pack [label .st.lsup -width 11 -font $::font -textvariable ::lsup -bg aquamarine -relief groove] -side left -expand 1 -fill both
 pack [checkbutton .st.tc  -width 12 -font $::font -bg PaleGreen2 -activebackground PaleGreen2 -relief groove -text "Temperature \rcompensation"] -side left -expand 1 -fill x
 pack [checkbutton .st.log -width 14 -text "Log to file" -bg lightgreen -activebackground lightgreen -font $::font -relief groove] -side left -expand 1 -fill both

 grid [frame .t -relief groove -bd 1] -sticky nswe; #pack .t -side top -fill both  -expand 1  -pady 3  ;# TEMPerature frame
 pack [label .t.b -width 14 -font $::font -bg SeaShell -activebackground SeaShell -relief raised -text "Ramp U/D"] -side left -expand 1 -fill both
 pack [entry .t.e -width 4 -textvariable ::activeRUDS -font $::font -bg white -relief groove \
    -validate all -vcmd {validInt %W %V %P %s 1 0xc8 } ] -side left -expand 1 -fill both
 bind  .t.e <KeyPress-Return>  {RUDentry_ret}             ;# set flag for writing and do some additional checks
 proc RUDentry_ret { } {    ;# Rump Up/Down speed set on Return pressed
   if {[string length $::activeRUDS]==0} {return}  ;#if entry is empty -> just do nothing and return
   if { $::activeRUDS<1 || $::activeRUDS>0xc8} {tk_messageBox -message "Value Out of Range" -icon warning; }
   .t.e configure -bg white ; set ::setRUDSfl 1; }
 pack [label .t.l -width 4 -font $::font -bg SeaShell -relief groove -textvariable ::activerdRUDS] -side left -expand 1 -fill both

 set ::TEMPSTR "TEMP (C)\r "
 pack [label .t.t -width 10 -font $::font -textvariable ::TEMPSTR -bg PaleGreen2 -relief groove] -side left -expand 1 -fill both
 pack [checkbutton .t.g -width 12 -font $::font -bg chocolate1 -activebackground chocolate1 -relief groove -text "HV Generator \rOn/Off"] -side left  -expand 1 -fill both
 bind .t.g <ButtonPress-1> {set ::setGENfl 1}

 grid [frame .p -relief groove -bd 1] -sticky nswe;# pack .p -side top -fill both  -expand 1  -pady 3   ;# Parameters frame

 grid [frame .h -relief groove -bd 1];# pack .h -side top -fill both  -expand 1  -pady 3   ;# Headers (titles) for channels frame
 pack [label .h.c -width 3 -font $::font -text "Ch.\r " -relief ridge] -side left
 pack [label .h.s -width 15 -font $::font -text "Set Voltage(V)\r @20C" -relief ridge] -side left
 pack [label .h.v -width 14 -font $::font -text "T Compensated\r Set Voltage" -relief ridge] -side left
 pack [label .h.m -width 10 -font $::font -text "Current\rVoltage(V) " -relief ridge] -side left
 pack [label .h.k -width 6 -font $::font -text "Kt\r(V/C)" -relief ridge] -side left -expand 1 -fill both
 pack [label .h.o -width 10 -font $::font -text "Output\rVoltage(V) " -relief ridge] -side left

 for {set n 0} {$n < $::nch} {incr n} {
   grid [frame .c$n -relief groove -bd 1] ;# pack .c$n -side top -fill both  -expand 1  -pady 1    ;# HV channels frames
   pack [label .c$n.c -width 3 -font $::font -text $n -relief ridge] -side left    ;# channel
   pack [spinbox .c$n.e -width 6 -textvariable ::activeSVE($n) -font $::font -bg white -relief ridge -command {%W configure -bg SkyBlue1}\
         -from $::Umin -to $::Umax($::activecell,$n) -increment $::ku($::activecell,$n) \
         -validate all -vcmd [list validReal %W %V %P %s $::Umin $::Umax($::activecell,$n) "SkyBlue1"]] -side left -padx 1 ;# Entry Set Voltage
   bind .c$n.e <KeyPress-Return> [list Uspinbox_ret $n]   ;# set flag for writing and do some formatting
   pack [label .c$n.s -width 6 -font $::font -text 0 -textvariable ::activeSV($n) -relief ridge] -side left -padx 2;# Set Voltage
   pack [label .c$n.cs -width 14 -font $::font -textvariable ::activeTCSV($n) -relief ridge] -side left;# Current Set Voltage
   pack [label .c$n.m -width 10 -font $::font -text 0 -textvariable ::activeMV($n) -relief ridge] -side left   ;# Measured Voltage
   pack [entry .c$n.k -width 6 -textvariable ::activeKT($n) -font $::font -bg white -relief ridge \
     -validate all -vcmd {validReal %W %V %P %s -1000 1000 "SkyBlue1"}] -side left -expand 1 -fill both  ;# Temperature Coefficient
   bind .c$n.k <KeyPress-Return> [list KT_ret $n]         ;# new KT
   set ::activeKT($n) 0
   pack [label .c$n.o -width 10 -font $::font -text 0 -textvariable ::activeOV($n) -relief ridge] -side left
  }
 .c10.c configure -text Ped; set ::activeOV([expr $::nch-1]) "Pedestal V";           ;# make special configuration on pedestal channel
 .c10.e configure -bg white;

 proc KT_ret { n } {                                  ;# new KT
   if {[string length $::activeKT($n)]==0} {return}   ;# if KT is empty -> just do nothing and return
   set ::KT($::activecell,$n) $::activeKT($n) 
   .c$n.k configure -bg white  }

 proc Uspinbox_ret { n } {    ;# set flag for writing and do some formatting
   if {[string length $::activeSVE($n)]==0} {return}  ;#if entry is empty -> just do nothing and return
   set ::activeSVE($n) [format "%.3f" [ expr round($::activeSVE($n)*1000)/1000.0 ]]       ;# round  $::activeSVE($n) to 0.01
   set ::SVE($::activecell,$n) $::activeSVE($n);
   set ::activeSV($n) $::activeSVE($n);
   .c$n.e configure -bg white ; set ::setUfl($n) 1; }

} ;# end of proc create_and_pack

proc get_initial_cells_state { } {                      ;# read once cell state on program start
  foreach c $::celllist {
    set ::gs($c) 0                                      ;# cell generator state
    set ::RUDS($c) 0                                    ;# Ramp up/down speed
    set ::ATEMP($c) 0                                   ;# Averaged 10 pts TEMPerature
    set ::TEMP($c) 0                                    ;# TEMPerature for log file
    for {set n 0} {$n < $::nch} {incr n} {
      set ::MV($c,$n) 0;  set ::KT($c,$n) 0; set ::SVE($c,$n) 0; set ::TCSV($c,$n) 0;
      set ::activeOV($n) 0; set ::activeTCSV($n) 0;  set ::Udacprev($c,$n) 0; }
  }
  foreach c $::celllist {
   # first check if GEN is ON
   cellreadstatus $c
   #if {$::debug} {puts "cellreadstatus=[string range $::reply 0 3]" };
   scan [string range $::reply 0 3 ] "%04x" aa                                ;# aa cell stat. reg
   if {[expr $aa&0x1]} {set ::gs($c) 1}                                       ;# indicate that GEN is ON from gen ctate massive
   cellreadrudtime $c;
   scan [string range $::reply 0 3 ] "%x" ::RUDS($c) ;# read back Up Down Time 
   cellreadVmax $c
   scan [string range $::reply 0 3 ] "%x" ::Vmax($c); set ::Vmax($c) [expr $::Vmax($c)/100.0] ;# read Umav from the cell
   cellreadPedVmax $c
   scan [string range $::reply 0 3 ] "%x" ::PedVmax($c); set ::PedVmax($c) [expr $::PedVmax($c)/100.0] ;# read PedUmav from the cell
   for {set n 0} {$n < $::nch} {incr n} {
     if {$n != [expr $::nch-1]} {set ::Umax($c,$n) $::Vmax($c);} else {set ::Umax($c,$n) $::PedVmax($c);}
     set ::ku($c,$n) [expr ($::Umax($c,$n)-$::Umin)/4095]                           ;# coefficient -> V=digits*ku

     cellreadchannelsetvalue $c $n;
     scan [string range $::reply 0 3] "%04x" ::SVE($c,$n)     ;# read Set Voltage from the channel -> display it on label and ...
     # next 2 arrays may be overwritten by ::activeSV($n) and ::activeSVE($n) from status file (if one exist)
     set ::SVE($c,$n) [format "%.3f" [expr $::SVE($c,$n)*$::ku($c,$n)]]  ;# convert it from bits to V
     }
   } ;# end of foreach cells list
  update; update idletasks
  wm title . "HVSys APD HV" ;# refresh title in case it was changed due to rs232 problems
}   ;# end of proc get_initial_cell_state

 proc newactivecell {nac} {
  .cells.$::activecell configure -fg black -font {-size 12 -weight normal -underline 0};
  .cells.$nac configure -fg blue -font {-size 14 -weight bold -underline 1} ; update
  set ::activecell $nac                                     ;# change active cell
  set ::g $::gs($nac)                                       ;# set gui variables to coresp. array values
  set ::activeRUDS $::RUDS($nac)
  set ::activerdRUDS $::RUDS($nac)
  set ::TEMPSTR "TEMP (C) \r[format "%4.2f" $::TEMP($nac)]"
  for {set n 0} {$n < $::nch} {incr n} {
    .c$n.e configure -bg white
    set ::activeSVE($n) $::SVE($nac,$n)
    set ::activeSV($n) $::activeSVE($n)
    set ::activeTCSV($n) $::TCSV($nac,$n) 
    set ::activeKT($n) $::KT($nac,$n)
    if {$n != [expr $::nch-1]} \
      {set ::activeOV($n) [format "%.3f" [expr $::MV($nac,$n)+$::MV($nac,[expr $::nch-1])]]
      set ::activeMV($n) [format "%.3f" $::MV($nac,$n)]
      }
    }
} ;# end of proc newactivecell

proc wsf { } {                                          ;# write status file on exit
  set sf [open apdhvctrl.st w]
  puts $sf "set ::tc $::tc"                             ;# write state of thermocompensation
  foreach c $::celllist {                               ;# for all detected cells
   for {set n 0} {$n < $::nch} {incr n} {
     puts $sf "set ::SVE($c,$n) $::SVE($c,$n)"          ;# U set values Entry
     puts $sf "set ::KT($c,$n) $::KT($c,$n)"            ;# write thermocompensation coefficients
     }
  }
}

proc wdf { } {                                          ;# write data/log file
  if {$::log && ![info exist ::df]} {
    set ::fname [clock format [clock seconds] -format %d%m%y_%H%M%S]; set ::df [open $::fname w]}
  if {!$::log && [info exist ::df]} {close $::df; unset ::df}
  if {$::log && [info exist ::df]} {
     puts -nonewline $::df "[clock seconds] $::tc"
     foreach c $::celllist {
      puts -nonewline $::df " [format "%.3f" $::TEMP($c)] "                                             ;# write Averaged Temp and state of thermocompensation
      for {set n 0} {$n < $::nch} {incr n} {puts -nonewline $::df " $::MV($c,$n)"}                      ;# Measured Value
      for {set n 0} {$n < $::nch} {incr n} {puts -nonewline $::df " [expr round($::Udacprev($c,$n))]"}  ;# Last value written to DAC
     }
    puts $::df ""; flush $::df;
  }
}

proc new_data { } {                                     ;# recursive - communicate to cell and put/get new data
  # Check setGENfl to do the job
  if { $::setGENfl } { set ::setGENfl 0                 ;# clear the flag first
    if {$::g} {cellgenon $::activecell} else {cellgenoff $::activecell} ;#switch  active cell gen corresp. checkbox state
    set ::gs($::activecell) $::g                        ;# store new gen state
    if {$::gs($::activecell)} {.cells.$::activecell configure -bg green -activebackground green} else {.cells.$::activecell configure -bg white -activebackground white}
    update
    }
 # check if we have to set some new settings in cell
 for {set n 0} {$n < $::nch} {incr n} {                 ;# Check flags to set (write U to) corresp. chanel
   if { $::setUfl($n) } { set ::setUfl($n) 0;
     set dacval [expr round($::SVE($::activecell,$n)/$::ku($::activecell,$n))]
     if {$dacval>$::dacmax} {set dacval $::dacmax};  if {$dacval<0} {set dacval 0};
     set ::activeSV($n) [format "%.3f" [expr $dacval*$::ku($::activecell,$n)]]  ;# trim SV to DAC bits and fill the corresponding entry
     cellwriteU $::activecell $n $dacval                ;# physically write new settings to the channel
     }
   }  ;# end of for { } setUfl
 # do we have to change Ramp Up/Down Speed?
 if { $::setRUDSfl } { set ::setRUDSfl 0                ;# clear the flag first
   cellwriterumpudspeed $::activecell;  set ::RUDS($::activecell) $::activeRUDS; set ::activerdRUDS $::RUDS($::activecell) }

 # read all channels voltages for active cell (to see RUP/DWN progress)
 for {set n 0} {$n < $::nch} {incr n} {
    cellreadcurrentchannelvalue $::activecell $n        ;# reread current channelsvalues
    if {[scan [string range $::reply 0 3] "%04x" val]==1} {             ;# read Voltage from the channel -> display it on label and ...
      set ::MV($::activecell,$n) [format "%.3f" [expr $val*$::ku($::activecell,$n)]]          ;# convert from real voltage to "set voltage" and ;# calculate sum of pedestal and channel V
      set ::activeMV($n) [format "%.3f" $::MV($::activecell,$n)]        ;# display MV for active cell
      if {$n != [expr $::nch-1]} {set ::activeOV($n) [format "%.3f" [expr $::MV($::activecell,$n)+$::MV($::activecell,[expr $::nch-1])]]}} \
    else {.cells.$::activecell configure -bg yellow; update; reperr $::activecell "er1"}         ;# blink yellow and report error
  }
 ##if {$::debug} {cellreadaddress $::activecell 0x40; puts "BV_repl=$::reply"  }
 ##if {$::debug} {cellreadtemperature $::activecell ; puts -nonewline "Tmes=$::reply"  }

 # now lets read status of channels (Gen, RUP?RDWN and Errors) for active cell
 cellreadstatus $::activecell
 if {[scan [string range $::reply 0 3 ] "%04x" aa]==1} {;# aa cell stat. reg
    ##if {$::debug} {puts "status_repl=$::reply"  }
    if {[expr $aa&0x1]} {set ::g 1}                        ;# indicate that GEN is ON
    set rumpreg [expr $aa&0x4];                            ;# rumping is actually one bit
    set errreg [expr ($aa>>3)&0x3ff]                       ;# 10 bits of errors
    for {set n 0} {$n < $::nch} {incr n} {
      .c$n.m configure -bg [expr {$rumpreg ? "burlywood3" : "grey"}] ;# show label in burlywood3 color if rampU/D is in progress
      .c$n.o configure -bg [expr {$rumpreg ? "burlywood3" : "grey"}] ;# show label in burlywood3 color if rampU/D is in progress
    if {[expr ($errreg>>$n)&1]} {.c$n.m configure -bg [expr {$::g ? "firebrick1" : "gold2"}] } };# RED(GEN ON) or Yellow(GEN OFF) on cell err
    } \
 else {.cells.$::activecell configure -bg yellow; update; reperr $::activecell "er2"}             ;# blink yellow and report error

 # lets read status of channels (RUP?RDWN and Errors) for ALL cells
 foreach c $::celllist {
    cellreadstatus $c
    if {[scan [string range $::reply 0 3 ] "%04x" aa]==1} { ;# aa cell stat. reg
      if {[expr $aa&0x1]} {.cells.$c configure -bg green -activebackground green} else {.cells.$c configure -bg white -activebackground white} ;# indicate that GEN is ON or OFF
##      set errreg [expr ($aa>>3)&0x3ff]                       ;# 10 bits of errors
      set errreg [expr $aa&0x2]                                 ;# overall error bit

      if {$errreg} {.cells.$c configure -bg [expr {$::gs($c) ? "firebrick1" : "white"}] } } \
    else {.cells.$c configure -bg yellow; update; reperr $::activecell "er3"}            ;# blink yellow and report error
 }

# read Temperature from all modules and calculate/fill corrected "current set voltages"
 foreach c $::celllist {
    cellreadtemperature $c
    if {[scan [string range $::reply 0 3] "%x" tmp]==1} {                                 ;# set tmp to readed raw hex temperature
      if {$::tempcnt==-1} { incr ::tempcnt; set ::TEMP($c) [expr -0.019*$tmp+66]
      if {$c==$::activecell} {set ::TEMPSTR "TEMP (C) \r[format "%4.2f" $::TEMP($c)]" }}  ;# first show up of TEMP after start
      set ::ATEMP($c) [expr $::ATEMP($c) + (-0.019*$tmp+66)]                                ;# keep summing Temperature values in ATEMP...
      } \
    else {.cells.$c configure -bg yellow; update; reperr $::activecell "er3"}            ;# blink yellow and report error
 };  # end foreach
 incr ::tempcnt;

 if { $::tempcnt == 10 } {
  set ::tempcnt 0;
  foreach c $::celllist {
    set ::TEMP($c) [expr $::ATEMP($c)/10]                                               ;# set averaged TEMP in grad C 
    if {$c==$::activecell} {set ::TEMPSTR "TEMP (C) \r[format "%4.2f" $::TEMP($c)]"}    ;# display averaged TEMP in grad C for the active cell
    for {set n 0} {$n < $::nch} {incr n} {
     
      set tmp [expr $::SVE($c,$n)+($::TEMP($c)-20)*$::KT($c,$n)0]                       ;#if field is empty -> multiply by 0
      if {$tmp<$::Umin} {set tmp $::Umin};      if {$tmp>$::Umax($c,$n)} {set tmp $::Umax($c,$n)};
      set ::TCSV($c,$n) [format "%.3f" [ expr round($tmp/$::ku($c,$n))*$::ku($c,$n) ]]  ;# round the value to 1 DAC bit
      if {$c==$::activecell} {set ::activeTCSV($n) $::TCSV($c,$n)}                      ;# display TCSV
     
      if {$::gs($c)} {                                                                  ;# if generator is ON
        if {$::tc} {
          set dacval [expr round($::TCSV($c,$n)/$::ku($c,$n))]                          ;# calculate DAC value if thermocompensation ON
        if {$dacval>$::dacmax} {set dacval $::dacmax};  if {$dacval<0} {set dacval 0};} \
        else {
          set dacval [expr round($::SVE($c,$n)/$::ku($c,$n))]                           ;# calculate DAC value if thermocompensation OFF
          if {$dacval>$::dacmax} {set dacval $::dacmax};  if {$dacval<0} {set dacval 0};
          };
        if {$::Udacprev($c,$n) != $dacval} {cellwriteU $c $n $dacval;}                  ;# and write it to cell if it is different from previous setting
      }
    } ;# end for {}
    set ::ATEMP($c) 0;
  }; # end foreach
 }; #end if $::tempcnt==10 
 update; update idletasks
 wdf;               ;# wtrite data/log file
 set ::lsup [clock format [clock seconds] -format "Last Updated:\r %H:%M:%S"]       ;#last updated label
 wm title . "HVSys APD HV cell=$::activecell  Umax=$::Umax($::activecell,0) Pedmax=$::Umax($::activecell,9)" ;# refresh title in case it was changed due to rs232 problems
 after 500 new_data
}     ;# end of proc new_data

# Cell communication subroutines
proc cellreadID { c } {for {set a 0} {$a<$::amax_id} {incr a} \
  {sputs [format "r%02x1c_\n" $c ] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}}      ;# read ID of the cell !!! NO reperr here for silent detection
proc cellreadstatus { c } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "r%02x00_\n" $c  ] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";}     ;# read status of the cell
proc cellreadrudtime { c } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "r%02x18_\n" $c  ] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";}     ;# read RUD time
proc cellreadVmax { c } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "r%02x38_\n" $c  ] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";}     ;# read calibration Vmax
proc cellreadPedVmax { c } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "r%02x3a_\n" $c  ] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";}     ;# read calibration PedVmax
proc cellreadchannelsetvalue {c n } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "r%02x%02x_\n" $c  [expr $n*2+2]] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";} ;# read cell channel
proc cellreadcurrentchannelvalue { c n } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "r%02x%02x_\n" $c  [expr $n*2+0x22]] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";} ;# read cell channel
proc cellreadaddress { c adr } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "r%02x%02x_\n" $c  $adr]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";} ;# read cell channel
proc cellwriteU {c n dacval} {
  for {set a 0} {$a<$::amax} {incr a} \
    {sputs [format "w%02x%02x%04x_\n" $c [expr ($n*2)+2] $dacval] ;if {[set ret [get_r232ch 6]]==0} {set ::Udacprev($c,$n) $dacval;return $ret;}; after 10;}
  reperr $c "";  
  };# write U to channel
proc cellgenon { c } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "w%02x000001_\n" $c ]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";}  ;# GEN On
proc cellgenoff { c } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "w%02x000000_\n" $c ]; if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";}  ;# GEN Off
proc cellwriterumpudspeed { c } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "w%02x18%04x_\n" $c  $::activeRUDS] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";} ;# Ramp Up/Down Speed;
proc cellreadtemperature { c } {for {set a 0} {$a<$::amax} {incr a} \
  {sputs [format "r%02x1a_\n" $c ] ;if {[set ret [get_r232ch 6]]==0} {return $ret;}; after 10;}; reperr $c "";}      ;# read Temperature from module

proc sputs {p1} {if {!$::demo} {puts -nonewline $::conn $p1}}  ;# wrap around puts

proc reperr {cell msg} {if {$::demo} {return}; puts $::ef "[clock format [clock seconds] -format "%H:%M:%S"] proc=[info level -1]; cell=$cell; $msg"; flush $::ef }                      ;# Report Error

#----------------------- MAIN --------------------------
init_vars                         ;# some global vars
set ::ef [open apdhvctrl.err a+]  ;# open errors log file
detectcell                        ;# find out the FIRST cell number
get_initial_cells_state           ;# read once cell state on program start
create_and_pack                   ;# create gui
if {[file exists apdhvctrl.st]} { ;# if status file exist ...
  source apdhvctrl.st}            ;# ... execute it
newactivecell $::activecell       ;# set active cell
new_data                          ;# recursive - communicate to cell and put/get new data

if {[file exists comp9cm_aux_cmds.tcl]} { ;# if comp9cm_aux_cmds.tcl file exist ...
  source comp9cm_aux_cmds.tcl}            ;# ... execute it
