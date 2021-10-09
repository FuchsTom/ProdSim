.. _data_file:

Data file
---------

The process data file is a .json file in which the user can set all the information about the structure of the process.
The file consists of one large object, which has three properties.

1. :ref:`Item <item>`
2. :ref:`Station <station>`
3. :ref:`Environment <environment>`

The following describes what these properties should look like and which parameters can be set.

....

.. _item:

Item
****

The property item itself is an array attribute of the top-level object. This array holds objects, representing different
types of items. Those item objects hold all the attributes this particular item should have. There are two different
types of attributes. Firstly, those that are predefined by the system and secondly, those that can be freely selected
by the user and describe the properties of the objects. The names of the freely chosen attributes must not collide with
those of the default attributes.
After the following example, by setting once all possible parameters and two free attributes and once only the name and
one free attribute, the default attributes are predefined.

.. warning::
   The following example is not a valid data file because only the item attribute is included for clarity. A valid
   file should at least contain the attribute station. Also not all items used in an assembly are defined in the
   item-array.

.. code-block:: JSON

   {
     "item": [

       {
         "name": "crankshaft",
         "length": ["n",450,0.1],
         "crack": ["b",0.1],
         "station": ["assembly_station_1", "assembly_station_2", "quality_control"],
         "function": ["assembly_1", "assembly_2", "quality_check"],
         "demand": [[1,2], [4], 10],
         "component": [["shaft","bearing"], ["rod"], []],
         "priority": 1,
         "sink": "sink_1",
         "source": "source_1",
         "storage": 100
       },

       {
         "name": "shaft",
         "surface_quality": ["n",1,0.1],
       }

     ]
   }

``name``

The name is the only mandatory parameter. It should be of type string, but other types will not cause errors in the
program. It is important that the name is unique and unambiguous.

.. list-table:: Overview: name
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - no
     -
   * - default value
     - /
     -
   * - Exceptions
     - MissingParameter
     - If name was not set
   * - Warnings
     - BadType
     - If name isn't a string

``priority``

The Priority is used to put all workpiece types in an ordered sequence. This is needed when two workpiece types are to
use a scarce resource at the same time and it must be decided which type is to be prioritized. If two types have the
same priority and use the same resources, the expected behavior of the system is not determined. The priority is an
integer greater than zero, with smaller values corresponding to a higher priority.

.. list-table:: Overview: priority
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - 10
     -
   * - Exceptions
     - InvalidType
     - If priority isn't an integer
   * -
     - InvalidValue
     - If priority is less than one

``storage``

The storage is a positive integer that indicates the storage capacity of the store in which workpieces of this type are
stored after processing at the last station. This storage space is resaved only for workpieces of this particular type.

.. list-table:: Overview: capacity
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - infinite
     -
   * - Exceptions
     - InvalidType
     - If capacity isn't an integer
   * -
     - InvalidValue
     - If capacity is less than one

.. _source:

``source``

Source is a generator function that creates new workpieces and places them in the buffer memory of the first station.
The source function gets passed exactly one argument, which is simpy's underlying environment for the simulation. This
argument should be named 'env' (other names only trigger warnings, but are not good practice).

The function must have a certain structure, by means of which one can model many different scenarios. With each call of
this function it must always be ensured that first a simpy.Timeout event is yielded (otherwise an infinite loop can
occur) and then an 'int' value, which stops the iteration via the generator. The timeout event determines the delay
between two deliveries and the 'int' value determines the amount of workpieces that are put into the buffer memory
during a delivery. By means of the attribute 'now' of the environment 'env' one can access the current simulation time
and thus achieve behavior in dependence of the time.

The first example is a simple source, which sends 2 units into the system every five time units. In the second example,
assume that the unit of time is hours. Then this source sends one piece every half hour in the period from 10 o'clock in
the evening to 6 o'clock in the morning, and 2 pieces every ten minutes in the other time period.

The default source will ensure that always, exactly the number of required workpieces are in the buffer memory.

.. code-block:: python

   def source_1(env: simpy.Environment):
       yield env.timeout(5)
       yield 2

   def source_2(env: simpy.Environment):

       if env.now % 24 < 6 or env.now % 24 > 22:
           yield env.timeout(0.5)
           yield 1

       yield env.timeout(0.1)
       yield 2

.. list-table:: Overview: source
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - infinite source
     - Ensures always enough workpieces
   * - Exceptions
     - UndefinedFunction
     - Function is not defined in the passed file
   * -
     - InvalidFunction
     - Function is not a generator function
   * -
     - InvalidSignature
     - Function has not exactly one argument
   * -
     - InvalidYield
     - Function doesn't yield Timeout and int
   * -
     - InvalidValue
     - Amount isn't greater than zero
   * - Warnings
     - BadSignature
     - Argument isn't called 'env'

.. _sink:

``sink``

The sink is a generator function that has the task of removing workpieces from the final store of each workpiece type.
The sink function gets passed exactly one argument, which is simpy's underlying environment for the simulation. This
argument should be named 'env' (other names only trigger warnings, but are not good practice).

The function must follow a certain structure, which allows it to flexibly represent many different scenarios.
In every possible case, the function must always yield an object of the type 'simpy.Timeout' first. This timeout event
specifies how long to wait between two accesses to the store. After a timeout object has been yielded, an object of
type 'int' must be yielded, which specifies how many workpieces are to be removed from the store. If it comes to the
case that an 'int' was yielded the iteration is aborted.

The logic behind implementing a sink is the same as for a source. For an example see :ref:`source <source>`.

.. list-table:: Overview: sink
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - infinite source
     - If item is not part of an assembly process
   * -
     - no source
     - If item is part of an assembly process
   * - Exceptions
     - UndefinedFunction
     - Function is not defined in the passed file
   * -
     - InvalidFunction
     - Function is not a generator function
   * -
     - InvalidSignature
     - Function has not exactly one argument
   * -
     - InvalidYield
     - Function doesn't yield Timeout and int
   * -
     - InvalidValue
     - Amount isn't greater than zero
   * - Warnings
     - BadSignature
     - Argument isn't called 'env'

``station``

Station is a list representing the stations in the order this particular type of item uses them. To reference the right
station the user passes the name as string of the corresponding station. Inside the program this string gets replaced by
the concrete StationData object. This isn't very elegant, but in the simulation module this results in short attribute
access calls.

Since the station list is handled as a reference in terms of number of process steps here no exception is raises, if
this list isn't as long as the other process lists (function, demand, component). Only if there length doesn't fit the
number of stations an exception is raised.

The only exception is raised here, when the referenced station isn't defined in the data file.

The default value is an empty list. In this content this means, that the source directly feeds the final store of an
item without any additional processing steps.

.. note::
   Here initially no exceptions are thrown if the length of station and function differ. This is only done for function to exclude redundant error messages.

.. list-table:: Overview: station
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - []
     -
   * - Exceptions
     - UndefinedObject
     - no station is defined with this name

.. _function:

``function``

The functions represent the interface where the user can define how the concrete process will look like. Here you can
access all the attributes of the used machine of station and the workpieces involved in the process, as well as the
properties of the factory and simpy environment.

The function gets exactly four parameters, whose order is mandatory. The names are freely selectable, but a warning is
given if the structure (env, item, machine, factory) is washed away. The first argument 'env' can be used to access the
simpy environment and env.now to refer to the simulation time. The second attribute is a reference to the workpieces
involved in the machining. 'machine' is the reference for the station attributes of a particular machine. The last
attribute 'factory' can be used to read or modify the global parameters.

Each process function should contain 'yield env.timeout(x)' at least once to block the station as a resource for a
period of time. It is possible to use this yield statement several times, for example, as shown below in the case when
there is maintenance besides processing because certain Parameters have run out of allowable.

An exception is also thrown if the number of functions does not match the number of stations.

.. code-block:: python

   def process_function(env: simpy.Environment, item: Union[Item, List[Item]], station: Station, factory: Factory):

        if station.wear > 8.2:
            station.wear = 0
            yield env.timeout(1.2)

        item.surface_quality = station.wear * 0.8 * factory.temperature / 100
        yield env.timeout(0.5)

.. list-table:: Overview: function
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - []
     -
   * - Exceptions
     - UndefinedFunction
     - No function with this name is defined
   * -
     - InvalidFunction
     - Function is not a generator function
   * -
     - InvalidSignature
     - Function doesn't have four arguments
   * -
     - InvalidYield
     - Function must yield a simpy.Timeout object
   * -
     - MissingParameter
     - Number stations doesn't match number of stations
   * -
     - MissingAttribute
     - Non defined Attribute is referenced
   * - Warnings
     - BadSignature
     - At least one argument has a bad name

.. _demand:

``demand``

The attribute demand is a list that specifies how many units of various workpiece types are required in a process step that corresponds to the index of the list. The list contains two different types of entries.

If there is no assembly in the corresponding process step but a pure machining, then the list contains an integer at the corresponding index position, which indicates how many workpieces this station requires per machining.

If, on the other hand, there is an assembly, then the element at the corresponding index position is of the type list, which itself contains integers. These integers correspond to a kind of parts list, which specifies how many assembly objects of different types are required. Which types these are is defined in the corresponding index position in the list component.

If the entire process chain consists only of machining operations where always one item is passed (line production), then this attribute does not need to be set and a list of only ones pages with the appropriate length is generated.

.. note::
   Here initially no exceptions are thrown if the strucutre of demand and component differ. This is only done for component to exclude redundant error messages.

.. list-table:: Overview: demand
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - [1, 1, .., 1]
     - Only possible if there is no assembly
   * - Exceptions
     - MissingParameter
     - Number elements doesn’t match number of stations
   * -
     - InvalidType
     - If list contains different objects than int or list of int
   * -
     - InvalidValue
     - Integer element in list isn't greater than zero


``component``

The list component has the same structure as the list demand. It supplements the list demand with the information, which workpiece types are to be assembled in case of an assembly process. This list contains only elements of the type list, which however can be differentiated into two cases.

If only one workpiece type is processed in a machining step, this list contains an empty list at the corresponding index position.

In the case of an assembly, the list contains the names of the workpieces to be assembled.

The lengths of the assembly items must of course correspond to the corresponding lists of the :ref:`demand lists <demand>`.

If the entire process chain consists only of machining operations, then this attribute does not need to be set and a list of empty pages with the appropriate length is generated.

If the whole process chain only

.. list-table:: Overview: component
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - [[], [], .., []]
     - Only possible if there is no assembly
   * - Exceptions
     - MissingParameter
     - Number elements doesn’t match number of stations or length of assembly process list doesn't mach length of assembly demand list
   * -
     - UndefinedObject
     - no item is defined with this name
   * -
     - InvalidValue
     - Structure doesn't correspond to demand structure
   * -
     - InvalidType
     - List contains object with other type then 'list'

``attribute``

All parameters that are set by the user and do not belong to the default parameters described above are considered as
user-defined attributes. The following :ref:`section <attr_values>` provides an overview of the features that may be
used in these attributes.

....

.. _station:

Station
*******

The property station itself is an array containing any number of objects, each of them being a separate type of station.
These station objects then contain all the properties that the corresponding station should have in the simulation.
A station can have two types of properties. On the one hand, those that are defined by the system by default and those
that are freely defined by the user. Every attribute that is not from the list of default attributes is automatically
considered as a user-defined attribute.
It should be noted that the freely selectable attributes must not overwrite the names of the default attributes.
Before explaining all the pre defined default properties that such a station object have, a small example of a
corresponding file containing two different stations is shown.

.. warning::
   The following example is not a valid data file because only the station attribute is included for clarity. A valid
   file should at least contain the attribute item.

.. code-block:: JSON

   {
     "station": [

       {
         "name": "mill",
         "capacity": 2,
         "storage": 25,
         "wear": ["f",0],
         "temperature": ["n",23,0.5]
       },

       {
         "name": "lathe",
         "prob_of_failure": ["f",0.01],
       }

     ]
   }

``name``

The name is a mandatory parameter that a station must have. It is recommended to use a string as data type, but other
data types do not cause errors in the program. Since it is not an optional parameter there is no default value.

.. list-table:: Overview: name
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - no
     -
   * - default value
     - /
     -
   * - Exceptions
     - MissingParameter
     - If name was not set
   * - Warnings
     - BadType
     - If name isn't a string

``capacity``

The capacity indicates the number of machines in a station. If a workpiece is processed on a station, one of the
available machines is selected. The capacity must be an integer and must not be less than one.

.. list-table:: Overview: capacity
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - 1
     -
   * - Exceptions
     - InvalidType
     - If capacity isn't an integer
   * -
     - InvalidValue
     - If capacity is less than one

``storage``

Storage indicates the storage location in the station's buffer memory. When a workpiece is waiting to be processed, it
is temporarily stored in this store. The storage must be an integer and must not be less than one.

.. list-table:: Overview: storage
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - infinite
     -
   * - Exceptions
     - InvalidType
     - If storage isn't an integer
   * -
     - InvalidValue
     - If storage is less than one

``attribute``

All parameters that are set by the user and do not belong to the default parameters described above are considered as
user-defined attributes. The following :ref:`section <attr_values>` provides an overview of the features that may be
used in these attributes.

....

.. _environment:

Factory
*******

Factory is also an attribute of the top-level object of the input file. Unlike item and station, however, factory is
optional and not an array, but an object. factory, like workpiece or station types, also has default and free attributes
that can be set by the user. The special feature of the free attributes of the object factory is that these attributes
are global attributes, i.e. they are available in every process function defined by the user. In addition, the value can
be also reassigned from any process function. Furthermore, global functions can be defined here, which are called in an
infinite loop in the simulation. These functions have no parameters.

In the following all default parameters are described in more detail and finally the free attributes.

.. warning::
   The following example is obviously not a valid input file. It should only show the structure of the attribute
   'factory'.

.. code-block:: JSON

   {
     "factory": {
        "temperature_sector_1": ["n",23,0.8],
        "temperature_sector_2": ["n",22.2,1],
        "energy_usage": ["f",0],
        "function": ["global_function_1", "global_function_2"]
      }
   }

``function``

Function is a list containing functions that are called in an infinite loop in the simulation. These functions can be
used to control global parameters. Each global function gets exactly two parameter, which should have the name 'env'
and 'factory'. with the first parameter 'env' the simpy.Environment can be accessed to yield timeout events or access
the current simulation time. With the secund parameter you get access to all global parameters.

.. list-table:: Overview: function
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - optional
     - yes
     -
   * - default value
     - []
     -
   * - Exceptions
     - UndefinedFunction
     - No function with this name is defined
   * -
     - InvalidFunction
     - Function is not a generator function
   * -
     - InvalidSignature
     - Function doesn't have exactly two argument
   * -
     - InvalidYield
     - Function yielded object which is not of type timeout
   * -
     - MissingAttribute
     - Non defined Attribute is referenced
   * - Warnings
     - BadSignature
     - Parameters aren't called 'env' and 'factory'

``attribute``

All parameters that are set by the user and do not belong to the default parameters described above are considered as
user-defined attributes. The following :ref:`section <attr_values>` provides an overview of the features that may be
used in these attributes.