from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info, uvm_error
from uvm.comps.uvm_monitor import UVMMonitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisPort
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item
from EF_UVM.bus_env.bus_agent.bus_base_monitor import bus_base_monitor

import cocotb


class bus_wb_monitor(bus_base_monitor):
    def __init__(self, name="bus_wb_monitor", parent=None):
        super().__init__(name, parent)

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if not UVMConfigDb.get(self, "", "bus_if", arr):
            uvm_fatal(self.tag, "No interface specified for self driver instance")
        else:
            self.vif = arr[0]
        regs_arr = []
        if not UVMConfigDb.get(self, "", "bus_regs", regs_arr):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.regs = regs_arr[0]

    async def run_phase(self, phase):
        await cocotb.start(self.watch_reset())
        while True:
            tr = None
            # wait for a transaction
            address, is_write, data = await self.recieve_transaction()
            tr = bus_item.type_id.create("tr", self)
            tr.kind = bus_item.WRITE if is_write else bus_item.READ
            tr.addr = address
            tr.data = data
            self.monitor_port.write(tr)
            # update reg value #TODO: move this to the ref_model later
            # self.regs.write_reg_value(tr.addr, tr.data)
            uvm_info(
                self.tag, "sampled AHB transaction: " + tr.convert2string(), UVM_HIGH
            )

    async def watch_reset(self):
        while True:
            await FallingEdge(self.vif.RESETn)
            # send reset tr
            tr = bus_item.type_id.create("tr", self)
            tr.kind = bus_item.RESET
            tr.addr = 0
            self.monitor_port.write(tr)
            uvm_info(
                self.tag, "sampled reset transaction: " + tr.convert2string(), UVM_HIGH
            )

    async def sample_delay(self):
        await RisingEdge(self.vif.CLK)
        await Timer(1, "NS")

    async def recieve_transaction(self):
        while True:
            await self.sample_delay()
            if (
                self.vif.cyc_i.value.binstr == "1"
                and self.vif.stb_i.value.binstr == "1"
            ):
                break
        while self.vif.ack_o.value == 0:
            await self.sample_delay()
        address = self.vif.adr_i.value.integer
        write = self.vif.we_i.value.integer
        if write:
            data = self.vif.dat_i.value.integer
        else:
            try:
                data = self.vif.dat_o.value.integer
            except ValueError:
                uvm_error(
                    self.tag, f"HRDATA is not an integer {self.vif.dat_o.value.binstr}"
                )
                data = self.vif.dat_o.value.binstr
        return address, write, data


uvm_component_utils(bus_wb_monitor)
