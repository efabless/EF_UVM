import json
import yaml

import cocotb

from cocotb.triggers import ClockCycles

from uvm.macros.uvm_message_defines import uvm_info, uvm_error, uvm_fatal
from uvm.base.uvm_object_globals import UVM_HIGH, UVM_LOW, UVM_MEDIUM


class bus_regs:
    """
    The bus_regs class is used to initialize and manage a set of registers specified in a JSON or YAML file.
    """

    def __init__(self, design_file) -> None:
        self.clock = None
        self.tag = "bus_regs"
        with open(design_file, "r") as file:
            if design_file.endswith(".json"):
                self.data = json.load(file)
            elif design_file.endswith(".yaml") or design_file.endswith(".yml"):
                self.data = yaml.safe_load(file)
        try:
            parameter_values = {
                param["name"]: param["default"] for param in self.data["parameters"]
            }
            self.replace_parameters(self.data, parameter_values)
        except KeyError:
            pass
        self.init_regs()
        uvm_info(self.tag, f"Regs: {self.regs}", UVM_HIGH)

    def set_clock(self, clock):
        self.clock = clock

    def init_regs(self):
        regs = {}
        address = 0
        self.irq_exist = False
        if "flags" in self.data and len(self.data["flags"]) > 0:
            size = len(self.data["flags"])
            reg_im = {
                "name": "im",
                "offset": 0xF00,
                "size": size,
                "mode": "w",
                "fifo": "no",
                "bit_access": "no",
                "val": 0,
                "delayed_val": 0,
            }
            reg_mis = {
                "name": "mis",
                "offset": 0xF04,
                "size": size,
                "mode": "r",
                "fifo": "no",
                "bit_access": "no",
                "val": 0,
                "delayed_val": 0,
            }
            reg_ris = {
                "name": "ris",
                "offset": 0xF08,
                "size": size,
                "mode": "r",
                "fifo": "no",
                "bit_access": "no",
                "val": 0,
                "delayed_val": 0,
            }
            reg_icr = {
                "name": "icr",
                "offset": 0xF0C,
                "size": size,
                "mode": "w",
                "fifo": "yes",
                "bit_access": "no",
                "val": 0,
                "delayed_val": 0,
            }
            address = 0xF00
            self.data["registers"].append(reg_im)
            self.data["registers"].append(reg_mis)
            self.data["registers"].append(reg_ris)
            self.data["registers"].append(reg_icr)
            self.irq_exist = True
        for reg in self.data["registers"]:
            if "init" not in reg:
                reg["val"] = 0
            else:
                try:
                    reg["val"] = int(reg["init"][2:], 16)
                except ValueError:
                    reg["val"] = int(reg["init"])
            reg["delayed_val"] = reg["val"]
            regs[int(reg["offset"])] = reg
        self.regs = regs
        self.reg_name_to_address = {
            info["name"]: address for address, info in self.regs.items()
        }
        uvm_info(
            self.tag, f"regs name and addresses {self.reg_name_to_address}", UVM_MEDIUM
        )

    def get_regs(self):
        return self.regs

    def get_irq_exist(self):
        return self.irq_exist

    async def __write_reg_value_after(
        self, reg, value, cycles, mask=0xFFFFFFFF, force_write=False
    ):
        uvm_info(self.tag, "delayed write waiting", UVM_LOW)
        await ClockCycles(self.clock, cycles)
        self.write_reg_value(reg=reg, value=value, mask=mask, force_write=force_write)
        uvm_info(self.tag, "delayed write done", UVM_LOW)

    def write_reg_value_after(
        self, reg, value, cycles, mask=0xFFFFFFFF, force_write=False
    ):
        if self.clock is None:
            uvm_fatal(self.tag, "No clock connected")
        cocotb.scheduler.add(
            self.__write_reg_value_after(
                reg=reg, value=value, mask=mask, force_write=force_write, cycles=cycles
            )
        )

    async def update_delayed_reg(self, address):
        await ClockCycles(self.clock, 1)
        self.regs[address]["delayed_val"] = self.regs[address]["val"]

    def write_reg_value(self, reg, value, mask=0xFFFFFFFF, force_write=False):
        """
        Writes a value to a register.
        Parameters:
            reg (int or str): The register to write to. If an integer is provided, it is treated as the address of the register. If a string is provided, it is treated as the name of the register and converted to its corresponding address using the `reg_name_to_address` dictionary.
            value: The value to write to the register.
        Returns:
            None
        """
        if type(reg) is int:
            address = reg
        elif type(reg) is str:
            address = self.reg_name_to_address[reg]
        else:
            uvm_error(
                self.tag, f"Invalid reg type: {type(reg)} for write value: {value}"
            )
        address = address & 0xFFFF
        if address in self.regs:
            uvm_info(
                self.tag,
                f"value before write {hex(value)} to address {hex(address)}: {hex(self.regs[address]['val'])}",
                UVM_HIGH,
            )
            if "w" in self.regs[address]["mode"] or force_write:
                if mask != 0xFFFFFFFF:
                    old_value = self.regs[address]["val"]
                    value = (old_value & ~mask) | (value & mask)
                self.regs[address]["val"] = value & (
                    (1 << int(self.regs[address]["size"])) - 1
                )
            uvm_info(
                self.tag,
                f"value after write to address {hex(address)}: {hex(self.regs[address]['val'])}",
                UVM_HIGH,
            )
            cocotb.scheduler.add(self.update_delayed_reg(address))

    def __read_reg_value(self, reg, delayed=False):
        if type(reg) is int:
            address = reg
        elif type(reg) is str:
            address = self.reg_name_to_address[reg]
        else:
            uvm_error(self.tag, f"Invalid reg type: {type(reg)} for read")
        address = address & 0xFFFF
        if delayed:
            return self.regs[address]["delayed_val"]
        else:
            return self.regs[address]["val"]

    def read_reg_value(self, reg):
        return self.__read_reg_value(reg)

    def read_reg_value_delayed(self, reg):
        return self.__read_reg_value(reg, delayed=True)

    # Function to replace parameter values in the data
    def replace_parameters(self, data, parameter_values):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value in parameter_values:
                    data[key] = parameter_values[value]
                else:
                    self.replace_parameters(value, parameter_values)
        elif isinstance(data, list):
            for item in data:
                self.replace_parameters(item, parameter_values)
