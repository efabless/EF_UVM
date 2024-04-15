set clock_port $::env(CLK_MAKEFILE)
set clock_period 10
set reset_port $::env(RST_MAKEFILE) 


set clk_input [get_port $clock_port]
create_clock $clk_input -name $clock_port -period $clock_period

# IO_DELAY_CONSTRAINT = 30
set input_delay_value [expr $clock_period * $::env(IO_DELAY_CONSTRAINT) / 100] 
set output_delay_value [expr $clock_period * $::env(IO_DELAY_CONSTRAINT) / 100]


set clk_indx [lsearch [all_inputs] $clk_input]
set all_inputs_wo_clk [lreplace [all_inputs] $clk_indx $clk_indx ""]

set rst_input [get_port $reset_port]
set rst_indx [lsearch [all_inputs] $rst_input]
set all_inputs_wo_clk_rst [lreplace $all_inputs_wo_clk $rst_indx $rst_indx ""]
set_false_path -from $rst_input 

# correct resetn
set clocks [get_clocks $clock_port]

set_input_delay $input_delay_value -clock $clocks $all_inputs_wo_clk_rst
set_output_delay $output_delay_value -clock $clocks [all_outputs]

if { ![info exists ::env(SYNTH_CLK_DRIVING_CELL)] } {
    set ::env(SYNTH_CLK_DRIVING_CELL) $::env(SYNTH_DRIVING_CELL)
}

set_driving_cell \
    -lib_cell [lindex [split $::env(SYNTH_DRIVING_CELL) "/"] 0] \
    -pin [lindex [split $::env(SYNTH_DRIVING_CELL) "/"] 1] \
    $all_inputs_wo_clk_rst

set_driving_cell \
    -lib_cell [lindex [split $::env(SYNTH_CLK_DRIVING_CELL) "/"] 0] \
    -pin [lindex [split $::env(SYNTH_CLK_DRIVING_CELL) "/"] 1] \
    $clk_input

set cap_load [expr $::env(OUTPUT_CAP_LOAD) / 1000.0]
set_load $cap_load [all_outputs]
