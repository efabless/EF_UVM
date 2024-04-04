from uvm.base.uvm_component import UVMComponent
from uvm.macros import uvm_component_utils
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW, UVM_MEDIUM
from uvm.macros import uvm_component_utils, uvm_info, uvm_fatal
from uvm.tlm1.uvm_analysis_port import UVMAnalysisExport
from uvm.macros.uvm_tlm_defines import uvm_analysis_imp_decl
import cocotb
from EF_UVM.bus_env.bus_item import bus_item
from uvm.base.uvm_config_db import UVMConfigDb

uvm_analysis_imp_bus = uvm_analysis_imp_decl("_bus")
uvm_analysis_imp_ip = uvm_analysis_imp_decl("_ip")
uvm_analysis_imp_ip_irq = uvm_analysis_imp_decl("_ip_irq")


class ref_model(UVMComponent):
    """
    The reference model or Verification IP, is a crucial element within the top-level verification environment, designed to validate the functionality and performance of both the IP (Intellectual Property) and the bus system. Its primary role is to act as a representative or mimic of the actual hardware components, including the IP and the bus. Key features and functions of the  include:
    1) Input Simulation: The  is capable of receiving the same inputs that would be provided to the actual IP and bus via connection with the monitors of the bus and IP.
    2) Functional Emulation: It emulates the behavior and responses of the IP and bus under test. By replicating the operational characteristics of these components, the  serves as a benchmark for expected performance and behavior.
    3) Output Generation: Upon receiving inputs, the  processes them in a manner akin to the real hardware, subsequently generating expected outputs. These outputs are essential for comparison in the verification process.
    4) Interface with Scoreboard: The outputs from the , representing the expected results, are forwarded to the scoreboard. The scoreboard then compares these expected results with the actual outputs from the IP and bus for verification.
    5)Register Abstraction Layer (RAL) Integration: The  includes a RAL model that mirrors the register values of the RTL, ensuring synchronization between expected and actual register states. This model facilitates register-level tests and error detection, offering accessible and up-to-date register values for other verification components. It enhances the automation and coverage of register testing, playing a vital role in ensuring the accuracy and comprehensiveness of the verification process.
    """

    def __init__(self, name="", parent=None):
        super().__init__(name, parent)
        self.analysis_imp_bus = uvm_analysis_imp_bus("_ap_bus", self)
        self.analysis_imp_ip = uvm_analysis_imp_ip("_ap_ip", self)
        self.bus_bus_export = UVMAnalysisExport("_bus_export", self)
        self.bus_irq_export = UVMAnalysisExport("_irq_export", self)
        self.ip_export = UVMAnalysisExport("_ip_export", self)
        self.analysis_imp_ip_irq = uvm_analysis_imp_ip_irq("_ap_ip_irq", self)
        self.model = None
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if not UVMConfigDb.get(self, "", "bus_regs", arr):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.regs = arr[0]

    def user_write_bus(self, tr):
        uvm_info(self.tag, " write: " + tr.convert2string(), UVM_HIGH)
        pass

    def write_ip(self, tr):
        uvm_info(self.tag, "ip  write: " + tr.convert2string(), UVM_HIGH)
        pass


uvm_component_utils(ref_model)
