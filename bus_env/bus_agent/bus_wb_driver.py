from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.comps.uvm_driver import UVMDriver
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_MEDIUM, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item
from EF_UVM.bus_env.bus_agent.bus_base_driver import bus_base_driver


class bus_wb_driver(bus_base_driver):
    def __init__(self, name="bus_ahb_driver", parent=None):
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
            tr.data = await self.send_trans(tr)
            self.seq_item_port.item_done()
            self.seq_item_port.put_response(tr)

    async def send_trans(self, tr):
        if tr.kind == bus_item.READ:
            self.vif.we_i.value = 0
        else:
            self.vif.we_i.value = 1
            self.vif.dat_i.value = tr.data
        if tr.size == bus_item.WORD_ACCESS:
            self.vif.adr_i.value = tr.addr
            self.vif.sel_i.value = 0b1111
        elif tr.size == bus_item.HALF_WORD_ACCESS:
            if tr.addr % 4 == 0:
                self.vif.adr_i.value = tr.addr
                self.vif.sel_i.value = 0b0011
            else:
                self.vif.adr_i.value = tr.addr & ~0b11 # divided by 4
                self.vif.sel_i.value = 0b1100
        elif tr.size == bus_item.BYTE_ACCESS:
            if tr.addr % 4 == 0:
                self.vif.adr_i.value = tr.addr
                self.vif.sel_i.value = 0b0001
            elif tr.addr % 4 == 1:
                self.vif.adr_i.value = tr.addr & ~0b11
                self.vif.sel_i.value = 0b0010
            elif tr.addr % 4 == 2:
                self.vif.adr_i.value = tr.addr & ~0b11
                self.vif.sel_i.value = 0b0100
            elif tr.addr % 4 == 3:
                self.vif.adr_i.value = tr.addr & ~0b11
                self.vif.sel_i.value = 0b1000
        self.vif.cyc_i.value = 0b1
        self.vif.stb_i.value = 0b1
        # TODO: HSIZE should be existed in the DUT wait until it got added
        await self.drive_delay()
        while self.vif.ack_o.value == 0:
            await self.drive_delay()
        self.end_of_trans()
        if tr.kind == bus_item.READ:
            return self.vif.dat_o.value.integer
        else:
            return tr.data

    def end_of_trans(self):
        self.vif.sel_i.value = 0b0000
        self.vif.cyc_i.value = 0b0
        self.vif.stb_i.value = 0


uvm_component_utils(bus_wb_driver)
