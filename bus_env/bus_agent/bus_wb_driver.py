from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.comps.uvm_driver import UVMDriver
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_MEDIUM, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item


class bus_wb_driver(UVMDriver):
    def __init__(self, name="bus_ahb_driver", parent=None):
        super().__init__(name, parent)
        self.tag = name

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        if (not UVMConfigDb.get(self, "", "bus_if", arr)):
            uvm_fatal(self.tag, "No interface specified for self driver instance")
        else:
            self.vif = arr[0]

    async def run_phase(self, phase):
        uvm_info(self.tag, "run_phase started", UVM_MEDIUM)
        await self.reset()
        while True:
            await self.drive_delay()
            tr = []
            await self.seq_item_port.get_next_item(tr)
            tr = tr[0]
            uvm_info(self.tag, "Driving trans into DUT: " + tr.convert2string(), UVM_HIGH)
            if tr.kind == bus_item.RESET:
                uvm_info(self.tag, "Doing reset", UVM_MEDIUM)
                await self.reset()
                self.seq_item_port.item_done()
                continue
            elif tr.kind == bus_item.NOPE:
                await self.drive_delay()
                self.seq_item_port.item_done()
                continue
            await self.send_trans(tr)
            self.seq_item_port.item_done()

    async def reset(self, num_cycles=3):
        self.vif.HRESETn.value = 0
        for _ in range(num_cycles):
            await self.drive_delay()
        self.vif.HRESETn.value = 1
        self.end_of_trans()

    async def send_trans(self, tr):
        if tr.kind == bus_item.READ:
            self.vif.we_i.value = 0
        else:
            self.vif.we_i.value = 1
            self.vif.dat_i.value = tr.data
        self.vif.adr_i.value = tr.addr
        self.vif.sel_i.value = 0b1111
        self.vif.cyc_i.value = 0b1
        self.vif.stb_i.value = 0b1
        # TODO: HSIZE should be existed in the DUT wait until it got added
        await self.drive_delay()
        while self.vif.ack_o.value == 0:
            await self.drive_delay()
        self.end_of_trans()

    async def drive_delay(self):
        await RisingEdge(self.vif.HCLK)

    def end_of_trans(self):
        self.vif.sel_i.value = 0b0000
        self.vif.cyc_i.value = 0b0
        self.vif.stb_i.value = 0


uvm_component_utils(bus_wb_driver)
