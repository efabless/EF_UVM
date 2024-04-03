from uvm.seq.uvm_sequence_item import UVMSequenceItem
from uvm.macros import (
    uvm_object_utils_begin,
    uvm_object_utils_end,
    uvm_field_int,
    uvm_object_utils,
    uvm_error,
    uvm_info,
)
from uvm.base.uvm_object_globals import UVM_ALL_ON, UVM_NOPACK, UVM_HIGH, UVM_MEDIUM
from uvm.base.sv import sv


class ip_item(UVMSequenceItem):
    def __init__(self, name="ip_item"):
        super().__init__(name)
        self.tag = name
        pass

    def convert2string(self):
        pass

    def do_compare(self, tr):
        pass


uvm_object_utils(ip_item)
