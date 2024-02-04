from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info, uvm_warning
from uvm.comps.uvm_driver import UVMDriver


class ip_driver(UVMDriver):
    def __init__(self, name="ip_driver", parent=None):
        super().__init__(name, parent)
        self.tag = name

    async def run_phase(self, phase):
        uvm_fatal(self.tag, "please write your monitor for the ip and replace it in the test")


uvm_component_utils(ip_driver)
