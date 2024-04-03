from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info, uvm_error
from uvm.comps.uvm_monitor import UVMMonitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisPort
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item
from EF_UVM.bus_env.bus_agent.bus_base_monitor import bus_base_monitor

import cocotb


class bus_apb_monitor(bus_base_monitor):
    def __init__(self, name="bus_apb_monitor", parent=None):
        super().__init__(name, parent)

    async def run_phase(self, phase):
        await cocotb.start(self.watch_reset())
        while True:
            tr = None
            # wait for a transaction
            while True:
                await self.sample_delay()
                if (
                    self.vif.PSEL.value.binstr == "1"
                    and self.vif.PENABLE.value.binstr == "0"
                ):
                    break
            tr = bus_item.type_id.create("tr", self)
            tr.kind = bus_item.WRITE if self.vif.PWRITE.value == 1 else bus_item.READ
            tr.addr = self.vif.PADDR.value.integer
            await self.sample_delay()
            if self.vif.PENABLE.value.binstr != "1":
                uvm_error(
                    self.tag,
                    f"APB protocol violation: SETUP cycle not followed by ENABLE cycle PENABLE={self.vif.PENABLE.value.binstr}",
                )
            if tr.kind == bus_item.WRITE:
                tr.data = self.vif.PWDATA.value.integer
            else:
                try:
                    tr.data = self.vif.PRDATA.value.integer
                except ValueError:
                    uvm_error(
                        self.tag,
                        f"PRDATA is not an integer {self.vif.PRDATA.value.binstr}",
                    )
                    tr.data = self.vif.PRDATA.value.binstr
            self.monitor_port.write(tr)
            # update reg value #TODO: move this to the ref_model later
            # self.regs.write_reg_value(tr.addr, tr.data)
            uvm_info(
                self.tag, "sampled APB transaction: " + tr.convert2string(), UVM_HIGH
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
        # await Timer(1, "NS")


uvm_component_utils(bus_apb_monitor)
