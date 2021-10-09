.. _data_file:

Production structure
--------------------

Each production process is defined in its own JSON file. This file contains a top-level object with two required
attributes and one optional one. The structure of these attributes is described as follows:

1. :ref:`Order <order>`
2. :ref:`Station <station>`
3. :ref:`Factory <factory2>`

....

.. _order:

Order
*****

The Order attribute is an attribute of the top-level production process object and is of the type JSON Array. This array
contains JSON objects and defines an order that combines all of the information about a particular order. The attributes
of an order are differentiated into predefined and user-defined attributes. Any attribute whose name is not predefined
is considered a user-defined attribute. In this section, all predefined attributes are described in detail. The possible
characteristics of the user-defined attributes are described in a separate section. :ref:`section <attr_values>`.

.. note::
   Only the individual parameters are described below. In  :ref:`example 01<1>` , a concrete example of this file is
   given.

``name``

The name is a required parameter of the data type String. It will later serve as an identifier for the different
jobs and should therefore be unique.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - no
     -
   * - Default value
     - /
     -
   * - Exceptions
     - MissingParameter
     - If name was not set
   * - Warnings
     - BadType
     - If name isn ot a string

.. warning::
   Since the suffix '_x' references identical assembly workpieces that are assembled in different process steps (see
   :ref:`process function <process_function>`), the name cannot have such a suffix.

``priority``

The priority is an optional integer parameter. It determines the processing order when multiple jobs request the same
scarce resource. If no priorities are set, then the program determines its order. A small value corresponds to a high
priority. If several orders do not use the same station, then the priorities have no meaning.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - 10
     -
   * - Exceptions
     - InvalidType
     - If priority is not an integer
   * -
     - InvalidValue
     - If priority is less than one

``storage``

The storage is an optional integer parameter that specifies the storage capacity of the final store of an order. The
storage is a piece value.

.. note::
   Even though this parameter is optional, it should always be set if there is no perfect understanding of the process;
   otherwise, situations may occur where an increasing number of item objects are stored in stores over the simulation
   time. This would lead to memory overload and slow the simulation speed.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - infinite
     -
   * - Exceptions
     - InvalidType
     - If capacity is not an integer
   * -
     - InvalidValue
     - If capacity is less than one

.. _source:

``source``

The source is a required parameter of type string. The function from the :ref:`production functions<function_file>`
file with the corresponding name is assigned to this order.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - /
     -
   * - Exceptions
     - UndefinedFunction
     - Function is not defined in the passed file
   * -
     - InvalidFunction
     - Function is not a generator function
   * -
     - InvalidSignature
     - Function does not have exactly two arguments
   * -
     - InvalidYield
     - Yielded object is not of type int or Timeout
   * -
     - InfiniteLoop
     - Source contains an infinite loop
   * -
     - MissingParameter
     - No source was defined
   * - Warnings
     - BadSignature
     - The signature is not (‘env’, ‘factory’)
   * -
     - BadYield
     - Source does not yield a timeout event

.. _sink:

``sink``

The sink is an optional parameter of type string. This order is assigned the function from the
:ref:`production functions<function_file>` file with the corresponding name. If workpieces of this order represent
assembly workpieces concerning another process, then the default sink will never be active. If this is not the case,
then it removes all workpieces from the final store without a time delay.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
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
     - Function does not have exactly two arguments
   * -
     - InvalidYield
     - Yielded object is not of type int or Timeout
   * -
     - InfiniteLoop
     - Source contains an infinite loop
   * - Warnings
     - BadSignature
     - The signature is not (‘env’, ‘factory’)
   * -
     - BadYield
     - Source does not yield a timeout event

``station``

The station attribute is an optional attribute of type Array. This array contains strings that represent the names of
stations in the order in which items of this order visit them. The default value is an empty array, which means that the
source places new workpieces directly into the final store (reflecting, for example, the retrieval of external assembly
workpieces).

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - []
     -
   * - Exceptions
     - UndefinedObject
     - No station is defined with this name

.. note::
   The program does not throw exceptions related to the array's length because the size of this array is considered a
   reference for the length of the other arrays.

.. _function:

``function``

The function attribute is an optional attribute of type array. It contains strings that correspond to the names of
functions defined in the  :ref:`process functions<function_file>` file. The index position determines the connection of
process functions to stations.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - []
     -
   * - Exceptions
     - UndefinedFunction
     - No function with this name is defined
   * -
     - InvalidSignature
     - Function does not have four arguments
   * -
     - MissingParameter
     - Number of functions does not match the number of stations
   * - Warnings
     - BadSignature
     - At least one argument has a bad name
   * -
     - BadYield
     - Function does not yield a simpy.Timeout object

.. _demand:

``demand``

The demand parameter is an optional parameter of type array. The index position of the entries connects them to the
stations from the station’s list. If a station performs an assembly or a pure machining process in a given process step,
then it determines the structure of the entries of the array. In machining at the station with index position i, the
i-th element of the demand array is an integer that determines the demand of this station. Another array of integers
at the corresponding index position in an assembly, which determines the number of individual assembly pieces. The
:ref:`component<component1>` attribute specifies which workpieces are used in an assembly. The default value is a list
with only 1s and the length of the station list. Thus, the default case represents a pure line production.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - [1, 1, .., 1]
     - Only possible if there is no assembly
   * - Exceptions
     - MissingParameter
     - Number of elements does not match the number of stations
   * -
     - InvalidType
     - If the list contains different objects than int or list of int
   * -
     - InvalidValue
     - Integer element in the list is not greater than zero

.. note::
   No exceptions are thrown if the inner structure does not fit around the attribute component because demand serves as
   a reference to avoid redundant error messages.

.. _component1:

``component``

The component attribute is an optional attribute of type array. The inner structure of this array corresponds to that
of the demand :ref:`demand attribute<demand>`. In the case of pure processing, there is an empty array at the
corresponding index position. In assembly, the inner array contains strings that correspond to the names of orders and
specify what type the assembly workpieces should be. The default value is an array with only empty arrays; thus, as with
the attribute demand, a pure line production is represented.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - [[], [], .., []]
     - Only possible if there is no assembly
   * - Exceptions
     - MissingParameter
     - Number of elements does not match the number of stations or the length of the assembly process list does not
       match the length of the assembly demand list
   * -
     - UndefinedObject
     - No item is defined with this name
   * -
     - InvalidValue
     - Structure does not correspond to the demand structure
   * -
     - InvalidType
     - List contains object with a type other than ‘list’

....

.. _station:

Station
*******

The station attribute is an attribute of the top-level production process object and is of the type JSON Array. This
array contains JSON objects that define a station that combines all of the information about a particular station. The
attributes of a station are differentiated into predefined and user-defined attributes. Every attribute whose name is
not predefined is considered a user-defined attribute. This section describes all predefined attributes in detail. The
possible characteristics of the user-defined attributes are described in a separate :ref:`section <attr_values>`.

.. note::
   Only the individual parameters are described below. In :ref:`example 01<1>`, a concrete example of this file is
   given.

``name``

The name is a required parameter of type string. It is used later to identify station objects and therefore must be
unique.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - no
     -
   * - Default value
     - /
     -
   * - Exceptions
     - MissingParameter
     - If name was not set
   * - Warnings
     - BadType
     - If name is not a string

``capacity``

The capacity is an optional integer parameter. It specifies the number of machines that the corresponding station has
and thus serves to map the production type of the shop floor production. The default value is one and it thus rather
represents a line production process. If a station has several machines, then one of the free machines is selected
randomly before machining at this station.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - 1
     -
   * - Exceptions
     - InvalidType
     - If capacity is not an integer
   * -
     - InvalidValue
     - If capacity is less than one

``storage``

The storage attribute is optional and of type integer. It describes the storage capacity of the buffer storage of a
station. This attribute is a unit value.

.. note::
   Even though this parameter is optional, it should always be set if a perfect understanding of the process does not
   exist; otherwise, an arbitrary accumulation of numerous objects could occur in the memory, which would slow the
   simulation arbitrarily.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - infinite
     -
   * - Exceptions
     - InvalidType
     - If storage is not an integer
   * -
     - InvalidValue
     - If storage is less than one

``measurement``

The measurement attribute is optional and of type Boolean. If a station is a measurement or quality control station
where the item attributes are not changed, then this attribute should be set to ‘true’. The effect is that workpieces
will not be tracked at this station, regardless of whether they are tracked at other stations.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
     - false
     -
   * - Exceptions
     - InvalidType
     - If measurement is not a Boolean

....

.. _factory2:

Factory
*******

The factory attribute is an optional attribute of the top-level production process object. Unlike the order and station
attributes, it is not an array but rather a single JSON object. This object contains all global attributes that any
process function, sink, source, and global function can retrieve. All of these attributes are user-definable. The rules
that apply to these attributes are described in the :ref:`'Attribute values' <attr_values>` section. In addition, the
factory object has a predefined attribute, which is described below.

``function``

The function is an optional attribute of type array. This array contains strings that correspond to the global functions
from the functions file. The global variables are controlled from these functions, whose structure is described in more
detail in the :ref:`'function file<function_file>` section.

.. list-table::
   :header-rows: 1
   :widths: 3, 3, 8

   * -
     - Value
     - Explanation
   * - Optional
     - yes
     -
   * - Default value
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
     - Function does not have exactly two argument
   * -
     - InvalidYield
     - Function yielded an object that is not of type
   * - Warnings
     - BadSignature
     - Parameters are not called ‘env’ and ‘factory’
