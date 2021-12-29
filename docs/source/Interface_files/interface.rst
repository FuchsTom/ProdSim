.. _interface:

Interface Files
===============

This chapter defines the structure of the two input interface files and the options available to the user for mapping
production processes. First, the elements of the JSON file describing the simulation objects are presented, followed by
the different function types of the py file.

* :ref:`Data file <data_file>`
* :ref:`Function file <function_file>`

A further section describes the possible distributions used to initialize the attributes of simulation objects when they
are created.

* :ref:`Attribute values <attr_values>`

.. note::
   A subset of the exceptions listed in the following sections will only be thrown when the inspect method is called.

....

.. toctree::
   :hidden:
   :maxdepth: 2

   data_file

   function_file

   attribute_values

   output_file
