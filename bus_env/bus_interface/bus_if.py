from uvm.base.sv import sv_if


class bus_apb_if(sv_if):
    #  // Actual Signals
    # wire 		PCLK;
    # wire 		PRESETn;
    # wire [31:0]	PADDR;
    # wire 		PWRITE;
    # wire 		PSEL;
    # wire 		PENABLE;
    # wire [31:0]	PWDATA;
    # wire [31:0]	PRDATA;
    # wire 		PREADY;
    # wire 		irq;

    def __init__(self, dut):
        bus_map = {
            "CLK": "CLK",
            "RESETn": "RESETn",
            "PADDR": "PADDR",
            "PWRITE": "PWRITE",
            "PSEL": "PSEL",
            "PENABLE": "PENABLE",
            "PWDATA": "PWDATA",
            "PRDATA": "PRDATA",
            "PREADY": "PREADY",
        }
        sv_if.__init__(self, dut, "", bus_map)


class bus_ahb_if(sv_if):
    #  // Actual Signals
    # wire 		PCLK;
    # wire 		PRESETn;
    # wire [31:0]	PADDR;
    # wire 		PWRITE;
    # wire 		PSEL;
    # wire 		PENABLE;
    # wire [31:0]	PWDATA;
    # wire [31:0]	PRDATA;
    # wire 		PREADY;
    # wire 		irq;

    def __init__(self, dut):
        bus_map = {
            "CLK": "CLK",
            "RESETn": "RESETn",
            "HADDR": "HADDR",
            "HWRITE": "HWRITE",
            "HSEL": "HSEL",
            "HREADYOUT": "HREADYOUT",
            "HTRANS": "HTRANS",
            "HWDATA": "HWDATA",
            "HRDATA": "HRDATA",
            "HREADY": "HREADY",
        }
        # optional_signals = dict() 
        # if "HSIZE" in dut._sub_handles:
        optional_signals = {"HSIZE": "HSIZE"}  # optional_signals
        sv_if.__init__(self, dut, "", bus_map, optional_signals=optional_signals)


class bus_wb_if(sv_if):
    def __init__(self, dut):
        bus_map = {
            "CLK": "CLK",
            "RESETn": "RESETn",
            "adr_i": "adr_i",
            "dat_i": "dat_i",
            "dat_o": "dat_o",
            "sel_i": "sel_i",
            "cyc_i": "cyc_i",
            "stb_i": "stb_i",
            "ack_o": "ack_o",
            "we_i": "we_i",
        }
        sv_if.__init__(self, dut, "", bus_map)


class bus_irq_if(sv_if):
    #  // Actual Signals
    # wire 		irq;

    def __init__(self, dut):
        bus_map = {"irq": "irq"}
        sv_if.__init__(self, dut, "", bus_map)
