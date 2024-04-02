from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.comps.uvm_driver import UVMDriver
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_MEDIUM, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item


class bus_apb_driver(UVMDriver):
    def __init__(self, name="bus_apb_driver", parent=None):
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
            #if (not self.vif.clk.triggered):
            #yield Edge(self.vif.clk)
            # await self.drive_delay()
            #yield RisingEdge(self.vif.clk)
            #yield Timer(1, "NS")

            await self.trans_received(tr)
            #uvm_do_callbacks(apb_master,apb_master_cbs,trans_received(self,tr))

            if tr.kind == bus_item.READ:
                data = []
                await self.read(tr.addr, data)
                tr.data = data[0]
            elif tr.kind == bus_item.WRITE:
                await self.write(tr.addr, tr.data)

            await self.trans_executed(tr)
            #uvm_do_callbacks(apb_master,apb_master_cbs,trans_executed(self,tr))
            self.seq_item_port.item_done()

    async def reset(self, num_cycles=3):
        self.vif.PRESETn.value = 0
        for _ in range(num_cycles):
            await self.drive_delay()
        self.vif.PRESETn.value = 1
        self.end_of_trans()

    async def drive_delay(self):
        await RisingEdge(self.vif.CLK)
        await Timer(1, "NS")

    async def trans_received(self, tr):
        await Timer(1, "NS")

    async def trans_executed(self, tr):
        await Timer(1, "NS")

    async def read(self, addr, data):
        uvm_info(self.tag, "Doing APB read to addr " + hex(addr), UVM_HIGH)
        self.vif.PADDR.value = addr
        self.vif.PWRITE.value = 0
        self.vif.PSEL.value = 1
        await self.drive_delay()
        self.vif.PENABLE.value = 1
        await self.drive_delay()
        data.append(self.vif.PRDATA)
        self.end_of_trans()

    async def write(self, addr, data):
        uvm_info(self.tag, "Doing APB write to addr " + hex(addr), UVM_HIGH)
        self.vif.PADDR.value = addr
        self.vif.PWDATA.value = data
        self.vif.PWRITE.value = 1
        self.vif.PSEL.value = 1
        await self.drive_delay()
        self.vif.PENABLE.value = 1
        await self.drive_delay()
        self.end_of_trans()
        uvm_info(self.tag, "Finished APB write to addr " + hex(addr), UVM_HIGH)

    def end_of_trans(self):
        self.vif.PSEL.value = 0
        self.vif.PENABLE.value = 0

uvm_component_utils(bus_apb_driver)
