# Example 03

## Table of Contents 

* [Purpose of this example](#purpose)
* [The modeled process](#process)
* [File structure](#file_structure)
* [For trying out](#try_out)

## <a id="purpose"></a>Purpose of this example

The focus of this example is on the definition of the source and sink function. It is shown how an infinite source can 
be defined to model a pull-driven manufacturing process. In addition, global attributes will be used to control the 
process. 
  
## <a id="process"></a>The modeled process

To demonstrate the functionality of the source and sink, the simplest possible process is used, which is shown below and 
consists of only one station. 

![bolt process](./figures/bolt_process.png "Bolt process")

This station consists of 5 forges, which can be activated or deactivated without delay, each producing 6 bolts per time 
unit. The aim is to control the stock so that it does not become too large, but the demand can always be met (it is 
fictitiously assumed that the course of demand over time is unknown).

## <a id="file_structure"></a>File structure

```
. example03
|--data/
| |--function.py
| |--process.json
|--figures/
| |--bolt_process.png
|--output/
| |--demand_profil_pre_run.png
|--example03.py
|--README.md
```

The folder ``example03`` already contains all the files needed to run the simulation. The subfolder ``data`` contains 
the two input files in which the production process is defined. In the script ``example03`` the input files are loaded 
in a newly created simulation environment, and the simulation is started. In addition, the script contains a function 
for plotting the simulation data. After the simulation, the exported simulation data is stored in the ``output`` 
subfolder. This folder also contains an image of the expected output.

## <a id="try_out"></a>For trying out

During the simulation, a progress bar should appear that scrolls from 0% to 100%. 

```
simulation progress: [====================] 100%
```

After the simulation is finished, the ``factory.csv`` file should appear in the output order. This folder also contains 
a plot of the data from a simulation that has already been run. 

To get a better understanding of the interaction between source and sink, it is recommended especially to vary the sink 
function and to run the simulation again (Attention: the output files which have been created before have to be deleted, 
because they might not be overwritten). The generated output data can be plotted using the function ``plot_demand`` 
(Attention: to call this method pandas, numpy and matplotlib must be installed).

Note: When the ``inspect()`` method is called the following output will be printed. This warning is generated because 
the used source is an infinite source, which leads to infinite loops if the corresponding storage capacities are not 
limited.  

```
progress station: [====================] 100%  forge
progress order:   [====================] 100%  bolt
factory:          [====================] 100%  factory
WARNINGS-------------------
Traceback (most recent call last):
  File "/Users/user/Documents/prodsim/inspector.py", line 306, in __inspect_order
    warnings.warn(
prodsim.exception.BadYield: The type of the first yielded object of the source/ sink 'infinite_source' is not 
'simpy.Timeout', this could lead to an infinite loop.

EXCEPTIONS-----------------
---------------------------
Number of Warnings:    1
Number of Exceptions:  0
---------------------------
```