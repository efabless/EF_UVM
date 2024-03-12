from uvm.macros import uvm_component_utils, uvm_fatal
from uvm.comps.uvm_monitor import UVMMonitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisPort
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW, UVM_MEDIUM
from uvm.base.uvm_config_db import UVMConfigDb


class ip_monitor(UVMMonitor):
    def __init__(self, name="ip_monitor", parent=None):
        super().__init__(name, parent)
        self.tag = name
        self.monitor_port = UVMAnalysisPort("monitor_port", self)
        self.monitor_irq_port = UVMAnalysisPort("monitor_irq_port", self)

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if (not UVMConfigDb.get(self, "", "ip_if", arr)):
            uvm_fatal(self.tag, "No interface specified for self monitor instance")
        else:
            self.vif = arr[0]
        regs_arr = []
        if (not UVMConfigDb.get(self, "", "bus_regs", regs_arr)):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.regs = regs_arr[0]


    async def run_phase(self, phase):
        uvm_fatal(self.tag, "please write your monitor for the ip and replace it in the test")


uvm_component_utils(ip_monitor)
