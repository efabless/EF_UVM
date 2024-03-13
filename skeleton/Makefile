PLUSARGS += "+UVM_VERBOSITY=UVM_MEDUIM"
TOPLEVEL := top
MODULE   ?= top_module
AHB_FILES ?= # TODO: Add add AHB wrapper file path
APB_FILES ?= # TODO: Add add APB wrapper file path
WB_FILES ?= # TODO: Add add WB wrapper file path
HDL_FILES ?= # TODO: Add ip hdl wrapper file path
VERILOG_SOURCES ?=  $(PWD)/top.v $(AHB_FILES) $(APB_FILES) $(WB_FILES) $(HDL_FILES)
RTL_MACROS += "" # Add macros needed
BUS_TYPE ?= APB
ifeq ($(BUS_TYPE),APB)
    RTL_MACROS += -DBUS_TYPE_APB
else ifeq ($(BUS_TYPE),AHB)
    RTL_MACROS += -DBUS_TYPE_AHB
else ifeq ($(BUS_TYPE),WISHBONE)
    RTL_MACROS += -DBUS_TYPE_WISHBONE
endif
# RTL_MACROS ?= "-DSKIP_WAVE_DUMP"
YAML_FILE = $(PWD)/../../<skeleton>.yaml # TODO: update yaml file path
MAKEFLAGS += --no-print-directory

# List of tests
TESTS := # TODO: Add tests names

# Variable for tag - set this as required
SIM_TAG ?= default_tag

# Define SIM_PATH variable
SIM_PATH := $(PWD)/sim/$(SIM_TAG)

# Check and clone EF_UVM repository at the beginning of the Makefile execution

clone_ef_uvm := $(shell if [ ! -d "EF_UVM" ]; then \
	echo "Cloning the EF_UVM repository..."; \
	git clone https://github.com/efabless/EF_UVM.git; \
fi;)


include EF_UVM/Makefile.test
