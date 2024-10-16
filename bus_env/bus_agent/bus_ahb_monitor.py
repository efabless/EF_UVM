from uvm.macros import uvm_component_utils, uvm_fatal, uvm_info, uvm_error, uvm_warning
from uvm.comps.uvm_monitor import UVMMonitor
from uvm.tlm1.uvm_analysis_port import UVMAnalysisPort
from uvm.base.uvm_config_db import UVMConfigDb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, NextTimeStep, Lock
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW
from EF_UVM.bus_env.bus_item import bus_item
from EF_UVM.bus_env.bus_agent.bus_base_monitor import bus_base_monitor
import cocotb


class bus_ahb_monitor(bus_base_monitor):
    def __init__(self, name="bus_ahb_monitor", parent=None):
        super().__init__(name, parent)
        self.active_reset = False

    async def run_phase(self, phase):
        uvm_info(self.tag, "Starting AHB monitor run phase", UVM_LOW)
        self.data_phase_lock = Lock()  # to get only one in piping
        while True:
            start_thread = await cocotb.start(self.start())
            await self.assert_reset()
            start_thread.kill()
            self.active_reset = True
            if self.data_phase_lock.locked:
                self.data_phase_lock.release()

    async def start(self):
        while True:
            tr = None
            # wait for a transaction
            await NextTimeStep()
            tr = bus_item.type_id.create("tr", self)
            tr = await self.address_phase(tr)
            uvm_info(self.tag, f"address_phase", UVM_LOW)
            await self.data_phase_lock.acquire()
            uvm_info(self.tag, f"acquired lock", UVM_LOW)
            await cocotb.start(self.data_phase(tr))
            uvm_info(self.tag, f"data_phase", UVM_LOW)

    async def assert_reset(self):
        await FallingEdge(self.vif.RESETn)
        # send reset tr
        tr = bus_item.type_id.create("tr", self)
        tr.kind = bus_item.RESET
        tr.addr = 0
        self.monitor_port.write(tr)
        uvm_info(self.tag, "sampled reset transaction: " + tr.convert2string(), UVM_LOW)

    async def deassert_reset(self):
        await RisingEdge(self.vif.RESETn)
        uvm_info(self.tag, "deasserted reset", UVM_LOW)

    async def sample_delay(self):
        await RisingEdge(self.vif.CLK)
        await Timer(1, "NS")
        await NextTimeStep()

    async def address_phase(self, tr):
        while True:
            await self.sample_delay()
            if self.vif.RESETn.value.binstr == "1":
                self.active_reset = False
            if self.vif.HSEL.value.binstr == "1":
                if self.vif.HTRANS.value.binstr[0] == "1":
                    break
        tr.addr = self.vif.HADDR.value.integer
        tr.kind = bus_item.WRITE if self.vif.HWRITE.value.integer else bus_item.READ
        try:
            tr.size = self.vif.HSIZE.value
        except AttributeError:
            tr.size = bus_item.WORD_ACCESS
        tr = self.monitor_optional_signals_address(tr)
        return tr

    def monitor_optional_signals_address(self, tr):
        return tr

    async def data_phase(self, tr):
        await self.sample_delay()
        while self.vif.HREADYOUT.value == 0:
            await self.sample_delay()
        if tr.kind == bus_item.WRITE:
            tr.data = self.vif.HWDATA.value.integer
        else:
            try:
                if tr.size == bus_item.WORD_ACCESS:
                    tr.data = self.vif.HRDATA.value.integer
                elif tr.size == bus_item.HALF_WORD_ACCESS:
                    if tr.addr % 4 == 0:
                        tr.data = self.vif.HRDATA.value.integer & 0xFFFF
                    else:
                        tr.data = self.vif.HRDATA.value.integer >> 16
                elif tr.size == bus_item.BYTE_ACCESS:
                    if tr.addr % 4 == 0:
                        tr.data = self.vif.HRDATA.value.integer & 0xFF
                    elif tr.addr % 4 == 1:
                        tr.data = (self.vif.HRDATA.value.integer >> 8) & 0xFF
                    elif tr.addr % 4 == 2:
                        tr.data = (self.vif.HRDATA.value.integer >> 16) & 0xFF
                    elif tr.addr % 4 == 3:
                        tr.data = (self.vif.HRDATA.value.integer >> 24) & 0xFF
            except ValueError:
                uvm_warning(
                    self.tag, f"HRDATA is not an integer {self.vif.HRDATA.value.binstr}"
                )
                if tr.size == bus_item.WORD_ACCESS:
                    tr.data = self.vif.HRDATA.value.binstr
                elif tr.size == bus_item.HALF_WORD_ACCESS:
                    try:
                        if tr.addr % 4 == 0:
                            tr.data = int(self.vif.HRDATA.value.binstr[0:16], 2)
                        else:
                            tr.data = int(self.vif.HRDATA.value.binstr[16:], 2)
                    except ValueError:
                        tr.data = self.vif.HRDATA.value.binstr
                elif tr.size == bus_item.BYTE_ACCESS:
                    try:
                        if tr.addr % 4 == 0:
                            tr.data = int(self.vif.HRDATA.value.binstr[0:8], 2)
                        elif tr.addr % 4 == 1:
                            tr.data = int(self.vif.HRDATA.value.binstr[8:16], 2)
                        elif tr.addr % 4 == 2:
                            tr.data = int(self.vif.HRDATA.value.binstr[16:24], 2)
                        elif tr.addr % 4 == 3:
                            tr.data = int(self.vif.HRDATA.value.binstr[24:], 2)
                    except ValueError:
                        tr.data = self.vif.HRDATA.value.binstr                    
        if self.data_phase_lock.locked:
            self.data_phase_lock.release()
        if self.active_reset:
            return
        self.monitor_port.write(tr)
        uvm_info(self.tag, "sampled AHB transaction: " + tr.convert2string(), UVM_LOW)
        return tr


uvm_component_utils(bus_ahb_monitor)
