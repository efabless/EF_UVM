from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.comps.uvm_driver import UVMDriver
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_MEDIUM, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item
from EF_UVM.bus_env.bus_agent.bus_base_driver import bus_base_driver


class bus_apb_driver(bus_base_driver):
    def __init__(self, name="bus_apb_driver", parent=None):
        super().__init__(name, parent)
        self.tag = name

    async def run_phase(self, phase):
        uvm_info(self.tag, "run_phase started", UVM_MEDIUM)
        while True:
            await self.drive_delay()
            tr = []
            await self.seq_item_port.get_next_item(tr)
            tr = tr[0]
            uvm_info(
                self.tag, "Driving trans into DUT: " + tr.convert2string(), UVM_HIGH
            )
            if tr.kind == bus_item.RESET:
                uvm_info(self.tag, "Doing reset", UVM_MEDIUM)
                await self.reset()
                self.seq_item_port.item_done()
                continue
            elif tr.kind == bus_item.NOPE:
                await self.drive_delay()
                self.seq_item_port.item_done()
                continue
            # if (not self.vif.clk.triggered):
            # yield Edge(self.vif.clk)
            # await self.drive_delay()
            # yield RisingEdge(self.vif.clk)
            # yield Timer(1, "NS")

            await self.trans_received(tr)
            # uvm_do_callbacks(apb_master,apb_master_cbs,trans_received(self,tr))

            if tr.kind == bus_item.READ:
                tr.data = await self.read(tr.addr)
            elif tr.kind == bus_item.WRITE:
                await self.write(tr.addr, tr.data)

            await self.trans_executed(tr)
            # uvm_do_callbacks(apb_master,apb_master_cbs,trans_executed(self,tr))
            self.seq_item_port.item_done()
            self.seq_item_port.put_response(tr)

    async def trans_received(self, tr):
        await Timer(1, "NS")

    async def trans_executed(self, tr):
        await Timer(1, "NS")

    async def read(self, addr):
        uvm_info(self.tag, "Doing APB read to addr " + hex(addr), UVM_HIGH)
        self.vif.PADDR.value = addr
        self.vif.PWRITE.value = 0
        self.vif.PSEL.value = 1
        await self.drive_delay()
        self.vif.PENABLE.value = 1
        await self.drive_delay()
        await self.wait_ready()
        try:
            data = self.vif.PRDATA.value.integer
        except TypeError or ValueError:
            data = self.vif.PRDATA.value
        self.end_of_trans()
        return data

    async def write(self, addr, data):
        uvm_info(self.tag, "Doing APB write to addr " + hex(addr), UVM_HIGH)
        self.vif.PADDR.value = addr
        self.vif.PWDATA.value = data
        self.vif.PWRITE.value = 1
        self.vif.PSEL.value = 1
        await self.drive_delay()
        self.vif.PENABLE.value = 1
        await self.drive_delay()
        await self.wait_ready()
        self.end_of_trans()
        uvm_info(self.tag, "Finished APB write to addr " + hex(addr), UVM_HIGH)

    def end_of_trans(self):
        self.vif.PSEL.value = 0
        self.vif.PENABLE.value = 0

    async def wait_ready(self):
        while self.vif.PREADY == 0:
            await self.drive_delay()
uvm_component_utils(bus_apb_driver)
