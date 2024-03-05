from uvm.base.uvm_component import UVMComponent
from uvm.macros import uvm_component_utils
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW, UVM_MEDIUM 
from uvm.macros import uvm_component_utils, uvm_info
from uvm.tlm1.uvm_analysis_port import UVMAnalysisExport
from uvm.macros.uvm_tlm_defines import uvm_analysis_imp_decl
import cocotb
from EF_UVM.bus_env.bus_item import bus_bus_item

uvm_analysis_imp_bus = uvm_analysis_imp_decl("_bus")
uvm_analysis_imp_ip = uvm_analysis_imp_decl("_ip")
uvm_analysis_imp_ip_irq = uvm_analysis_imp_decl("_ip_irq")


class VIP(UVMComponent):
    """
    The VIP, or Verification IP, is a crucial element within the top-level verification environment, designed to validate the functionality and performance of both the IP (Intellectual Property) and the bus system. Its primary role is to act as a representative or mimic of the actual hardware components, including the IP and the bus. Key features and functions of the VIP include:
    1) Input Simulation: The VIP is capable of receiving the same inputs that would be provided to the actual IP and bus via connection with the monitors of the bus and IP.
    2) Functional Emulation: It emulates the behavior and responses of the IP and bus under test. By replicating the operational characteristics of these components, the VIP serves as a benchmark for expected performance and behavior.
    3) Output Generation: Upon receiving inputs, the VIP processes them in a manner akin to the real hardware, subsequently generating expected outputs. These outputs are essential for comparison in the verification process.
    4) Interface with Scoreboard: The outputs from the VIP, representing the expected results, are forwarded to the scoreboard. The scoreboard then compares these expected results with the actual outputs from the IP and bus for verification.
    5)Register Abstraction Layer (RAL) Integration: The VIP includes a RAL model that mirrors the register values of the RTL, ensuring synchronization between expected and actual register states. This model facilitates register-level tests and error detection, offering accessible and up-to-date register values for other verification components. It enhances the automation and coverage of register testing, playing a vital role in ensuring the accuracy and comprehensiveness of the verification process.
    """
    def __init__(self, name="VIP", parent=None):
        super().__init__(name, parent)
        self.analysis_imp_bus = uvm_analysis_imp_bus("vip_ap_bus", self)
        self.analysis_imp_ip = uvm_analysis_imp_ip("vip_ap_ip", self)
        self.bus_bus_export = UVMAnalysisExport("vip_bus_export", self)
        self.bus_irq_export = UVMAnalysisExport("vip_irq_export", self)
        self.ip_export = UVMAnalysisExport("vip_ip_export", self)
        self.analysis_imp_ip_irq = uvm_analysis_imp_ip_irq("vip_ap_ip_irq", self)
        self.model = None
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        pass

    def write_bus(self, tr):
        uvm_info(self.tag, "Vip write: " + tr.convert2string(), UVM_HIGH)
        pass

    def write_ip(self, tr):
        uvm_info(self.tag, "ip Vip write: " + tr.convert2string(), UVM_HIGH)
        pass


uvm_component_utils(VIP)
