from uvm.seq import UVMSequence
from uvm.macros.uvm_object_defines import uvm_object_utils
from uvm.macros.uvm_message_defines import uvm_fatal
from EF_UVM.bus_env.bus_item import bus_bus_item
from uvm.base.uvm_config_db import UVMConfigDb
from uvm.macros.uvm_sequence_defines import uvm_do_with, uvm_do


class bus_seq_base(UVMSequence):

    def __init__(self, name="bus_seq_base"):
        UVMSequence.__init__(self, name)
        self.set_automatic_phase_objection(1)
        self.req = bus_bus_item()
        self.rsp = bus_bus_item()
        self.tag = name

    async def body(self):
        # get register names/address conversion dict
        arr = []
        if (not UVMConfigDb.get(self, "", "bus_regs", arr)):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.adress_dict = arr[0].reg_name_to_address

    async def send_req(self, is_write, reg, data_condition=None):
        # send request
        if is_write:
            if data_condition is None:
                await uvm_do_with(self, self.req, lambda addr: addr == self.adress_dict[reg], lambda kind: kind == bus_bus_item.WRITE)
            else:
                await uvm_do_with(self, self.req, lambda addr: addr == self.adress_dict[reg], lambda kind: kind == bus_bus_item.WRITE, data_condition)
        else:
            await uvm_do_with(self, self.req, lambda addr: addr == self.adress_dict[reg], lambda kind: kind == bus_bus_item.READ)


uvm_object_utils(bus_seq_base)
