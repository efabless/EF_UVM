from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info, uvm_error
from uvm.comps.uvm_monitor import UVMMonitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisPort
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from EF_UVM.bus_env.bus_item import bus_item
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW
import cocotb


class bus_base_monitor(UVMMonitor):
    def __init__(self, name="base_monitor", parent=None):
        super().__init__(name, parent)
        self.monitor_port = UVMAnalysisPort("monitor_port", self)
        self.tag = name

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

    async def reset_phase(self, phase):
        uvm_info(self.tag, "Resetting", UVM_LOW)

    def end_of_elaboration_phase(self, phase):
        super().end_of_elaboration_phase(phase)
        self.regs.set_clock(self.vif.CLK)
        uvm_info(self.tag, "Clock set", UVM_LOW)
