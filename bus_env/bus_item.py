from uvm.seq.uvm_sequence_item import UVMSequenceItem
from uvm.macros import (
    uvm_object_utils_begin,
    uvm_object_utils_end,
    uvm_field_int,
    uvm_object_utils,
)
from uvm.base.uvm_object_globals import UVM_ALL_ON, UVM_NOPACK
from uvm.base.sv import sv
from uvm.macros import uvm_component_utils, uvm_info, uvm_error, uvm_warning
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW


class bus_item(UVMSequenceItem):

    READ = 0
    WRITE = 1
    RESET = 2
    NOPE = 3  # Insert a no-op in the sequence

    def __init__(self, name="bus_item"):
        super().__init__(name)
        self.tag = name
        self.addr = 0  # bit
        self.rand("addr", range(0, 0xFFF))
        self.data = 0  # logic
        self.rand("data", range(0, 0xFFFF))
        self.kind = bus_item.READ  # kind_e
        self.rand("kind", [bus_item.READ, bus_item.WRITE])

    def convert2string(self):
        if self.kind == bus_item.RESET:
            return sv.sformatf("RESET command send to DUT")
        if self.kind == bus_item.NOPE:
            return sv.sformatf("NO-OP command send to DUT")
        kind = "READ"
        if self.kind == 1:
            kind = "WRITE"
        try:
            return f"kind={kind} addr={hex(self.addr)} data={hex(self.data)}"
        except TypeError or ValueError:
            return f"kind={kind} addr={self.addr} data={self.data}"

    def do_clone(self):
        t = bus_item()
        t.copy(self)
        return t

    def do_compare(self, tr):
        # check if the data is trash return True
        if tr.data == "X":
            uvm_warning(
                self.tag,
                f"Data for comparing {self.convert2string()} is trash as it's not upredictable and in valid so the scoreboard should not check it",
            )
            return True
        return self.kind == tr.kind and self.addr == tr.addr and self.data == tr.data


uvm_object_utils_begin(bus_item)
uvm_field_int("addr", UVM_ALL_ON | UVM_NOPACK)
uvm_field_int("data", UVM_ALL_ON | UVM_NOPACK)
uvm_object_utils_end(bus_item)


class bus_irq_item(UVMSequenceItem):

    def __init__(self, name="bus_irq_item"):
        super().__init__(name)
        self.trg_irq = 0  # bit

    def convert2string(self):
        return sv.sformatf(
            f"{'clear interrupt' if self.trg_irq == 0 else 'set interrupt'}"
        )

    def do_compare(self, tr):
        # check if the data is trash return True
        return self.trg_irq == tr.trg_irq


uvm_object_utils(bus_irq_item)
