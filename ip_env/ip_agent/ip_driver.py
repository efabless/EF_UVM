from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info, uvm_warning
from uvm.comps.uvm_driver import UVMDriver
from uvm.base.uvm_config_db import UVMConfigDb


class ip_driver(UVMDriver):
    def __init__(self, name="ip_driver", parent=None):
        super().__init__(name, parent)
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if (not UVMConfigDb.get(self, "", "ip_if", arr)):
            uvm_fatal(self.tag, "No interface specified for self driver instance")
        else:
            self.vif = arr[0]
        regs_arr = []
        if (not UVMConfigDb.get(self, "", "bus_regs", regs_arr)):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.regs = regs_arr[0]

    async def run_phase(self, phase):
        uvm_fatal(self.tag, "please write your driver for the ip and replace it in the test")


uvm_component_utils(ip_driver)
