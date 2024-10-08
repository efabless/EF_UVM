from uvm.comps import UVMEnv
from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from EF_UVM.ip_env.ip_env import ip_env
from EF_UVM.bus_env.bus_env import bus_env
from EF_UVM.ref_model.ref_model import ref_model
from EF_UVM.scoreboard import scoreboard


class top_env(UVMEnv):
    """
    This class is the top-level verification environment for any IP (Intellectual Property) that is encapsulated by a bus created using the efabless wrapper generation script. The structure of the verification environment should be similar for all IPs, resulting in significant commonalities across different environments. The top level comprises four main components:
        1)wrapperEnv: This is the verification environment for the bus, which could be of types like Wishbone, AHB, or APB.
        2)ipEnv: This refers to the verification environment specific to the IP, covering a range of IPs such as UART, SPI, DDR RAM, AES, among others.
        3)ref_model (Verification IP): This component mimics the functionality of both the IP and the bus. It takes the same inputs as the IP and the bus and is expected to generate the corresponding outputs.
        4)Scoreboard: This is used to compare the outputs from the ref_model (which are the expected outputs) with the actual outputs from the IP and bus.
    The Top-Level Environment is responsible for initializing these components and ensuring they are correctly connected.
    """

    def __init__(self, name="env", parent=None):
        super().__init__(name, parent)
        self.ip_env = None
        self.bus_env = None
        self.ref_model = None
        self.scoreboard = None

    def build_phase(self, phase):
        self.ip_env = ip_env.type_id.create("ip_env", self)
        self.bus_env = bus_env.type_id.create("bus_env", self)
        self.ref_model = ref_model.type_id.create("ref_model", self)
        self.scoreboard = scoreboard.type_id.create("scoreboard", self)

    def connect_phase(self, phase):
        """
        Connect the scoreboard  with the bus and ip environment.
        Connect the scorebord with  the ref_model.
        Connect the ref_model with bus and ip environment monitors.
        """
        self.bus_env.bus_bus_export.connect(self.ref_model.analysis_imp_bus)
        self.ip_env.ip_env_export.connect(self.ref_model.analysis_imp_ip)
        self.ip_env.ip_env_irq_export.connect(self.ref_model.analysis_imp_ip_irq)
        # scoreboard connection
        self.bus_env.bus_bus_export.connect(self.scoreboard.analysis_imp_bus)
        self.bus_env.bus_irq_export.connect(self.scoreboard.analysis_imp_irq)
        self.ip_env.ip_env_export.connect(self.scoreboard.uvm_analysis_imp_ip)
        self.ref_model.bus_bus_export.connect(
            self.scoreboard.analysis_imp_bus_ref_model
        )
        self.ref_model.bus_irq_export.connect(
            self.scoreboard.analysis_imp_irq_ref_model
        )
        self.ref_model.ip_export.connect(self.scoreboard.uvm_analysis_imp_ip_ref_model)
        pass


uvm_component_utils(top_env)
