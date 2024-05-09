from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.comps.uvm_driver import UVMDriver
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import RisingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_MEDIUM, UVM_LOW, UVM_DEBUG
from abc import abstractmethod
import cocotb


class bus_base_driver(UVMDriver):
    def __init__(self, name="bus_base_driver", parent=None):
        super().__init__(name, parent)
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if not UVMConfigDb.get(self, "", "bus_if", arr):
            uvm_fatal(self.tag, "No interface specified for self driver instance")
        else:
            self.vif = arr[0]

    def start_of_simulation_phase(self, phase):
        super().start_of_simulation_phase(phase)
        cocotb.scheduler.add(self.rising_edge_time())

    @abstractmethod
    async def run_phase(self, phase):
        pass

    async def reset(self, num_cycles=3):
        self.vif.RESETn.value = 0
        self.end_of_trans()
        for _ in range(num_cycles):
            await self.drive_delay()
        self.vif.RESETn.value = 1

    async def drive_delay(self):
        await RisingEdge(self.vif.CLK)
        # await Timer(1, "NS")

    @abstractmethod
    async def end_of_trans(self, phase):
        pass

    async def rising_edge_time(self):
        self.rise_edge_time = cocotb.simulator.get_sim_time()
        while True:
            await RisingEdge(self.vif.CLK)
            self.rise_edge_time = cocotb.simulator.get_sim_time()
            uvm_info(
                self.tag, "Rising edge time: " + str(self.rise_edge_time), UVM_DEBUG
            )

    async def is_rising_edge(self):
        current_time = cocotb.simulator.get_sim_time()
        if self.rise_edge_time == current_time:
            uvm_info(self.tag, "it is a rising edge", UVM_DEBUG)
            return
        else:
            uvm_info(self.tag, "it is not a rising edge", UVM_DEBUG)
            await self.drive_delay()
            return False


uvm_component_utils(bus_base_driver)
