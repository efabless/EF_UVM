from EF_UVM.ip_env.ip_logger.ip_logger import ip_logger
import cocotb 
from uvm.macros import uvm_component_utils, uvm_fatal


class skeleton_logger(ip_logger):
    def __init__(self, name="skeleton_logger", parent=None):
        super().__init__(name, parent)
        uvm_fatal("skeleton_logger", "please write self.header in list format")
        # self.header = ['Time (ns)', "Direction"]
        self.col_widths = [10]* len(self.header)

    def logger_formatter(self, transaction):
        # this called when new transaction is called from ip monitor
        # TODO: should return the list of strings by the information in the header with the same order
        return []


uvm_component_utils(skeleton_logger)
