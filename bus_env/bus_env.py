from uvm.comps import UVMEnv
from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from EF_UVM.bus_env.bus_agent.bus_agent import bus_agent
from EF_UVM.bus_env.bus_coverage.bus_coverage import bus_coverage
from EF_UVM.bus_env.bus_logger.bus_logger import bus_logger
from uvm.tlm1.uvm_analysis_port import UVMAnalysisExport
from uvm.base.uvm_config_db import UVMConfigDb


class bus_env(UVMEnv):
    """
        The wrapperEnv is a specialized environment for verifying the bus system in an IP (Intellectual Property) design. This environment is structured to ensure comprehensive testing and validation of the bus interface, which could be of various types such as Wishbone, AHB, or APB. Its three main components are:
            Agent: At the core of the wrapperEnv is the agent, which includes both a driver and a monitor.
            Coverage Model: This component is closely linked with the monitor. It analyzes the outputs captured by the monitor to measure the extent of the test coverage.
            Logger Model: The logger model works in conjunction with the monitor to log activities and events in the bus system.
            It captures detailed logs of the transactions and interactions observed by the monitor.
    """
    def __init__(self, name="bus_env", parent=None):
        super().__init__(name, parent)
        self.coverage_comp = None
        self.logger_comp = None
        self.bus_agent = None
        self.bus_bus_export = UVMAnalysisExport("bus_bus_export", self)
        self.bus_irq_export = UVMAnalysisExport("bus_irq_export", self)

    def build_phase(self, phase):
        self.bus_agent = bus_agent.type_id.create("bus_agent", self)
        collect_cov = []
        if (not UVMConfigDb.get(self, "", "collect_coverage", collect_cov)):
            collect_cov = False
        else:
            collect_cov = collect_cov[0]
        if (collect_cov):
            self.coverage_comp = bus_coverage.type_id.create("bus_coverage", self)
        disable_logger = []
        if (not UVMConfigDb.get(self, "", "disable_logger", disable_logger)):
            disable_logger = False
        else:
            disable_logger = disable_logger[0]
        if not disable_logger:
            self.logger_comp = bus_logger.type_id.create("bus_logger", self)
        pass

    def connect_phase(self, phase):
        self.bus_agent.agent_bus_export.connect(self.bus_bus_export)
        self.bus_agent.agent_irq_export.connect(self.bus_irq_export)
        if self.coverage_comp is not None:
            self.bus_agent.agent_bus_export.connect(self.coverage_comp.analysis_imp_bus)
            self.bus_agent.agent_irq_export.connect(self.coverage_comp.analysis_imp_irq)
        if self.logger_comp is not None:
            self.bus_agent.agent_bus_export.connect(self.logger_comp.analysis_imp_bus)
        pass


uvm_component_utils(bus_env)
