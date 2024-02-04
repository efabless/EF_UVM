from uvm.macros import uvm_component_utils, uvm_fatal
from uvm.comps.uvm_monitor import UVMMonitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisPort
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW, UVM_MEDIUM


class ip_monitor(UVMMonitor):
    def __init__(self, name="ip_monitor", parent=None):
        super().__init__(name, parent)
        self.tag = name
        self.monitor_port = UVMAnalysisPort("monitor_port", self)
        self.monitor_irq_port = UVMAnalysisPort("monitor_irq_port", self)

    async def run_phase(self, phase):
        uvm_fatal(self.tag, "please write your monitor for the ip and replace it in the test")


uvm_component_utils(ip_monitor)
