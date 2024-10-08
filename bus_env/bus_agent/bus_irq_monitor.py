from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.comps.uvm_monitor import UVMMonitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisPort
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Edge, Timer
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_irq_item


class bus_irq_monitor(UVMMonitor):
    def __init__(self, name="bus_irq_monitor", parent=None):
        super().__init__(name, parent)
        self.monitor_port = UVMAnalysisPort("bus_irq_monitor", self)
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if not UVMConfigDb.get(self, "", "bus_irq_if", arr):
            uvm_fatal(self.tag, "No interface specified for self driver instance")
        else:
            self.vif = arr[0]

    async def run_phase(self, phase):
        if self.vif.irq.value.binstr not in ["1", "0"]:  # ignore transition from x to 0
            await Edge(self.vif.irq)
            await Timer(1, "NS")
        while True:
            tr = None
            await Edge(self.vif.irq)
            tr = bus_irq_item.type_id.create("tr", self)
            if self.vif.irq == 1:
                tr.trg_irq = 1
            else:
                tr.trg_irq = 0
            self.monitor_port.write(tr)
            uvm_info(
                self.tag, "sampled IRQ transaction: " + tr.convert2string(), UVM_HIGH
            )


uvm_component_utils(bus_irq_monitor)
