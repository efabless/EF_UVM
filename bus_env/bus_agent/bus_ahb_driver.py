from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info
from uvm.comps.uvm_driver import UVMDriver
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_MEDIUM, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item
from EF_UVM.bus_env.bus_agent.bus_base_driver import bus_base_driver


class bus_ahb_driver(bus_base_driver):
    def __init__(self, name="bus_ahb_driver", parent=None):
        super().__init__(name, parent)
        self.tag = name

    async def run_phase(self, phase):
        uvm_info(self.tag, "run_phase started", UVM_MEDIUM)
        await self.reset()
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
            await self.address_phase(tr)
            await self.data_phase(tr)
            self.seq_item_port.item_done()

    async def address_phase(self, tr):
        if tr.kind == bus_item.READ:
            self.vif.HWRITE.value = 0
        else:
            self.vif.HWRITE.value = 1
        self.vif.HADDR.value = tr.addr
        self.vif.HTRANS.value = 0b10
        self.vif.HSEL.value = 0b01
        self.vif.HREADY.value = 1
        # TODO: HSIZE should be existed in the DUT wait until it got added
        await self.drive_delay()
        self.end_of_trans()

    async def data_phase(self, tr):
        if tr.kind == bus_item.WRITE:
            self.vif.HWDATA.value = tr.data
            await self.drive_delay()
            while self.vif.HREADYOUT == 0:
                await self.drive_delay()
        else:
            # for reading just wait until the data is ready
            await self.drive_delay()
            while self.vif.HREADYOUT == 0:
                await self.drive_delay()

    def end_of_trans(self):
        self.vif.HSEL.value = 0b00
        self.vif.HTRANS.value = 0b00
        self.vif.HWRITE.value = 0


uvm_component_utils(bus_ahb_driver)
