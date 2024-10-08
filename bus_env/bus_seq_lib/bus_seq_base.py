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
        # self.set_automatic_phase_objection(1)

        self.tag = name
        # disable checking for overflow if the response queue is full
        # if respose checking is needed the sequence should take care of it
        self.set_response_queue_error_report_disabled(1)
        self.response_queue_error_report_disabled = 1

    def create_new_item(self):
        self.req = bus_item()
        self.rsp = bus_item()

    async def body(self):
        # get register names/address conversion dict
        arr = []
        if not UVMConfigDb.get(self, "", "bus_regs", arr):
            uvm_fatal(self.tag, "No json file wrapper regs")
        else:
            self.adress_dict = arr[0].reg_name_to_address

    async def send_req(self, is_write, reg, data_condition=None, data_value=None):
        # send request
        self.create_new_item()
        if data_condition is not None and data_value is not None:
            uvm_fatal(self.tag, "You should only provide data condition or data value")
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
                    await uvm_do_with(
                        self,
                        self.req,
                        lambda addr: addr == self.adress_dict[reg],
                        lambda kind: kind == bus_item.WRITE,
                    )
            else:
                self.req.rand_mode(1)
                await uvm_do_with(
                    self,
                    self.req,
                    lambda addr: addr == self.adress_dict[reg],
                    lambda kind: kind == bus_item.WRITE,
                    data_condition,
                )
        else:
            self.req.rand_mode(0)
            self.req.addr = self.adress_dict[reg]
            self.req.kind = bus_item.READ
            self.req.data = 0  # needed to add any dummy value
            await uvm_do(self, self.req)
        self.req.rand_mode(1)

    async def send_nop(self, nope_size=1):
        self.create_new_item()
        self.req.rand_mode(0)
        self.req.addr = 0
        self.req.kind = bus_item.NOPE
        self.req.data = nope_size  # needed to add any dummy value
        await uvm_do(self, self.req)
        self.req.rand_mode(1)

    async def send_reset(self):
        self.create_new_item()
        self.req.rand_mode(0)
        self.req.addr = 0
        self.req.kind = bus_item.RESET
        self.req.data = 0  # needed to add any dummy value
        await uvm_do(self, self.req)
        self.req.rand_mode(1)


uvm_object_utils(bus_seq_base)
