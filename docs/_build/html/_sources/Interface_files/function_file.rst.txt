.. _function_file:

Function file
-------------

The function file is a .py file in which the user can fill all functions used in the data file with content. All
functions defined here can be differentiated into three categories:

* :ref:`process function <process_function>`
* :ref:`source and sink <source_sink>`
* :ref:`global function <global_function>`

As the names already indicate, process functions are functions that describe a machining process of an item on a
machine of a station. Source and sink functions describe how many workpieces are fed into the system and when. The
global functions are functions to influence the behavior of the global attributes. In the following the required
structure of the respective functions is described.

....

.. _process_function:

Process function
****************

Process functions are functions that describe the behavior of the workpiece and station/machine attributes during
machining depending on the current workpiece and station properties. In order to be able to define the change of the
attributes, one can fall back in these functions on the attributes of the workpiece, the station, the factory and the
simpy.environment (i.e. the simulation time). In addition to changing the attributes, the processing time should also be
taken into account here, because the simpy.environment can be used to block the machine for other workpieces for a
certain period of time using the 'timeout' method. If no timeout event is yielded, then this corresponds to a processing
which needs no time and thus the resource is blocked also only for a time and no time span.

As the following example shows, process functions must always have exactly 4 parameters. The first parameter should be
named 'env' to avoid user errors and via this the simpy.environment and its attributes can be reached. The second
parameter is 'item'. With this you can access all user defined attributes corresponding to this item in the data file.
The next parameter is 'station' which, as with the items, can be used to access the current properties of the machines
of a station. The last parameter is 'factory' which gives access to all global attributes.

To see which exceptions are thrown when there are faulty functions see the following :ref:`section <function>`.

To give an example of a possible function, assume that a shaft is to be turned on a lathe. The shaft has a surface
quality and the lathe has an attribute wear and eccentricity of the spindle. One can now choose different approaches to
integrate a process model of the machining.Here we assume that we know a process function (here fictitious), which
describes the surface quality after machining in dependence of the parameters 'wear', ' eccentricity', as well as a
global parameter 'temperature'. The machining process is normally distributed and takes on average 3 minutes with a
standard deviation of 0.2. If the wear on the machine is greater than 1, then the desired quality cannot be achieved and
maintenance is carried out before machining, which resets the wear to zero. This operation lasts exactly 5 minutes. In
addition, the wear increases in a normally distributed manner with each machining operation. To track the power
consumption, the global parameter is updated before and after the machining.

.. code-block:: python

   from random import normalvariate

   def shaft_on_lathe(env: simpy.Environment, item: Item, machine: Machine, factory: Factory):

       # Maintenance when wear is too great
       if machine.wear > 1:
           machine.wear = 0
           yield env.timeout(5)

       # Update global parameter
       factory.energy_usage_sector_1 += 10

       # Calculate the new attributes using a process function
       item.surface_quality = machine.wear * 0.8 (factory.temperature + 273) / 100 + machine.eccentricity

       # Blocking the resource for the processing time
       yield env.timeout(normalvariate(3, 0.2))

       # Update global parameter
       factory.energy_usage_sector_1 -= 10

The following table gives a small overview of the different Parameters of a process function.

.. list-table:: Overview: process function
   :header-rows: 1

   * - Parameter name
     - Type
     - Usage
   * - env
     - simpy.Environment
     - block resource via yield env.timeout(delay=value)
   * -
     -
     - access simulation time via env.now
   * - item
     - Item
     - access user defined item attributes
   * - station
     - Station
     - access user defined item attributes
   * - factory
     - Factory
     - access global attributes

Finally, it should be noted that in the case when several items are being processed at the same time on one station, the
parameter item is of the type List[Item] and the list contains all the workpieces appearing during the processing. The
access to the attributes must be adapted accordingly.
Also we refer to assemblies, because assembled workpieces can be accessed via 'item.assembly_item_name', which of course
have further attributes (tree structure).

....

.. _source_sink:

Source and Sink
***************

Sources and sinks are used to insert workpieces into the system and to remove finished workpieces after machining. Each
workpiece has a source and a sink. If no sources are specified by the user, then default sources are activated, which
ensure that the process is always started when stations or machines are available.

Sources place new workpieces with freshly generated attribute values (according to the distribution defined by the user)
in the store of the first station, the process chain of the respective item type.
Sinks remove finished workpieces from the end storage of the respective item type.

As the following example shows, sources and sinks get the simpy.environment as their only passing parameter, which is
used to define time intervals between two store accesses.

To see which exceptions are thrown when there are faulty functions see the following section for :ref:`source <source>`
and :ref:`sink <sink>`.

Since sources and sinks essentially function in the same way, only an example of a source is given here, which is
supposed to exhibit the following behavior as an example. It is assumed that the time steps are in hours (any other time
unit can be used by simple transformations). During the day shift (8:00-20:00) every ten minutes three workpieces are to
be placed in the memory of the first station of the corresponding item type. During the night shift, exactly one
workpiece should be placed every fifteen minutes.

.. code-block:: python

   def source_1(env: Environment):

       # Check if there is a night shift
       if env.now % 24 < 8 or env.now % 24 > 20:
           yield env.timeout(15)
           yield 1
       # 'yield 1', works like 'return' in a regular function

       # Day shift
       yield env.timeout(10)
       yield 3


Each time a source function or a sink function is called, a generator is created from it, which is iterated over until
an object of type 'int' is yielded. Therefore it is always necessary that with each possible iteration first an object
of the type 'simpy.Timeout' is yielded and then an object of the type 'int'. Since the iteration is aborted when an
'int' yield statement is reached, 'yield int_object' has the same function as a 'return' statement.

.. list-table:: Overview: source and sink
   :header-rows: 1

   * - Parameter name
     - Type
     - Usage
   * - env
     - simpy.Environment
     - block resource via yield env.timeout(delay=value)
   * -
     -
     - access simulation time via env.now

....

.. _global_function:

Global function
***************

Global functions are used to control the global parameters. Even process functions can also read and assign new values
to the global parameters within, however this brings some problems with itself, because one assigns
global parameter from these process functions with new values, then the resulting behavior is only with difficulty to
estimate, because one does not know always apriori how often and when exactly this function is called (in particular if
one integrates coincidence with into the system). In addition, you have no flexible access to the values via the process
functions, because assuming you want to have a global parameter 'temperature', which follows a certain course, then you
have access to this course via the process functions, but cannot define the course itself. The reason for this is that
the process functions are always called only in the discrete time steps as they are specified by the editing process.
This problem is solved by the global functions, as the following example shows.

global functions get exactly two parameters. One is the simpy.environment, which is used to access the time, and the
other is a factory object, which is used to access the global attributes.

As an example, suppose you want to have a global parameter 'temperature' that follows a step history over time. Again,
the unit of time is assumed to be hours.

.. code-block:: python

   def global_temperature(env: simpy.Environment, factory: Factory):

       def is_in(time, lower_bound, upper_bound):
           if time % 24 > low_bound and time % 24 < upper_bound:
               return True
           return False

       if is_in(env.now,0,8):
           factory.temperature = 18
       elif is_in(env.now,8,14):
           factory.temperature = 22
       elif is_in(env.now,14,20):
           factory.temperature = 23
       else :
           factory.temperature = 19

       yield env.timeout(0.5)

It is important that at least one 'simpy.timeout' event is yielded on each run. It is not allowed to yield an object
that is not of type 'simpy.Timeout'. The delay specified in the timeout event indicates how large the time jump between
two update calls should be.

Of course, it is also possible to model much more complex behavior of global variables, for example, any thermodynamic
models that determine the course of temperature as a function of the temperature itself and other global attributes,such
as the power consumption of the machines.

.. list-table:: Overview: global function
   :header-rows: 1

   * - Parameter name
     - Type
     - Usage
   * - env
     - simpy.Environment
     - block resource via yield env.timeout(delay=value)
   * -
     -
     - access simulation time via env.now
   * - factory
     - Factory
     - access global attributes
