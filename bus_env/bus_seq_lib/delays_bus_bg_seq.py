from uvm.macros.uvm_object_defines import uvm_object_utils
from EF_UVM.bus_env.bus_seq_lib.bus_seq_base import bus_seq_base
import random
from cocotb.triggers import Timer
from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.base.uvm_object_globals import UVM_FULL, UVM_LOW, UVM_ERROR


class delays_bus_bg_seq(bus_seq_base):
    """This sequence is suppose to be run in the background to insert random delays
    This needed because this flow mostly communicate with 1 slave but in real SOCs
    the master is connected to more than 1 and a lot of delays exists
    """

    def __init__(self, name="delays_bus_bg_seq", clk_period=20):
        super().__init__(name)
        self.clk_period = clk_period

    async def body(self):
        while True:
            random_delay = (
                random.randint(0, (self.clk_period) * 100 // self.clk_period)
                * self.clk_period
            )  # multiple of clk_period it can be up to 100 clk_period
            uvm_info(self.tag, "Random delay: " + str(random_delay) + "ns", UVM_FULL)
            await Timer(random_delay, "ns")
            await self.send_nop(nope_size=random.randint(1, 3))


uvm_object_utils(delays_bus_bg_seq)
