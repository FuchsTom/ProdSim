.. _example_1:

Example 01: Create input files
------------------------------

In this example, a textual description of a sample process is converted into a formal structure, which can be passed to
the program as an input file. This step is necessary for every simulation, because without appropriate files no
simulation environment could be created. At the end of this example an .json file containing the process data and a .py
file containing all the functions are created.

A gear shaft serves as an example here, which must first be machined. Gear wheels are then assembled in an initial
assembly process. Before bearings can be mounted in a further assembly process, the shaft with the gears must first heat
treated and undergo quality control. The bearings are supplied externally and mounted as delivered, while the gears must
first be ground.

To map this process, the following content-related sub-aspects are considered.

* :ref:`Stations <station_setup>`
* :ref:`Items <item_setup>`
* :ref:`Factory <factory>`
* :ref:`Functions <function_ex>`

.. note::
   The example does not claim to represent a real existing process, but aims to show as many facets as possible.



.. warning::
   In the following, a file example is given separately for each of the three top-level attributes. It should be noted
   that the later input file combines all these three attributes into one large top-level object.

....

.. _station_setup:

Stations
********

First, the stations that occur in the process are described, as these form the basis for the later process. Each station
must have at least the attribute ``name``, which must be chosen in such a way that there is no name collision, otherwise
no clear assignment can be made. In addition, each station has the attribute ``capacity``, which indicates the number of
equivalent machines in the station. If this attribute is not set, it is assumed to be one. The attribute ``storage`` is
also optional and specifies the capacity of the buffer memory in front of the station, which is infinite by default.
All other ``attributes`` that are set by the user represent physical properties of the station itself. The characteristics
of these attributes can take on different distributions (:ref:`distributions <attr_values>`), which describe the state
of the characteristics at the beginning of the simulation.

Since this structure is the same for all stations, the first station in the process 'lathe' is described in detail here
and all others are only listed below.

Since there is only one station with lathes in this process, the ``name`` lathe can be used. Assume that there are 2
actual machines in the lathe station. So that the ``capacity`` differs from the default value and can be set to two. All
of these machines have the same attributes, but of course each machine has its own characteristics of these attributes,
which are individually determined for each machine during machining. If, on the other hand, you want to map two lathes
that have different attributes, then you simply have to define two stations. It should be noted, however, that one must
then also clearly define which of these machines will be visited by the workpiece, because in the case of a station with
two machines, a possible free machine is always selected by itself. Since a separate source is to be defined later, it
is advisable to define a ``storage`` for the buffer store, because otherwise an extremely large number of objects will
accumulate if the processing time is greater than the interval in which new objects enter the system. The capacity is
set here to twenty units as an example. If this buffer store full, the source, or upstream stations can only store new
objects again when the machine has taken an object from the buffer. Finally, some physical ``attributes`` of the machine
can be defined, which can be referenced later in the process function. Lathes of this station should have the attribute
'wear', which is initially zero. In addition, each lathe has an eccentricity, which is normal distributed around the
mean value 0 with a standard deviation of 0.5.

Of course, lathes have many other properties, but only those that are relevant for the process should be defined here.

For this particular machine, the following results:

.. code-block:: JSON

   {
     "name": "lathe",
     "capacity": 2,
     "storage": 20,
     "wear": ["f",0],
     "eccentricity": ["n",0,0.5]
   }

This set of attributes now describes the station for the lathes. Each of these sets represents an station object. To
describe all stations all these objects are written into the list ``station``, which is an attribute of the top-level
object in the json file.

.. note::
   The order of attributes in objects is arbitrary

Thus, for the process described above, the following could result:

.. code-block:: JSON

   {
     "station": [
        {
          "name": "lathe",
          "capacity": 2,
          "storage": 20,
          "wear": ["f",0],
          "eccentricity": ["n",0,0.5]
        },
        {
          "name": "assembly",
          "capacity": 2,
          "storage": 20,
          "mistake_rate": ["f",0.01]
        },
        {
          "name": "grinding_machine",
          "wear": ["f",0],
          "lubricant_purity": ["n",0.99,0.01]
        },
        {
          "name": "heat_treatment",
          "temperature": ["n",1200,5],
          "atmosphere_CO2": ["f",0.8],
          "atmosphere_N2": ["f",0.1]
        },
        {
          "name": "quality_control",
          "detection_rate": ["f",0.98]
        }
      ]
   }

....

.. _item_setup:

Items
*****

After defining the stations, which determine the rough structure of the process, it is recommended to define the actual
workpieces. An item type receives all the information that it would receive in a real process in the form of a
production card. Like the stations, the item types must also have unique ``names`` in order to be identified in the process.
To describe the stations and the order in which a workpiece of this type passes through, there is a list ``station``
which contains the names of the stations in the order in which they are passed through. Each of these stations must
itself also be defined in the .json file. If no list of stations is specified, then it is a workpiece that comes from
outside and is only introduced into the process because it is part of an assembly process. At each defined station a
function is executed, which must be defined by the user. The list ``function`` contains the names of these functions in
the appropriate order to the list station. Therefore both lists must always have the same length. Finally, the demand
quantities and the objects in the case of an assembly must be defined. Each station has a demand for objects that it
needs to run once. This information is stored in the list ``demand``, which of course must have the length of the
station list. If a simple machining is mapped, the list at the corresponding index position contains the quantity as
int. If, on the other hand, an assembly occurs, then demand contains a list which contains the quantity of the objects
to be assembled. It should be noted that only one main workpiece is ever used in an assembly, to which any number of
workpieces of other types can be assembled. In order to specify which item types are to be mounted in case of an
assembly, there is the list ``component``, which again has the same length as the list station. In the case of a simple
machining it simply contains an empty list at the corresponding index position. In case of an assembly it contains a
list with the names of the parts to be assembled at the position. In addition, each workpiece has a ``priority`` which
becomes relevant when multiple workpieces request a scarce resource. The priority must be a positive integer, where
small corresponds to a higher priority (the default value is 10). The ``storage`` describes the storage capacity of the
end storage where finished workpieces of that type are stored before being removed from the sink or an assembly process.
Finally, there are the ``source`` and ``sink``, which are string representations of corresponding functions.

The process described above consists of 4 different item types. The shaft, the gears and two different bearings. It may
be that the gears have different diameters, for example, but if this fact is not relevant to the process, the three
different gears can be modeled as one item type.

All workpieces can be separated into three different mental categories. Workpieces which are assembled and/or machined,
workpieces which are only machined and those which are machined or assembled and only workpieces which are delivered
externally and then assembled.

In this example, the shaft represents a workpiece that is both machined and assembled. Since this is the most general
case, the procedure is described in more detail on the basis of the shaft.

Since there is only one type of shaft, the ``name`` 'shaft' is appropriate. As described above, the shaft visits the
stations 'lathe', 'assembly', 'heat_treatment', 'quality_control' and again 'assembly' in this order. This is stored in
the list ``station``. The functions are stored in exactly the same structure in the ``function`` list. For the
``demand``, assume that the lathe always processes exactly one shaft at a time, while the heat_treatment always
processes ten units and the quality_control always processes two units at a time. The first assembly step requires three
gears and the second assembly step requires one ball bearing and two cylindrical bearings as a ``component``. Since
there are no competing types for resources here, the ``priority`` for all workpieces can be left at the default value.
Also the final store should not be of interest here, so its ``storage`` is left at the default value (infinite) and
also the default ``sink`` is used. The attribute ``source`` is assigned the name of the source function to be defined
later. All other ``attributes`` differing from the reacted terms represent the core physical properties of the wave.

This description can be translated as follows:

.. code-block:: JSON

   {
     "name": "shaft",
     "station": ["lathe","assembly","heat_treatment","quality_control","assembly"],
     "function": ["turning","assembly_gear","heating","quality_check","assembly_bearing"],
     "demand": [1,[3],10,2,[1,2]],
     "component": [[],["gear"],[],[],["ball_bearing","cylindrical bearing"]],
     "source": "shaft_source",
     "length": ["n",45,0.02],
     "diameter_1": ["n",12,0.08],
     "diameter_2": ["n",22,0.02],
     "surface_quality": ["n",1.2,0.1],
     "hardness": ["f",650]
   }

Of course, each item type that appears in the ``component`` list must also be defined. As with the stations, each item
type represents an object. All types together are stored in the list/array ``item``, which is a top-level attribute.
This results in:

.. code-block:: JSON

   {
     "item": [
        {
          "name": "shaft",
          "station": ["lathe","assembly","heat_treatment","quality_control","assembly"],
          "function": ["turning","assembly_gear","heating","quality_check","assembly_bearing"],
          "demand": [1,[3],10,2,[1,2]],
          "component": [[],["gear"],[],[],["ball_bearing","cylindrical bearing"]],
          "source": "shaft_source",
          "length": ["n",45,0.02],
          "diameter_1": ["n",12,0.08],
          "diameter_2": ["n",22,0.02],
          "surface_quality": ["n",1.2,0.1],
          "hardness": ["f",650]
        },
        {
          "name": "gear",
          "station": ["grinding_machine"],
          "function": ["gear_grinding"],
          "storage": 20,
          "source": "gear_source",
          "inner_diameter": ["n",22,0.03],
          "hardness": ["f",1200]
        },
        {
          "name": "ball_bearing",
          "storage": 10,
          "crack": ["b",0.01],
          "roasted": ["b",0.005],
          "inner_diameter": ["n",12,0.01]
        },
        {
          "name": "cylindrical_bearing",
          "storage": 10,
          "crack": ["b",0.02],
          "inner_diameter": ["n",12,0.01],
          "outer_diameter": ["n",50,0.2]
        }
      ]
   }

It should be noted that each workpiece automatically gets the attribute ``reject``, which can be accessed in the process
functions. This attribute determines whether a workpiece is to be removed from production after a process.
Also, it is pointed out that the bearings here are supposed to represent external components, since unlike the gears,
they do not have stations or similar as attributes. To see all parameters and their default values see:
:ref:`Interface file <interface>`.

....

.. _factory:

Factory
************************

Factory provides a global variable space. The purpose of this is to introduce variables that are not tied to a specific
machine or workpiece, but are available for each process to define the process function. In addition, global functions
can also be defined here.
In this example there should be three global parameters and one global function. Let us assume that the production
process takes place in two halls and that each of these halls has its own temperature which can influence the processes.
In addition, there is a variable, which should track the total power consumption. These attributes are also written into
an object, as with the stations and items, with the difference that this object is now an attribute at the top level in
the .json file, since there is only one of these objects and therefore no list is necessary.
The global function has the purpose to control the course of the temperatures.

Thus, for the top-level:

.. code-block:: JSON

   {
     "factory":
        {
          "function": ["temperature_course"],
          "temperature_1": ["f",23],
          "temperature_2": ["f",20],
          "energy_usage": ["f",0]
        },
   }

....

.. _function_ex:

Functions
*********

Now that the entire process has been described on a logistics level, the individual processes on the machine level still
need to be represented. This is done by means of a .py input file, in which the corresponding functions are defined in
the global scope. It is important that each function defined in the item attribute 'function' is also defined in the
file.

Here we will not go into the exact design of these functions, as this has already been done in the function file
:ref:`description <function_file>`.
