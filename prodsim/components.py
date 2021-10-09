"""This module contains all class definitions of the simulation objects and the internal data structure for storing the
process data

"""

from __future__ import annotations
from dataclasses import dataclass, field, InitVar
from typing import Union, Dict, List, Callable, Optional, Any, Iterator, TYPE_CHECKING
from itertools import repeat, count

from simpy import (
    PriorityResource,
    Event,
    FilterStore,
    Environment
)

from prodsim.helper import Helper

if TYPE_CHECKING:
    # avoid circular imports, since Tracker is only used for type hinting
    from prodsim.tracker import Tracker


class Component:
    """Superclass for all simulation objects with which the user interacts in the process functions"""

    # Caches the attribute lists of all different simulation objects so that they only have to be created once
    __cache_attr: Dict[str, list] = {}

    def __init__(self, subclass_instance: Component, name) -> None:

        self._name = name

        # Since 'create_attr_list' is called only once for each simulation object, try-except is used instead of if-else
        try:
            self.attr_list = Component.__cache_attr[name]
        except KeyError:
            Component.__cache_attr[name] = self.create_attr_list(subclass_instance)
            self.attr_list = Component.__cache_attr[name]

        self._iteration_index: int = 0
        self._iteration_list: List[Any] = []

    @property
    def name(self):
        return self._name

    @staticmethod
    def clear_cache():
        """Resets the '__cache_attr' attribute to allow multiple simulations in a single run"""

        Component.__cache_attr = {}

    @staticmethod
    def create_attr_list(subclass_instance: Component) -> List[str]:
        """Generate a list of all attribute names which are to be considered during an iteration"""

        # Take all elements from 'dir(subclass_instance)' and remove all callables, dunder attributes and 'name'
        attr_list: List[str] = list(filter(lambda x: not any(
            [callable(getattr(subclass_instance, x, None))] +
            [x.startswith('_')] +
            [x == 'name']
        ), [attr_ for attr_ in dir(subclass_instance)]))

        return attr_list

    def keys(self) -> Iterator[Any]:
        """Return a list of all attribute names to iterate over"""

        self._iteration_index = 0
        self._iteration_list = self.attr_list

        return self

    def values(self) -> Iterator[Any]:
        """Return a list of all attribute values to iterate over"""

        self._iteration_index = 0
        self._iteration_list = [getattr(self, attr_) for attr_ in self.attr_list]

        return self

    def items(self) -> Iterator[Any]:
        """Return a list of tuples of attribute name-value pairs to iterate over"""

        self._iteration_index = 0
        self._iteration_list = [(attr_, getattr(self, attr_)) for attr_ in self.attr_list]

        return self

    def __len__(self) -> int:
        """Return number of attributes to iterate over"""

        return len(self.attr_list)

    def __contains__(self, key: str) -> bool:
        """Return whether an attribute is included in the iterator list"""

        return key in self.attr_list

    def __repr__(self) -> str:
        """Return a standardized representation for debugging"""

        return self.__class__.__name__ + '(' + ''.join([attr_ + '=' + str(getattr(self, attr_)) +
                                                        ', ' for attr_ in self.attr_list]).strip(', ') + ')'

    def __getitem__(self, key: str) -> Any:
        """Return whether the attribute list being iterated over contains a value"""

        if key in self.attr_list:
            return getattr(self, key)
        raise AttributeError("Object of type {type} has no attribute {attr}.".format(type=type(self).__name__,
                                                                                     attr=key))

    def __next__(self):
        """Return the next element from the 'iteration_list'"""

        if self._iteration_index < len(self._iteration_list):
            self._iteration_index += 1
            return self._iteration_list[self._iteration_index - 1]
        raise StopIteration

    def __iter__(self):
        """Return the iterator object"""

        return self


class Item(Component):
    """Represents a concrete workpiece, of a order"""

    __item_id_counter: Iterator = count(start=0, step=1)

    def __init__(self, attributes: Dict[str, Any], name: str) -> None:

        self._item_id = next(Item.__item_id_counter)

        for key, value in attributes.items():
            self.__setattr__(key, value)

        super().__init__(self, name)

        # Predefined attribute: Used in the simulation to remove work backs from the process.
        self.reject: bool = False

        # Predefined attribute: Used in simulation to represent recirculation in the material flow
        self.current_process_step = -1

        # Predefined attribute: Used to store the number of assembly types
        self.assembled_item_dict: Dict[str, int] = {}

    @property
    def item_id(self):
        return self._item_id

    def assemble_item(self, item: Union[Item, List[Item]]) -> None:
        """Adds a passed item to the attributes of the current item"""

        if isinstance(item, list):
            item_name = item[0].name
        else:
            item_name = item.name

        # If a type of workpiece is assembled several times in different process steps, then, starting from the second
        # of these process steps, the reference is stored under '_ + item name + x' (x>2).
        # Therefore it follows that the names of workpieces must not begin with a underscore.
        if item_name not in self.assembled_item_dict:
            # No workpiece of this type has been mounted so far
            self.assembled_item_dict[item_name] = 1
            self.__setattr__(item_name, item)
        else:
            # At least one workpiece of this type has been mounted so far
            num_item_assembled = self.assembled_item_dict[item_name]
            self.assembled_item_dict[item_name] = num_item_assembled + 1
            self.assembled_item_dict['_' + item_name + str(num_item_assembled + 1)] = 1
            self.__setattr__('_' + item_name + str(num_item_assembled + 1), item)


class Machine(Component):
    """Represents a concrete machine, of a station"""

    def __init__(self, attributes: Dict[str, Any], name: str, nr: int) -> None:

        self._nr = nr

        for key, value in attributes.items():
            setattr(self, key, value)

        super().__init__(self, name)

    @property
    def nr(self):
        return self._nr


class Factory(Component):
    """Represents the factory object which contains all global attributes"""

    def __init__(self, attributes: Dict[str, Any]):

        for key, value in attributes.items():
            setattr(self, key, value)

        super().__init__(self, name='factory')


@dataclass(eq=True)
class OrderData:

    # Environment is only needed for initialization of the data instance
    env: InitVar[Environment]

    # General data about the order
    name: str
    priority: int = 10
    attribute: Dict[str, list] = field(default_factory=dict)

    # Lists with the length of the number of stations
    station: List[StationData] = field(default_factory=list)
    function: List[Callable] = field(default_factory=list)
    counter: List[int] = field(default_factory=list)
    demand: List[Union[int, List[int]]] = field(default_factory=list)
    component: List[Union[OrderData, List[OrderData]]] = field(default_factory=list)

    # Information about sources and sinks
    sink: Optional[Callable] = None
    source: Optional[Callable] = None
    storage: Union[int, float] = float('inf')
    sink_store: FilterStore = None
    sink_put_event: Event = None
    sink_get_event: Event = None

    # Object for simulation data storage (is assigned in the simulator)
    tracker: Optional[Tracker] = None

    def __post_init__(self, env) -> None:

        # ---- Set default values -------------------------

        if self.demand == [] and self.station != []:
            for _ in repeat(None, len(self.station)):
                self.demand.append(1)

        if self.component == [] and self.station != []:
            for _ in repeat(None, len(self.station)):
                self.component.append([])

        # ---- Initialize attributes ----------------------

        for _ in repeat(None, len(self.station)):
            self.counter.append(0)

        self.sink_put_event = Event(env=env)
        self.sink_get_event = Event(env=env)
        self.sink_store = FilterStore(env=env, capacity=self.storage)

    def build_item(self) -> Item:
        """Creates a concrete workpiece with attributes according to the distributions defined in the order"""
        return Item(Helper.determinate_attr(self.attribute), self.name)


_station_id_counter: Iterator = count(start=0, step=1)
@dataclass()
class StationData(PriorityResource):

    # Environment is only needed for initialization of the data instance
    env: InitVar[Environment]

    # General data about the station
    name: str
    capacity: Optional[int] = 1
    station_id: int = field(default_factory=lambda: next(_station_id_counter))
    attribute: Dict[str, list] = field(default_factory=dict)
    measurement: bool = False

    # Data about about the machines and the buffer store
    storage: Union[int, float] = float('inf')
    station_store: Optional[FilterStore] = None
    machine: List[Machine] = field(default_factory=list)
    available_machine: List[int] = field(default_factory=list)

    # Object for simulation data storage (is assigned in the simulator)
    tracker: Optional[Tracker] = None

    def __post_init__(self, env: Environment) -> None:

        # ---- Constructor of PriorityResource ------------

        super().__init__(env=env, capacity=self.capacity)

        # ---- Initialize attributes ----------------------

        self.available_machine = [machine_index for machine_index in range(self.capacity)]

        self.station_store = FilterStore(env=env, capacity=self.storage)

        # Each machine of a station has its own number
        for nr in range(self.capacity):
            self.machine.append(self.build_machine(nr))

    def build_machine(self, nr: int) -> Machine:
        """Creates a concrete machine with attributes according to the distributions defined in the station"""
        return Machine(Helper.determinate_attr(self.attribute), self.name, nr)


@dataclass()
class FactoryData:

    # Used only for symmetry reasons regarding items and machines
    name: str

    function: List[Callable] = field(default_factory=list)
    attribute: Dict[str, list] = field(default_factory=list)

    # Object for simulation data storage (is assigned in the simulator)
    tracker: Optional[Tracker] = None

    def __post_init__(self) -> None:

        self.factory = self.build_factory()

    def build_factory(self) -> Factory:
        """Creates a concrete factory with attributes according to the distributions defined in the factory-data"""
        return Factory(Helper.determinate_attr(self.attribute))
