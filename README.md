# ProdSim - ReadMe

## Table of contents 

1. [Introduction](#introduction)
1. [Installation](#installation)
1. [Requirements](#requirements)
1. [Documentation](#documentation) 
1. [Examples](#examples)
1. [Source code](#sourcecode)

## <a id="introduction"></a>Introduction

ProdSim is a process-based discrete event simulation for production environments based on the 
[SimPy](https://simpy.readthedocs.io/en/latest/contents.html) framework. The package is designed to generate large 
high-resolution synthetic production data sets.

The characteristics of a production system are represented by three system components, namely machines, workpieces, and 
a factory. These components interact with one another on the following three system layers:

* logistics 
* stations
* processes

The bottom level, namely the process level, models elementary assembly or machining operations in which the properties 
and behavior of the system components can be influenced. The middle level, namely the station level, maps the system’s 
buffer stores and groups machines together into stations according to a workshop or line production. At the top level, 
namely the layout level, workpieces are created by sources and removed by sinks. In addition, the material flow of 
workpieces through the production process is described.

Users must define production processes in two input files. In a JSON file, all orders, stations, and the factory are 
defined. In a Python script, the users specify the assembly and processing functions, the behavior of the sources and 
sinks, as well as global functions and user-defined distributions for attribute values.

Additionally, the package offers functionalities for the visualization of passed production processes, verification of 
input files, and methods for estimating the simulation runtime

The following code displays the typical usage of the package:

```python 
from prodsim import Environment 

def main():
    
    # Create simulation environment
    env = Environment()
    
    # Read the input files
    env.read_files('./data/process.json', './data/function.py')
    
    # Inspect and visualize the input data (optional)
    # env.inspect()
    # env.visualize()

    # Start the simulation
    env.simulate(sim_time=10_000, progress_bar=True, max_memory=5, bit_type=64)

    # export the output data
    env.data_to_csv("./data/output/", remove_column=['item_id'], keep_original=True)

if __name__ == '__main__':
    
    main()
```

## <a id="installation"></a>Installation 

---
**NOTE**

The program, as well as the installation described below, was tested for the operating systems Win10 and macOS. A 
current Python version (>=3.8.0) is required.

---

Since the installation of ProdSim includes some additional [packages](#requirements), it is recommended to install 
ProdSim in its own (virtual) environment. This environment can be created for example with the standard library venv. In 
the following the recommended and tested installation is described step by step. Of course, the program can also be 
installed in other ways as desired, this is left to the user.

1. cd to the directory in which the environment should be created 
   
    macOS: ``cd path``
    
    Win10: ``cd path``

1. Create a new environment 

    macOS: ``python3 -m venv ProdSim_venv``
      
    Win10: ``py -m venv ProdSim_venv``

1. Activate the environment
    
    macOS: ``source ProdSim_venv/bin/activate``
    
    Win10: ``ProdSim_venv\Scripts\activate``

1. Install ProdSim
  
    macOS: ``pip install path_to_ProdSim/dist/ProdSim-0.1.0.tar.gz``

    Win10: ``pip install path_to_ProdSim\dist\ProdSim-0.1.0.tar.gz``

To check if the installation was successful, the following Python script can be created and executed outside the 
``ProdSim`` folder. Thereby the environment in which ProdSim was installed must be active. If the installation was not 
successful, a ``ModuleNotFoundError`` is displayed. 

```
from prodsim import Environment 

env = Environment() 
```

---
**NOTE**

When using an old version of pip, a parse error may occur during installation. It is recommended to use the latest 
version of pip. 

Since ProdSim (including the required third party libraries) is installed in its own environment, it must be ensured 
that the correct interpreter is selected when executing a script. 

The easiest way is to run the script from an IDE and specify the interpreter in the settings (MacOS: 
``ProdSim_venv/bin/python``, Win10: ``ProdSim_venv\Scripts\python``). If the script should be executed from the 
terminal, it is sufficient with MacOS if the corresponding environment is active. With Win10, the path to the desired 
interpreter must be specified for each call: 

```
> ProdSim_venv\Scripts\python path_to_script\script.py  
```

---

Alternatively it is also possible to install ProdSim without the package manager pip with ``python setup.py install``. 
This is not recommended since external libraries may not be installed correctly automatically.

## <a id="requirements"></a>Requirements

The following packages are automatically installed in the current environment when ProdSim is installed via pip:

| Library              | Usage                                   | Version               | 
| -------------------- | --------------------------------------- | --------------------- |
| simpy                | simulation kernel                       | \>= 4.0.1             |
| numpy                | internal tracking of simulation objects | \>= 1.21.2            |
| dill                 | plotting the simulation data            | \>= 0.3.4             |
| h5py                 | internal caching of simulation data     | \>= 3.4.0             | 
| dash, dash_cytoscape | visualization of the production process | \>= 2.0.0, \>= 0.3.0  |

## <a id="documentation"></a>Documentation

The documentation is hosted via read the docs: 

`` https://prodsim.readthedocs.io/en/latest/index.html ``

Alternatively, the documentation can be downloaded: 

* pdf: `` /ProdSim/docs/_build/latex/prodsim.pdf ``
* html: `` /ProdSim/docs/_build/html/index.html ``

## <a id="examples"></a>Examples

In ``/ProdSim/examples`` five ready executable examples are contained. The examples 01 to 04 correspond to the examples 
from the documentation and offer the possibility to reproduce and execute what is described in the documentation. The 
example ``example_bulb`` contains the two input files from the example process described in the bachelor thesis. These 
files can be used to fill the light bulb production with process functions and to analyze them as needed. 

## <a id="sourcecode"></a>Source Code

The complete source code can be found at ``/ProdSim/prodsim/`` and contains the following files:

```
. /ProdSim/prodsim/
|--__init__.py
|--__pychache__/
|--_estimate_process/
|--_temp_data/
|--app/
|--components.py
|--environment.py
|--estimator.py
|--exception.py
|--filehandler.py
|--helper.py
|--inspector.py
|--simulator.py
|--tracker.py
|--visualizer.py
```

The folders ``_estimate_process`` and ``_temp_data`` are also installed during the installation. 
``_estimate_process`` contains a set of input files which are used to perform the estimation measurements of the 
estimator. In ``_temp_data`` the h5 file with the simulation data is cached during the simulation run.
