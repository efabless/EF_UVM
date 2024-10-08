from uvm.base.uvm_component import UVMComponent
from uvm.macros import uvm_component_utils
from uvm.tlm1.uvm_analysis_port import UVMAnalysisImp
from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW
from EF_UVM.bus_env.bus_coverage.bus_cov_groups import bus_cov_groups
from uvm.base.uvm_config_db import UVMConfigDb
from uvm.macros.uvm_tlm_defines import uvm_analysis_imp_decl

uvm_analysis_imp_bus = uvm_analysis_imp_decl("_bus")
uvm_analysis_imp_irq = uvm_analysis_imp_decl("_irq")


class bus_coverage(UVMComponent):
    """
    component that initialize the coverage groups and control when to sample the data.
    """

    def __init__(self, name="bus_coverage", parent=None):
        super().__init__(name, parent)
        self.analysis_imp_bus = uvm_analysis_imp_bus("analysis_imp_bus", self)
        self.analysis_imp_irq = uvm_analysis_imp_irq("analysis_imp_irq", self)
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if not UVMConfigDb.get(self, "", "bus_regs", arr):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.regs = arr[0]

        self.cov_groups = bus_cov_groups(
            "top.wrapper", self.regs, self.regs.get_irq_exist()
        )

    def write_bus(self, tr):
        uvm_info(self.tag, "get bus coverage for " + tr.convert2string(), UVM_HIGH)
        self.cov_groups.bus_cov(tr)
        pass

    def write_irq(self, tr):
        uvm_info(self.tag, "get irq coverage for " + tr.convert2string(), UVM_HIGH)
        self.cov_groups.irq_cov(tr)
        pass


uvm_component_utils(bus_coverage)
