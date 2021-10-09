.. _1:

Example 01: Gearbox
-------------------

In this example, all steps are run through that should be conducted before each new simulation study. The focus is on
the actual procedure and less on the process itself. Therefore, the process functions, sources, sinks, and attributes of
the simulation objects are not filled with concrete content. Examples  :ref:`02<2>`, :ref:`03<3>`, and
:ref:`04<4>` focus on the concrete modeling of process functions and sources.

....

Process description
*******************

Before any simulation study, the production process should first be formally described. For assembly processes, the use
of a product tree is recommended to represent the product structure. The hierarchical relationship of the components
with each other and the individual quantities are displayed. As shown with the
:ref:`process functions<process_function>`,this simplifies the later access to the workpiece attributes starting from
the process functions. The following figure presents such a product tree using the example of a gearbox:

.. image:: ../Figures/product_tree_gearbox.png
   :align: center
   :width: 40%
   :alt: distribution_normal

In addition, the production process should be represented in the form of a network. All product components' final stores
(triangles) and all processing and assembly stations (circles) are drawn in. Then, all production processes are drawn in
by directed edges between the stations. In addition, for assembly processes, the edges for the assembly workpieces from
the final stores to the assembly stations are inserted.

.. image:: ../Figures/product_process_gearbox.png
   :align: center
   :width: 70%
   :alt: distribution_normal

....

.. _define_orders:

Define orders
*************

After describing the production process, the input files are defined. First, the orders should be specified in the JSON
file. For this purpose, an order is created for each element from the product tree. Even if the elements gearbox and
gear_shaft are not physical products but rather only namespaces for the union of elementary components, then these are
also defined as orders. Thus, attributes can be assigned to them later.

The following procedure is recommended when defining an order:

1. Set general information (*name*, *priority*, *storage*, *source*, and *sink*)
2. Describe the process of the order (*station*, *function*, *demand*, and *component*)
3. Add custom attributes

The corresponding orders are presented as follows. The storage capacity is limited to 10 for each order to avoid
unintentionally overfilling the computer memory.

.. code-block:: JSON

   {
     "order": [
       {
         "name": "gearbox",
         "storage": 10,
         "source": "source_1",
         "station": ["assemble_gb","quality_check"],
         "function": ["assemble_gb","quality_check"],
         "demand": [[1,8,1],2],
         "component": [["housing","screw","gear_shaft"],[]]
       },
       {
         "name": "housing",
         "source": "source_1",
         "storage": 10
       },
       {
         "name": "screw",
         "source": "source_1",
         "storage": 10
       },
       {
         "name": "gear_shaft",
         "storage": 10,
         "source": "source_1",
         "station": ["assemble_gs"],
         "function": ["assemble_gs"],
         "demand": [[6,1]],
         "component": [["gear","shaft"]]
       },
       {
         "name": "gear",
         "storage": 10,
         "source": "source_2",
         "station": ["heat_treatment"],
         "function": ["heating"],
         "demand": [8]
       },
       {
         "name": "shaft",
         "storage": 10,
         "source": "source_2",
         "station": ["lathe"],
         "function": ["turning"]
       }
     ]
   }

....

.. _define_station:

Define stations
***************

Next, the stations can be defined. For this purpose, a station object is created for each station in the production
process. Since stations do not have as many properties as orders, the following procedure is recommended:

1. Set general information (*name*, *storage*, *capacity*, and *measurement*)
2. Add custom attributes

Here, the capacities are also limited in order not to overfill the computer memory. In addition, the station
*quality_check* is a pure measuring station where no attributes are changed. Therefore, *measurement* is set to *true*
for this station.

.. code-block:: JSON

   {
      "station": [
       {
         "name": "lathe",
         "storage": 10
       },
       {
         "name": "heat_treatment",
         "storage": 10
       },
       {
         "name": "assemble_gs",
         "storage": 10
       },
       {
         "name": "assemble_gb",
         "storage": 10
       },
       {
         "name": "quality_check",
         "storage": 10,
         "measurement": true
       }
     ]
   }

....

.. _define_factory:

Define factory
**************

Finally, the global attributes and global functions must be defined. For this purpose, all attributes and global
functions are assigned to the *factory* object.

As an example, two global attributes and one global function are defined as follows:

.. code-block:: JSON

   {
      "factory": {
         "glob_attr_1": ["f",0],
         "glob_attr_2": ["n",1,0.1],
         "function": ["glob_func_1"]
      }
   }

....

.. _define_functions:

Define functions
****************

After the JSON file is set up, the Python script must be created. In this script, all previously used functions
(sources, sinks, process functions, global functions, and distributions) are defined. As this focuses on the procedure,
these functions are not assigned any content here. Therefore, examples  :ref:`02<2>`,
:ref:`03<3>`, and :ref:`04<4>` should be viewed.

....

.. _inspect:

Inspect
*******

After both input files are fully defined, the ``inspect()`` method can be called to identify errors that do not
terminate the program when reading the data. Before doing so, a simulation environment must be created and the
corresponding data read in.

.. code-block:: python

   from prodsim import Environment

   if __name__ == '__main__':

       # Create simulation environment
       env = Environment()

       # Read in the process data
       env.read_files('.data/process.json', './data/function.py')

       # Inspect the process data
       env.inspect()

In the following example, two errors were deliberately introduced in the JSON file. First, the signature of the process
function ``turning`` was changed, and the global function ``global_func_1`` did not yield a timeout event. After calling
``inspect``, the output was as follows:

.. code-block:: none

   progress station: [====================] 100%  quality_check
   progress order:   [====================] 100%  shaft
   factory:          [====================] 100%  factory
   WARNINGS-------------------
   Traceback (most recent call last):
     File "/Users/user/prodsim/inspector.py", line 522, in __inspect_order
       warnings.warn(
           prodsim.exception.BadSignature: The signature of a process function should be (env, item, machine,
           factory), but in the function 'turning' at least one argument has a different name.

   EXCEPTIONS-----------------
   Traceback (most recent call last):
     File "/Users/user/prodsim/inspector.py", line 575, in __inspect_factory
       raise prodsim.exception.InvalidFunction(
           prodsim.exception.InvalidFunction: The function 'glob_func_1' from the
           function file is not a generator function. A global function must yield at least one timeout-event.

   ---------------------------
   Number of Warnings:    1
   Number of Exceptions:  1
   ---------------------------

....

.. _visualize:

Visualize
*********

Finally, the ``visualize`` method can be called to check if the process was defined correctly.

.. code-block:: python

   # Visualize the process data
   env.visualize()

This call leads to the following output:

.. code-block:: none

   Dash is running on http://127.0.0.1:8050/

    * Serving Flask app 'ProdSim_app' (lazy loading)
    * Environment: production
      WARNING: This is a development server. Do not use it in a production deployment.
      Use a production WSGI server instead.
    * Debug mode: on

By clicking on the link, a browser window opens that presents the interactive network graph.

.. image:: ../Figures/screenshot_web_app.png
   :align: center
   :width: 90%
   :alt: distribution_normal
