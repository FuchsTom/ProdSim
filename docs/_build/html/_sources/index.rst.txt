
.. image:: ./source/Figures/logo.png
   :width: 100%
   :alt: logo

....

Overview
========

ProdSim is a process-based discrete event simulation for production environments based on the
`SimPy <https://simpy.readthedocs.io/en/latest/>`_ framework. The package is designed to generate large high-resolution
synthetic production data sets.

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

.. code-block:: python

   from prodsim import Environment

   def main():

       # Create simulation Environment
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

How this documentation should be used:

The :ref:`API Reference <api>` chapter provides an overview of all methods and their attributes as well as the
corresponding data types. The  :ref:`Interface Files <interface>` chapter describes the structure to be followed by the
input files. These two chapters are designed as a reference for specific content. In the final
:ref:`Examples <examples>` chapter, examples are chronologically matched to the later simulation study and contain all
elementary features of the package. Since some modeling techniques are also explained, studying these examples is
recommended before conducting one’s own simulation study.

....

Table of Contents
=================

.. toctree::
   :includehidden:
   :maxdepth: 2

   ./source/API/api

   ./source/Interface_files/interface

   ./source/Defining_processes/defining_processes

   ./source/Examples/examples
