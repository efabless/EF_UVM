import cocotb
from uvm.comps import UVMTest
from uvm import UVMCoreService
from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.base.uvm_config_db import UVMConfigDb
from uvm.base.uvm_printer import UVMTablePrinter
from uvm.base.sv import sv
from uvm.base.uvm_object_globals import UVM_FULL, UVM_LOW, UVM_ERROR
from EF_UVM.top_env import top_env
from uvm.base.uvm_report_server import UVMReportServer

# override bus classes
from EF_UVM.bus_env.bus_agent.bus_ahb_driver import bus_ahb_driver
from EF_UVM.bus_env.bus_agent.bus_apb_driver import bus_apb_driver
from EF_UVM.bus_env.bus_agent.bus_wb_driver import bus_wb_driver
from EF_UVM.bus_env.bus_agent.bus_ahb_monitor import bus_ahb_monitor
from EF_UVM.bus_env.bus_agent.bus_apb_monitor import bus_apb_monitor
from EF_UVM.bus_env.bus_agent.bus_wb_monitor import bus_wb_monitor

from EF_UVM.bus_env.bus_seq_lib.reset_bus_seq import reset_bus_seq
from EF_UVM.bus_env.bus_seq_lib.delays_bus_bg_seq import delays_bus_bg_seq
from cocotb.triggers import Event
from abc import abstractmethod


class base_test(UVMTest):
    def __init__(self, name="base_test", bus_type="AHB", parent=None):
        super().__init__(name, parent)
        self.test_pass = True
        self.top_env = None
        self.printer = None
        self.bus_type = bus_type

    def build_phase(self, phase):
        super().build_phase(phase)
        if self.bus_type == "AHB":
            self.set_type_override_by_type(
                bus_apb_driver.get_type(), bus_ahb_driver.get_type()
            )
            self.set_type_override_by_type(
                bus_apb_monitor.get_type(), bus_ahb_monitor.get_type()
            )
        elif self.bus_type == "WISHBONE":
            self.set_type_override_by_type(
                bus_apb_driver.get_type(), bus_wb_driver.get_type()
            )
            self.set_type_override_by_type(
                bus_apb_monitor.get_type(), bus_wb_monitor.get_type()
            )
        elif self.bus_type == "APB":
            pass
        else:
            uvm_fatal("BUS_TYPE", "Passed unsupported bus type " + self.bus_type)
        # Enable transaction recording for everything
        UVMConfigDb.set(self, "*", "recording_detail", UVM_FULL)
        # Create the tb
        self.top_env = top_env.type_id.create("top_env", self)
        # Create a specific depth printer for printing the created topology
        self.printer = UVMTablePrinter()
        self.printer.knobs.depth = -1

        arr = []
        if UVMConfigDb.get(None, "*", "ip_if", arr) is True:
            UVMConfigDb.set(self, "*", "ip_if", arr[0])
        else:
            uvm_fatal("NOVIF", "Could not get ip_if from config DB")

        if UVMConfigDb.get(None, "*", "bus_if", arr) is True:
            UVMConfigDb.set(self, "*", "bus_if", arr[0])
        else:
            uvm_fatal("NOVIF", "Could not get bus_if from config DB")
        # set max number of uvm errors
        server = UVMReportServer()
        server.set_max_quit_count(3)  # set maximum count of uvm_error before quitting
        UVMCoreService.get().set_report_server(server)

    def end_of_elaboration_phase(self, phase):
        # Set verbosity for the bus monitor for this demo
        uvm_info(
            self.get_type_name(),
            sv.sformatf("Printing the test topology :\n%s", self.sprint(self.printer)),
            UVM_LOW,
        )

    def update_min_checkers(self, num_checkers):
        """update min number of checker the scoreboard should have done for the tests
        the default is 50
        """
        self.top_env.scoreboard.update_min_checkers(num_checkers)
        # TODO: try this again not working

    def start_of_simulation_phase(self, phase):
        self.bus_sqr = self.top_env.bus_env.bus_agent.bus_sequencer
        self.ip_sqr = self.top_env.ip_env.ip_agent.ip_sequencer

    async def reset_phase(self, phase):
        phase.raise_objection(self, f"{self.__class__.__name__} reset phase OBJECTED ")
        bus_seq = reset_bus_seq("reset_bus_seq")
        uvm_info(self.get_type_name(), "reset_phase test", UVM_LOW)
        await bus_seq.start(self.bus_sqr)
        phase.drop_objection(
            self, f"{self.__class__.__name__} reset phase drop objection"
        )

    # remove background sequences as it introduce errors in the cases of ahbl
    # async def configure_phase(self, phase):
    #     # add background sequences
    #     await super().configure_phase(phase)
    #     bus_seq = delays_bus_bg_seq("delays_bus_bg_seq")
    #     await bus_seq.start(self.bus_sqr)

    @abstractmethod
    async def main_phase(self, phase):
        pass

    def extract_phase(self, phase):
        super().check_phase(phase)
        server = UVMCoreService.get().get_report_server()
        errors = server.get_severity_count(UVM_ERROR)
        if errors > 0:
            uvm_fatal(
                "FOUND ERRORS", "There were " + str(errors) + " UVM_ERRORs in the test"
            )

    def report_phase(self, phase):
        uvm_info(self.get_type_name(), "report_phase", UVM_LOW)
        if self.test_pass:
            uvm_info(self.get_type_name(), "** UVM TEST PASSED **", UVM_LOW)
        else:
            uvm_fatal(self.get_type_name(), "** UVM TEST FAIL **\n" + self.err_msg)


uvm_component_utils(base_test)
