from uvm.macros.uvm_object_defines import uvm_object_utils
from uvm.macros.uvm_message_defines import uvm_info, uvm_fatal
from uvm.macros.uvm_sequence_defines import uvm_do_with, uvm_do
from uvm.base import sv, UVM_HIGH, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb_coverage.coverage import coverage_db
import os
from EF_UVM.bus_env.bus_seq_lib.bus_seq_base import bus_seq_base


class write_read_regs(bus_seq_base):
    def __init__(self, name="write_read_regs"):
        super().__init__(name)
        self.tag = name

    async def body(self):
        # get all regs valid addresses
        arr = []
        if not UVMConfigDb.get(self, "", "bus_regs", arr):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            regs = arr[0]
        self.regs_dict = regs.get_regs()
        self.address = list(self.regs_dict.keys())
        # remove non read write addresses
        uvm_info(self.tag, "Got addresses: " + str(self.address), UVM_LOW)
        self.address = [
            addr
            for addr in self.address
            if self.regs_dict[addr]["mode"] == "w"
            and self.regs_dict[addr]["fifo"] is False
        ]
        uvm_info(self.tag, "Got addresses: " + str(self.address), UVM_LOW)
        self.add_cov_notify()
        for i in range(3000):
            await uvm_do_with(self, self.req, lambda addr: addr in self.address)
            if (
                len(self.address) < 2
            ):  # if only one is still can't get high coverage it probabily need corner test
                break

    def add_cov_notify(self):
        # add callback to the cover group
        for name in self.regs_dict.values():
            coverage_db["top.wrapper.regs." + name["name"]].add_threshold_callback(
                self.remove_addr, 95
            )

    def remove_addr(self):
        # remove callback from the cover group
        for address, name in self.regs_dict.items():
            if coverage_db["top.wrapper.regs." + name["name"]].cover_percentage >= 95:
                try:
                    self.address.remove(address)
                    uvm_info(
                        self.tag,
                        f"removed address: {str(address)}({name['name']})  address available in regs:  {str(self.address)}",
                        UVM_LOW,
                    )
                except ValueError:
                    pass


uvm_object_utils(write_read_regs)
