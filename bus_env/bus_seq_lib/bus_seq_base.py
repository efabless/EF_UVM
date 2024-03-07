from uvm.seq import UVMSequence
from uvm.macros.uvm_object_defines import uvm_object_utils
from uvm.macros.uvm_message_defines import uvm_fatal, uvm_info
from EF_UVM.bus_env.bus_item import bus_item
from uvm.base.uvm_config_db import UVMConfigDb
from uvm.macros.uvm_sequence_defines import uvm_do_with, uvm_do
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW, UVM_MEDIUM

class bus_seq_base(UVMSequence):

    def __init__(self, name="bus_seq_base"):
        UVMSequence.__init__(self, name)
        self.set_automatic_phase_objection(1)
        self.req = bus_item()
        self.rsp = bus_item()
        self.tag = name

    async def body(self):
        # get register names/address conversion dict
        arr = []
        if (not UVMConfigDb.get(self, "", "bus_regs", arr)):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.adress_dict = arr[0].reg_name_to_address

    async def send_req(self, is_write, reg, data_condition=None, data_value = None):
        # send request
        if data_condition is not None and data_value is not None:
            uvm_fatal (self.tag, "You should only provide data condition or data value")
        if is_write:
            if data_condition is None:
                if data_value is not None:
                    self.req.rand_mode(0)
                    self.req.addr = self.adress_dict[reg]
                    self.req.data = data_value
                    self.req.kind = bus_item.WRITE
                    await uvm_do(self, self.req)
                else:
                    self.req.rand_mode(1)
                    await uvm_do_with(self, self.req, lambda addr: addr == self.adress_dict[reg], lambda kind: kind == bus_item.WRITE)
            else:
                self.req.rand_mode(1)
                await uvm_do_with(self, self.req, lambda addr: addr == self.adress_dict[reg], lambda kind: kind == bus_item.WRITE, data_condition)
        else:
            self.req.rand_mode(0)
            self.req.addr = self.adress_dict[reg]
            self.req.kind = bus_item.READ
            self.req.data = 0  # needed to add any dummy value
            await uvm_do(self, self.req)

uvm_object_utils(bus_seq_base)
