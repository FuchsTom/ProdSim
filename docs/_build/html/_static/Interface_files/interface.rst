.. _interface:

Interface Files
===============

This section describes the expected structure of the interface files and the corresponding default values of various
parameters. There are two interface files, which contain on the one hand the process data and on the other hand the
functions.

* :ref:`Data file <data_file>`
* :ref:`Function file <function_file>`

Furthermore, there is a small overview of the possible distributions/values that the freely selectable attribute of the
simulation objects can assume.

* :ref:`Attribute values <attr_values>`

.. note::
   The exceptions listed in the underlying sections, which are thrown when the data are not valid, can be divided into
   two groups. Firstly, those which actually lead to the termination of the program, because they are errors which are
   so serious that the data cannot be constructed correctly. On the other hand there are exceptions which are thrown and
   caught and then displayed when calling the function 'inspect'. These exceptions are errors, of a content nature.

....

.. toctree::
   :hidden:
   :maxdepth: 2

   data_file

   function_file

   attribute_values
