from uvm.comps.uvm_agent import UVMAgent
from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from EF_UVM.bus_env.bus_agent.bus_sequencer import bus_sequencer
from EF_UVM.bus_env.bus_agent.bus_apb_driver import bus_apb_driver
from EF_UVM.bus_env.bus_agent.bus_apb_monitor import bus_apb_monitor
from EF_UVM.bus_env.bus_agent.bus_irq_monitor import bus_irq_monitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisExport
from uvm.base.uvm_config_db import UVMConfigDb


class bus_agent(UVMAgent):
    """
    The bus_agent is an essential component of the wrapperEnv, specifically designed to facilitate the verification of the bus system in an IP (Intellectual Property) design. It plays a critical role in ensuring that the bus, which could be of various types such as Wishbone, AHB, or APB, operates according to its specifications and interfaces effectively with the IP. The bus_agent consists of several key sub-components:
        Driver: This sub-component is responsible for generating and driving bus transaction scenarios. It simulates various operational conditions to test the bus's functionality, including:
        Generating diverse data patterns and control sequences to challenge the bus system.
        Monitor: The monitor in the bus_agent has a critical role in verifying the bus's adherence to its specific protocol standards. It ensures that all bus activities, including data transfers and control signal interactions, comply with the protocol specifications such as Wishbone, AHB, or APB.
        The monitor observes and captures the bus activities to provide insights into its operational compliance and performance, ensuring that the bus behaves as expected under various test conditions.
        Sequencer (if present): Coordinates the sequence of test operations, enabling the creation of complex scenarios that effectively test the bus system in real-world-like conditions.
    """
    def __init__(self, name="bus_agent", parent=None):
        super().__init__(name, parent)
        self.tag = name
        self.bus_sequencer = None
        self.driver = None
        self.bus_monitor = None
        self.irq_monitor = None
        self.agent_bus_export = UVMAnalysisExport("agent_bus_export", self)
        self.agent_irq_export = UVMAnalysisExport("agent_irq_export", self)

    def build_phase(self, phase):
        self.bus_sequencer = bus_sequencer.type_id.create("bus_sequencer", self)
        self.driver = bus_apb_driver.type_id.create("bus_apb_driver", self)
        self.bus_monitor = bus_apb_monitor.type_id.create("bus_apb_monitor", self)
        arr = []
        if (not UVMConfigDb.get(self, "", "irq_exist", arr)):
            uvm_fatal(self.tag, "No info about irq exists in config DB")
        else:
            irq_exist = arr[0]
        if irq_exist:
            self.irq_monitor = bus_irq_monitor.type_id.create("bus_irq_monitor", self)

    def connect_phase(self, phase):
        self.driver.seq_item_port.connect(self.bus_sequencer.seq_item_export)
        self.bus_monitor.monitor_port.connect(self.agent_bus_export)
        if self.irq_monitor is not None:
            self.irq_monitor.monitor_port.connect(self.agent_irq_export)
        pass


uvm_component_utils(bus_agent)
