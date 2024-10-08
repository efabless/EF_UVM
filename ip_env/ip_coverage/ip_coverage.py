from uvm.base.uvm_component import UVMComponent
from uvm.macros import uvm_component_utils
from uvm.tlm1.uvm_analysis_port import UVMAnalysisImp
from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info, uvm_warning
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW
from uvm.base.uvm_config_db import UVMConfigDb
from uvm.macros.uvm_tlm_defines import uvm_analysis_imp_decl


class ip_coverage(UVMComponent):
    """
    component that initialize the coverage groups and control when to sample the data.
    """

    def __init__(self, name="ip_coverage", parent=None):
        super().__init__(name, parent)
        self.analysis_imp = UVMAnalysisImp("cov_ap", self)
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        uvm_warning(
            self.tag,
            "please implement your coverage model for the ip and replace it in the test",
        )


uvm_component_utils(ip_coverage)
