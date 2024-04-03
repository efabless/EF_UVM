from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.comps.uvm_driver import UVMDriver
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_MEDIUM, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item
from abc import abstractmethod


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

    @abstractmethod
    async def run_phase(self, phase):
        pass

    async def reset(self, num_cycles=3):
        self.vif.RESETn.value = 0
        for _ in range(num_cycles):
            await self.drive_delay()
        self.vif.RESETn.value = 1
        self.end_of_trans()

    async def drive_delay(self):
        await RisingEdge(self.vif.CLK)
        await Timer(1, "NS")

    @abstractmethod
    async def end_of_trans(self, phase):
        pass


uvm_component_utils(bus_base_driver)
