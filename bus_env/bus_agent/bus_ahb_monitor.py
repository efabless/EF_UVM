from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info, uvm_error
from uvm.comps.uvm_monitor import UVMMonitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisPort
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from EF_UVM.bus_env.bus_item import bus_item
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW
import cocotb


class bus_ahb_monitor(UVMMonitor):
    def __init__(self, name="bus_ahb_monitor", parent=None):
        super().__init__(name, parent)
        self.monitor_port = UVMAnalysisPort("monitor_port", self)
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if (not UVMConfigDb.get(self, "", "bus_if", arr)):
            uvm_fatal(self.tag, "No interface specified for self driver instance")
        else:
            self.vif = arr[0]
        regs_arr = []
        if (not UVMConfigDb.get(self, "", "bus_regs", regs_arr)):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.regs = regs_arr[0]

    async def run_phase(self, phase):
        await cocotb.start(self.watch_reset())
        while True:
            tr = None
            # wait for a transaction
            address, is_write = await self.address_phase()
            data = await self.data_phase(is_write)
            tr = bus_item.type_id.create("tr", self)
            tr.kind = bus_item.WRITE if is_write else bus_item.READ
            tr.addr = address
            tr.data = data
            self.monitor_port.write(tr)
            # update reg value #TODO: move this to the ref_model later
            # self.regs.write_reg_value(tr.addr, tr.data)
            uvm_info(self.tag, "sampled AHB transaction: " + tr.convert2string(), UVM_HIGH)

    async def watch_reset(self):
        while True:
            await FallingEdge(self.vif.HRESETn)
            # send reset tr 
            tr = bus_item.type_id.create("tr", self)
            tr.kind = bus_item.RESET
            tr.addr = 0
            self.monitor_port.write(tr)
            uvm_info(self.tag, "sampled reset transaction: " + tr.convert2string(), UVM_HIGH)

    async def sample_delay(self):
        await RisingEdge(self.vif.HCLK)
        await Timer(1, "NS")

    async def address_phase(self):
        while True:
            await RisingEdge(self.vif.HCLK)
            if self.vif.HSEL.value.binstr == "1":
                if self.vif.HTRANS.value.binstr[0] == "1":
                    break
        address = self.vif.HADDR.value.integer
        write = self.vif.HWRITE.value.integer
        return address, write

    async def data_phase(self, is_write):
        # await self.sample_delay()
        await Timer(1, "NS")
        while self.vif.HREADYOUT.value == 0:
            await self.sample_delay()
        if is_write:
            data = self.vif.HWDATA.value.integer
        else:
            try:
                data = self.vif.HRDATA.value.integer
            except ValueError:
                uvm_error(self.tag, f"HRDATA is not an integer {self.vif.HRDATA.value.binstr}")
                data = self.vif.HRDATA.value.binstr
        return data


uvm_component_utils(bus_ahb_monitor)
