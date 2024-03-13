##  Overview

EF_UVM is a resuable UVM testbench environment based on [uvm-python](https://github.com/tpoikela/uvm-python) library. The environment could be used for any IP/design after wrapping the design with [this](https://github.com/shalan/IP_Utilities/tree/main/generators) AMBA wrappers generator. 

Before usage, it is recommended to get familiar with [cocotb](https://docs.cocotb.org/en/stable/) which is a framework which enables verifying Verilog RTL using Python. Also, if you are new to UVM (Universal Verification Methodolgy), it is recommended to check [this](https://www.youtube.com/watch?v=igYsB_sKeNc&list=PLEgCreVKPx5AP61Pu36QQE0Pkni2Vv-HD). Finally, you should check [uvm-python](https://github.com/tpoikela/uvm-python) which is a Python and cocotb-based port of the SystemVerilog Universal Verification Methodology (UVM) 

---
##  Quick Links
> - [ Architecture](#architecture)
> - [ IPs verified using EF_UVM](#IPs-verified-using-EF_UVM)
> - [ Running tests](#running-tests)
> - [ Steps to verify new IP](#Steps-to-verify-new-IP)
> - [ Contributing](#contributing)
> - [ License](#license)

---


## Architecture 
As shown in Figure 1 below, The environment consisted of two sub environmnet one for the bus wrapper and the other is for the IP. Most of the testbench components can be used without modification and some should be updated for each IP.

![alt text](<doc/img/uvm arc.png>)
Figure 1: Environment diagram.

### Testbench overview 
The testbench is written in Python using the UVM-Python library. Since the testbench is based on UVM, it adheres to the UVM standard. It also inherits the powerful features of UVM, such as reusability, scalability, and automation. As the design should consist of two parts, the bus wrapper (APB, AHB, etc.) and the IP, the testbench is also divided into two main environments: the Bus Environment and the IP Environment. Each environment is responsible for monitoring, driving, and collecting coverage for one part of the design. The two environments should then communicate with the reference model and the scoreboard. Each environment should have its separate sequence/sequences connected to its sequencer. If any dependency between the parts' sequences exists, it should be handled by the test.

### Environment
The enviroment component is used to encapsulates verification components. In this architecture, there are two enviroment classes; one for the bus wrapper; [bus_env](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_env.py) and the other for the ip itself; [ip_env](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_env.py). Both of them inheret from [UVMEnv](https://uvm-python.readthedocs.io/en/latest/comps/uvm_env.html) class.  

##### Components:
- Agent
- Coverage collector
- Logger.
##### Connection between components
- The agent send data to the coverage collector and logger. 
##### Connection with other components
- The environment should be able to send data to the scoreboard and reference model.
- The environment should be able to send and receive data from the sequence.
- The environment should be be connected with one of the design interfaces.

### Agent
The agent component is used to encapsulates a sequencer, driver, and monitor. In this architecture, there are two enviroment classes; one for the bus wrapper; [bus_agent](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_agent/bus_agent.py) and the other for the ip itself; [ip_agent](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_agent/ip_agent.py). Both of them inheret from [UVMAgent](https://uvm-python.readthedocs.io/en/latest/comps/uvm_agent.html) class.  

##### Components
- Sequencer
- Driver
- Monitor.
##### Connection between components
- Driver and sequencer should have bidirectional connection. 
##### Connection with other components
- Monitor should be able to send data outside of the agent. 
- Sequencer should be connected with sequence/sequences by the test.
- Monitor and driver should be connected to the design interface.

### Monitor
The monitor component is used to capture transactions and pass them to other components for further analysis or processing. It acts as a data capture mechanism within the testbench environment. There are three monitor classes in the bus enviromnt; one for AHBL bus wrapper [bus_ahb_monitor](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_agent/bus_ahb_monitor.py), one for APB bus wrapper [bus_apb_monitor](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_agent/bus_apb_monitor.py), and one for interrupts [bus_irq_monitor](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_agent/bus_irq_monitor.py). There is another monitor to capture transactions related to ip external interface; [ip_monitor](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_agent/ip_monitor.py). All monitors inheret from [UVMMonitor](https://uvm-python.readthedocs.io/en/latest/comps/uvm_monitor.html) class.

> **_NOTE:_** only one of the bus monitors (bus_ahb_monitor or bus_apb_monitor) is used in the test according to which wrapper is being verified  

##### Connection with other components
- Monitor should be able to send data outside of the agent.
- Monitor should be connected to an hdl interface.

### Driver
The driver component is used to drive transactions to the design under test (DUT). It interacts with the sequencer to fetch and execute the transactions. There are three drivers in the architecture; one to drive the AHBL bus ports [bus_ahb_driver](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_agent/bus_ahb_driver.py), one to drive APB bus ports [bus_apb_driver](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_agent/bus_apb_driver.py), the last one is to drive ports related to the ip [ip_driver](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_agent/ip_driver.py). All driver classes are inherited from [UVMDriver](https://uvm-python.readthedocs.io/en/latest/comps/uvm_driver.html) class.

> **_NOTE:_** only one of the bus drivers (bus_ahb_driver or bus_apb_driver) is used in the test according to which wrapper is being verified 

##### Connection with other components
- Driver should be able to send and receive data from the sequencer.
- Driver should be connected to an hdl interface.

### Sequencer
The sequencer component is used to control the flow of transactions between the driver and the DUT, as well as communicating with the sequence to coordinate the generation and execution of transactions. There are two sequencer one for the bus [bus_sequencer](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_agent/bus_sequencer.py) and the other for the ip [ip_sequencer](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_agent/ip_sequencer.py). Both of the sequencer inheret from [UVMSequencer](https://uvm-python.readthedocs.io/en/latest/seq/uvm_sequencer.html) class.

##### Connection with other components
- Sequencer should be able to send and receive data from the driver.
- Sequencer should be able to send and receive data from the sequence.

### Coverage
The coverage component is used to observe the transactions captured by the agent and extracting coverage information from them. There are two coverage classes; one for the bus [bus_coverage](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_coverage/bus_coverage.py) and the other for the ip [ip_coverage](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_coverage/ip_coverage.py). Both of the sequencer inheret from [UVMComponent](https://uvm-python.readthedocs.io/en/latest/seq/uvm_sequencer.html) class.

##### Connection with other components
- Coverage should be able to receive data from the agent/monitor.

### Logger
The logger component is used to capture transactions and store them in a log file. There are two logger classes; one for the bus [bus_logger](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_logger/bus_logger.py) and the other for the ip [ip_logger](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_logger/ip_logger.py). Both of the sequencer inheret from [UVMComponent](https://uvm-python.readthedocs.io/en/latest/seq/uvm_sequencer.html) class.

##### Connection with other components
- Logger should be able to send and receive data from the agent/monitor.

### Reference model
The [ref_model](https://github.com/efabless/EF_UVM/blob/main/ref_model/ref_model.py) is a golden model or a trusted source of expected behavior, against which the actual behavior of the DUT is compared. It provides a basis for verifying the correctness of the DUT's functionality.

##### Connection with other components
- Reference model should be able to be able to receive data from the two environments. 
- Reference model should be able to send expected data to the scoreboard.

### Scoreboard
The [scoreboard](https://github.com/efabless/EF_UVM/blob/main/scoreboard.py) is used to compare the actual results produced by the DUT with the expected results from the reference model. It helps in determining the correctness of the DUT's behavior by monitoring and analyzing the transactions and their outcomes.

##### Connection with other components
- Scoreboard should be able to receive data from the reference model.
- Scoreboard should be able to send data from the 2 environments.

### Test
The test manages the overall verification process. It coordinates the creation and execution of sequences, manages the test environment, and handles any dependencies between different parts of the testbench. Details of how to write a test is provided [here]().

### Sequence Item
UVM sequence itme is the representation of transaction-level data for verification in a Universal Verification Methodology (UVM) environment. It represents a single transaction or data item that is passed between all the relevant components, including the monitor, sequence, sequencer, driver, etc. It encapsulates the information and behavior related to a specific transaction within the testbench environment. In the architecture, there are two item classes, one for the bus [bus_item](https://github.com/efabless/EF_UVM/blob/main/bus_env/bus_item.py) and the other for the ip [ip_item](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_item.py). both of them inherets from [UVMSequenceItem](https://uvm-python.readthedocs.io/en/latest/seq/uvm_sequence_item.html) class. 

----
## IPs verified using EF_UVM

- [EF_UART](https://github.com/efabless/EF_UART) : A Universal Asynchronous Receiver Transmitter 
- [EF_GPIO](https://github.com/efabless/EF_GPIO8/tree/main) : A generic 8-bit General Purpose I/O (GPIO)
- [EF_TMR32](https://github.com/efabless/EF_TMR32) : A 32-bit timer and PWM generator

----
## Running tests
This section will discuss how to run tests for IPs which have an existing EF_UVM enviroment and what is the expected output. You can find a list for those IPs [here](). If you want to create UVM enviroment for a new IP, please refer to [this]() section.  

#### Prerequisites
- RTL design wrapped using [AMBA bus generator](https://github.com/shalan/IP_Utilities/tree/main/generators)
- python 3.7+
- [cocotb](https://github.com/cocotb/cocotb?tab=readme-ov-file#installation)
- [uvm-python](https://github.com/tpoikela/uvm-python?tab=readme-ov-file#uvm-library-for-python)
- docker

##### TODO: update this section after creating the new flow

#### Verify APB wrapper 

```shell
make run_all_tests
make run_<test_name>
make run_all_tests TAG=<new_tag> BUS_TYPE=APB
```

#### Verify AHBL wrapper 

```shell
make run_all_tests BUS_TYPE=AHB
make run_<test_name> BUS_TYPE=APB
make run_all_tests TAG=<new_tag> BUS_TYPE=APB
```

#### Results obtained
After running the test, a directory called ``sim`` will be created with the following structure.
```
└── <tag_name>
    ├── compilation
    │   └── sim.vvp
    ├── <Test1_name>
    │   ├── coverage.yalm
    │   ├── loggers
    │   │   ├── logger_bus.log
    │   │   ├── logger_ip.log
    │   │   ├── logger_irq.log
    │   │   └── regs_write.log
    │   ├── passed
    │   ├── results.xml
    │   ├── test.log
    │   ├── top_module.py
    │   ├── tr_db.log
    │   └── waves.vcd
    └── <Test2_name>
        ├── coverage.yalm
        ├── loggers
        │   ├── logger_bus.log
        │   ├── logger_ip.log
        │   ├── logger_irq.log
        │   └── regs_write.log
        ├── passed
        ├── results.xml
        ├── test.log
        ├── top_module.py
        ├── tr_db.log
        └── waves.vcd
    
```

#### TODO: explain the improtant output files

---
## Steps to verify new IP
To verify an IP using EF_UVM enviroment, all the components highlighted with red in the [architectutre]() should be updated. New classes specific to the IP will be created and they will inheret from the corressponding class. Then, the object type should be ovverridden in the test. Here are the steps to follow to create a test. 


### 1. Create verilog top level 
A verilog file that instantiate the wrapper and contains all the top level signal and information about how to dump the waves and time step should be added. An example of the top level module is provided [here](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/top.v). 

### 2. Create interface 
Interface mapping of the verilog signals to testbench is needed. This is done using by inherite from class [sv_if](https://github.com/tpoikela/uvm-python/blob/288b252228eedaa5967d552335f3692d3058cf3e/src/uvm/base/sv.py#L550) and mapping the signals to the testbench. You can check [uart_if](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/uart_interface/uart_if.py) for refrence. 

### 3. Create the item class
An item class for the ip should be created and should inherit from the [ip_item](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_item.py#L7) class. Three functions in the class should be overridden:
 - `__init__` function should have variables representing the item
 - `convert2string` return the string representation of the item
 - `do_compare` has condition to compare the item with the another item.

You can check [uart_item](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/uart_item/uart_item.py) for refrence. 

### 4. Create monitor class
A customized monitor class should be created and should inherit from [ip_monitor](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_agent/ip_monitor.py#L8) class. Mostly, only the run_phase function should be overridden. The monitor run phase should continuously observe the the design under test (DUT) interface and convert it to transaction level item (UVMSequenceItem). You can check [uart_monitor](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/uart_agent/uart_monitor.py) for refrence. 

### 5. Create driver class
A customized driver class should be created and should inheret from [ip_driver](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_agent/ip_driver.py#L8) class. Like the monitor, only the run_phase function should be overridden. In the run phase, the driver should recieve the UVMSequenceItem and convert it to pin-level signals to interact with the design under test (DUT). You can check [uart_driver](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/uart_agent/uart_driver.py) for refrence.

### 6. Create reference model 
A refrence model should be created which inherits from the [ref_model](https://github.com/efabless/EF_UVM/blob/main/ip_env/ref_model/ref_model.py#L8) class. The model primary role is to act as a representative or mimic of the actual hardware components, including the IP and the bus. You can check [ref_model](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/ref_model/ref_model.py) for refrence.

### 7. Create Sequences 
A sequence is a collection of UVM sequence items that will be used to drive the testbench. The sequence should be updated after each test. sequences should be connected to the sequencers as the testbench has 2 sequencers, usually 2 more sequences are needed.
- [] TODO: Add example from uart or any ip

### 8. Add functional Coverage 
A coverage class should be created and should inherit from [ip_coverage](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_coverage/ip_coverage.py#L8) class. The coverage component recieves transactions from the agent and should utilize [cocotb_coverage](https://cocotb-coverage.readthedocs.io/en/latest/tutorials.html) to create [Cover Points](https://cocotb-coverage.readthedocs.io/en/latest/tutorials.html) relative to the IP to ensure that all cases are covered. You can check [uart_coverage](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/uart_coverage/uart_coverage.py) and [uart_cov_groups](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/uart_coverage/uart_cov_groups.py) for refrence. 

### 9. Create Logger
A customized logger class should be created and should inheret from [`ip_logger`](https://github.com/efabless/EF_UVM/blob/main/ip_env/ip_logger/ip_logger.py#L8) class. Two functions in the class should be overridden:
 - `__init__` function should update ``self.header`` according to the ip sequence item
 - `logger_formatter` should return the relative components from the sequence item

You can check [uart_logger](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/uart_logger/uart_logger.py) for refrence.

### 10. Create Test 

The test should have the following:
1. asynchronus function with ``@cocotb.test()`` decorator. 
##### TODO [more explaination needed] 
2. Base test class which inherets from [UVMTest](https://uvm-python.readthedocs.io/en/latest/comps/uvm_test.html) class. 
##### TODO [more explaination needed] 
3. Test classes which inherets from the base test class and ovveride the run_phase function. In the run phase, sequence objects should be created and ``.start(<sequencer>)`` function should be used and the relative sequencer should be passed (either bus or ip sequencer).  

### 11. Create Makefile
You can copy this [Makefile](https://github.com/efabless/EF_UART/blob/main/verify/uvm-python/Makefile) as a refrence and Update the following:

- verilog files paths
- yaml/json file path
- tests names. 


##  Contributing

***TODO***

<details closed>
    <summary>Contributing Guidelines</summary>

1. **TODO**
</details>

---

##  License

**TODO**

---
