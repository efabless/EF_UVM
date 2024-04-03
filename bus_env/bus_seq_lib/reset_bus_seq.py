from uvm.macros.uvm_object_defines import uvm_object_utils
from EF_UVM.bus_env.bus_seq_lib.bus_seq_base import bus_seq_base


class reset_bus_seq(bus_seq_base):
    def __init__(self, name="reset_bus_seq"):
        super().__init__(name)

    async def body(self):
        await super().body()
        await self.send_reset()


uvm_object_utils(reset_bus_seq)
