`timescale 1ns/1ps

module top();
    reg 		CLK = 0;
    wire 		RESETn = 1;
    wire 		irq;
    // TODO: Add any IP signals here
    `ifdef BUS_TYPE_APB
        wire [31:0]	PADDR;
        wire 		PWRITE;
        wire 		PSEL;
        wire 		PENABLE;
        wire [31:0]	PWDATA;
        wire [31:0]	PRDATA;
        wire 		PREADY;
        // TODO: initialize the ABP wrapper here
        // for example
        // EF_skeleton_APB dut(.PCLK(CLK), .PRESETn(RESETn), .PADDR(PADDR), .PWRITE(PWRITE), .PSEL(PSEL), .PENABLE(PENABLE), .PWDATA(PWDATA), .PRDATA(PRDATA), .PREADY(PREADY), .IRQ(irq));
    `endif // BUS_TYPE_APB
    `ifdef BUS_TYPE_AHB
        wire [31:0]	HADDR;
        wire 		HWRITE;
        wire 		HSEL = 0;
        wire 		HREADYOUT;
        wire [1:0]	HTRANS=0;
        wire [31:0]	HWDATA;
        wire [31:0]	HRDATA;
        wire 		HREADY;
        // TODO: initialize the AHB wrapper here
        // for example
        // EF_skeleton_AHBL dut(.HCLK(CLK), .HRESETn(RESETn), .HADDR(HADDR), .HWRITE(HWRITE), .HSEL(HSEL), .HTRANS(HTRANS), .HWDATA(HWDATA), .HRDATA(HRDATA), .HREADY(HREADY),.HREADYOUT(HREADYOUT), .IRQ(irq));
    `endif // BUS_TYPE_AHB
    `ifdef BUS_TYPE_WISHBONE
        wire [31:0] adr_i;
        wire [31:0] dat_i;
        wire [31:0] dat_o;
        wire [3:0]  sel_i;
        wire        cyc_i;
        wire        stb_i;
        reg         ack_o;
        // TODO: initialize the Wishbone wrapper here
        // for example
        // EF_skeleton_WB dut(.clk_i(CLK), .rst_i(~RESETn), .adr_i(adr_i), .dat_i(dat_i), .dat_o(dat_o), .sel_i(sel_i), .cyc_i(cyc_i), .stb_i(stb_i), .ack_o(ack_o), .we_i(we_i), .irq(irq));
    `endif // BUS_TYPE_WISHBONE
    // monitor inside signals
    `ifndef SKIP_WAVE_DUMP
        initial begin
            $dumpfile ({"waves.vcd"});
            $dumpvars(0, top);
        end
    `endif
    always #10 CLK = !CLK; // clk generator
endmodule