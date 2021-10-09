from sys import stdout
from random import choice
from itertools import repeat
from glob import glob
from typing import Optional, List, Callable, Generator, Any, Dict, Union
from os import (
    mkdir,
    remove,
    path
)

from simpy.resources.resource import PriorityRequest
from simpy import (
    Environment,
    FilterStore,
    events
)

from prodsim.filehandler import FileHandler
from prodsim.tracker import Tracker
from prodsim.components import (
    OrderData,
    StationData,
    FactoryData,
    Machine,
    Item,
    Factory
)

class Simulator:
    """Starts the simulation and maps the entire recursive simulation logic"""

    def __init__(self):
        pass

    def simulate(self, filehandler: FileHandler, sim_time: int, env: Environment, track_component: List[str],
                 progress_bar: bool, max_memory: float, bit_type: int) -> None:
        """Serves as entry point for the Blackboard when starting the simulation.

        First, some preconditions (e.g. setting up the tracker) are ensured and then the simulation is started via the
        sources and sinks.

        """

        # ---- Create a temporary folder ------------------

        try:
            mkdir(path.join(path.dirname(__file__) + '/_temp_data/_temp'))
        except FileExistsError:
            # The folder will be deleted after the data export. If the data was not exported during the last simulation
            # run, the content of the temporary folder is deleted here.
            files = glob(path.join(path.dirname(__file__) + '/_temp_data/_temp/*'))
            for f in files:
                remove(f)

        # ---- Create list of all assembly items ----------

        # List containing the names of all orders that represent assembly workpieces. This list is needed to
        # differentiate if the attribute 'comp' should be tracked.
        assemble_orders: List[str] = []

        # This triple for-loop is messy. But it is called only once and the lists have a length in the range of about
        # 20, so there is no optimization potential here.
        for order_data in filehandler.order_data_list:
            # loop over all orders (outer)
            for order_data_ in filehandler.order_data_list:
                # loop over all orders (inner)
                for component in order_data_.component:
                    # loop over all component lists of an order (inner)
                    if order_data in component:
                        # check if the order (outer) is part of the component list
                        assemble_orders.append(order_data.name)
                        continue

        # ---- Add the trackers ---------------------------

        # Store all objects that are to be tracked. This way you do not have to iterate again when creating the h5 file
        tracked_sim_obj: List[Any] = []
        tracked_orders: Dict[str, Any] = {}

        for sim_data in filehandler.sim_objects():

            if sim_data is None:
                # Case: Factory object was not set
                continue

            name: str = sim_data.name

            if track_component is None or name in track_component:
                tracker: Optional[Tracker] = None

                tracked_sim_obj.append(sim_data)

                # The difference between these cases is the number of columns that must be kept in the numpy.arrays
                if isinstance(sim_data, OrderData) and name in assemble_orders:
                    # 4: 'item_id', 'comp', 'station_id', 'time'
                    tracker = Tracker(max_memory, bit_type, len(sim_data.attribute) + 4, name)
                    tracked_orders[name] = sim_data
                elif isinstance(sim_data, OrderData) and name not in assemble_orders:
                    # 3: 'item_id', 'station_id', 'time'
                    tracker = Tracker(max_memory, bit_type, len(sim_data.attribute) + 3, name)
                    tracked_orders[name] = sim_data
                elif isinstance(sim_data, StationData):
                    # 2: 'machine_nr', 'time'
                    tracker = Tracker(max_memory, bit_type, len(sim_data.attribute) + 2, name)
                elif isinstance(sim_data, FactoryData):
                    # 1: 'time'
                    tracker = Tracker(max_memory, bit_type, len(sim_data.attribute) + 1, name)

                sim_data.tracker = tracker

        Tracker.set_tracked_orders(tracked_orders)
        Tracker.set_tracked_sim_obj(tracked_sim_obj)

        # ---- Setting up the h5 file ---------------------

        Tracker.setup_file(bit_type, assemble_orders)

        # ---- Activate factory functions -----------------

        fac_data = filehandler.factory_data

        if fac_data is not None:
            factory = fac_data.factory
            for function in fac_data.function:
                Simulator.__activate_global_function(function, env, fac_data)
        else:
            factory = None

        # ---- Activate source and sink -------------------

        for order_data in filehandler.order_data_list:
            env.process(self.__activate_source(order_data, env, factory))
            env.process(Simulator.__activate_sink(order_data, env, filehandler.order_data_list, factory))

        # ---- Activate progress bar (opt.) ---------------

        if progress_bar:
            Simulator.__progress_bar(sim_time, env)

        # ---- Start the simulation -----------------------

        env.run(until=sim_time)

        # ---- Saving the unsaved data --------------------

        # When the simulation is finished, there is still remaining data in the numpy arrays. These are stored here
        # temporarily
        for sim_data in filehandler.sim_objects():

            if sim_data is None:
                # Case: Factory object was not set
                continue

            if sim_data.tracker is not None:
                sim_data.tracker.cache_data_final()

    def __activate_source(self, order_data: OrderData, env: Environment, factory: Factory) -> \
            Generator[events.Event, Any, Any]:
        """Activates the source of an order

        """

        #####################################
        # Define frequently used references #
        #####################################

        store: FilterStore
        no_processes: Optional[bool]
        first_process_is_assembly: Optional[bool] = None
        demand: Optional[Union[List[int], int]] = None

        if order_data.station:
            # Order type has process steps
            store = order_data.station[0].station_store
            no_processes = False
            first_process_is_assembly: bool = False if isinstance(order_data.demand[0], int) else True
            demand = order_data.demand[0]
        else:
            # Item type has no process steps
            store = order_data.sink_store
            no_processes = True

        #######################
        # Activate the source #
        #######################

        while 1:

            amount: int = 0

            # Iterate over the generator
            for obj in order_data.source(env, factory):
                if isinstance(obj, int):
                    amount = obj
                    break
                yield obj

            for _ in repeat(None, amount):

                item: Item = order_data.build_item()

                # Saving the initial attribute characteristics (optional)
                if order_data.tracker is not None:
                    order_data.tracker.track_component(item, env.now, -1)

                yield store.put(item)

                if no_processes:
                    if not order_data.sink_put_event.triggered:
                        order_data.sink_put_event.succeed()
                    continue

                # No local reference is created on the counter, because this attribute is modified
                order_data.counter[0] += 1

                if first_process_is_assembly:
                    env.process(self.__assembling_process(order_data, 0, env, factory))
                elif order_data.counter[0] % demand == 0:
                    env.process(self.__machining_process(order_data, 0, env, factory))

    @staticmethod
    def __activate_sink(order_data: OrderData, env: Environment, item_data_list: List[OrderData], factory: Factory) -> \
            Generator[events.Event, Any, Any]:
        """Activate the sink of an order

        """

        # nested function to check if workpieces of this order become part of some other assembly
        def is_assembly_item(item_name_: str) -> bool:
            for item_data_ in item_data_list:
                for component_list in item_data_.component:
                    if item_name_ in [component.name for component in component_list]:
                        return True
            return False

        if order_data.sink is None:
            # default sink
            if is_assembly_item(order_data.name):
                pass
            else:
                store: FilterStore = order_data.sink_store
                item_name: str = order_data.name
                while 1:
                    yield store.get(lambda x: x.name == item_name)
        else:
            # user defined sink
            store: FilterStore = order_data.sink_store
            item_name: str = order_data.name

            while 1:

                amount: int = 0

                # iterate over the generator
                for obj in order_data.sink(env, factory):
                    if isinstance(obj, int):
                        amount = obj
                        break
                    yield obj

                for _ in repeat(None, amount):
                    yield store.get(lambda x: x.name == item_name)
                    if not order_data.sink_get_event.triggered:
                        order_data.sink_get_event.succeed()

    def __assembling_process(self, item_data: OrderData, process_step: int, env: Environment, factory: Factory) -> \
            Generator[events.Event, Any, Any]:
        """Describes a single machining process

        First, frequently used references are stored in local variables to make the following code clearer.
        Subsequently, the individual process steps are executed.

        """

        #####################################
        # Define frequently used references #
        #####################################

        station: StationData = item_data.station[process_step]
        store: FilterStore = item_data.station[process_step].station_store
        priority: int = item_data.priority
        item_name: str = item_data.name
        function: Callable = item_data.function[process_step]
        component_list: List[OrderData] = item_data.component[process_step]
        demand_list: List[int] = item_data.demand[process_step]
        number_assembling_items: int = len(component_list)

        # References that depend on whether it is the last process step in a process chain
        next_store: FilterStore
        is_last_process: bool
        next_process_is_assembly: Optional[bool] = None
        next_demand: Optional[int] = None

        if process_step == len(item_data.station) - 1:
            # Current process step is the last one in this process chain
            is_last_process = True
            next_store = item_data.sink_store
        else:
            is_last_process = False
            next_store = item_data.station[process_step + 1].station_store
            next_process_is_assembly = False if isinstance(item_data.demand[process_step + 1], int) else True
            # An assembly process always has a demand of 1
            next_demand = 1 if next_process_is_assembly else item_data.demand[process_step + 1]

        ###################################
        # Describe the assembling process #
        ###################################

        # The outer loop is run until the assembly order is accepted by the station
        while 1:

            # The inner loop is run until all required workpieces are present
            while 1:

                # Indicates for each type of assembly workpiece whether its required number is available
                items_available: List[bool] = []

                for count in range(number_assembling_items):
                    number_needed_items: int = demand_list[count]
                    # List of all workpieces currently in the store
                    item_in_store_list: List[Item] = component_list[count].sink_store.items
                    if sum(item.name == component_list[count].name for item in item_in_store_list) >= \
                            number_needed_items:
                        items_available.append(True)
                    else:
                        items_available.append(False)

                if all(items_available):
                    # Detrigger all involved sink_get_events by assigning new events to them
                    for item_data_ in component_list:
                        item_data_.sink_get_event = events.Event(env)
                    break

                # Before checking again whether all workpieces are available, the system waits until at least one
                # additional workpiece is stored in a corresponding store.
                yield events.AnyOf(env, [item_data_.sink_put_event for item_data_ in component_list])

                # Detrigger all involved sink_put_events by assigning new events to them
                for item_data_ in component_list:
                    if item_data_.sink_put_event.triggered:
                        item_data_.sink_put_event = events.Event(env)

            # 'Infinitesimal' time jump proportional to priority to avoid simultaneity of several different orders
            yield env.timeout(float('1e-16') * priority)

            # Here no context manager is used, because the concrete request instance is needed to cancel a request.
            request: PriorityRequest = station.request(priority=priority)

            # Wait until either the request is accepted or a sink_get_event is triggered.
            get_events = [item_data_.sink_get_event for item_data_ in component_list]
            yield events.AnyOf(env, get_events + [request])

            if not request.triggered:
                request.cancel()
            else:
                break

        for item_data_ in component_list:
            if not item_data_.sink_get_event.triggered:
                item_data_.sink_get_event.succeed()

        # The workpiece to which the other assembly workpieces are mounted is taken from the station store.
        # note:
        # The type of 'main_item' is Item, but simpy returns it as type 'FilterStoreGet', to avoid warnings Any is used
        main_item: Any = yield store.get(lambda x: x.name == item_name and
                                         x.current_process_step == process_step - 1)
        main_item.current_process_step = process_step

        # remove and assemble the assembly workpieces
        for index, item_data_ in enumerate(component_list):
            if demand_list[index] == 1:
                assemble_item = yield item_data_.sink_store.get(lambda x: x.name == item_data_.name)
                main_item.assemble_item(assemble_item)
            else:
                assemble_item_list = []
                for _ in repeat(None, demand_list[index]):
                    assemble_item_list.append((yield item_data_.sink_store.get(lambda x: x.name == item_data_.name)))
                main_item.assemble_item(assemble_item_list)

        # Selecting one of the free machines (criterion: random choice)
        machine_index: int = choice(station.available_machine)
        station.available_machine.remove(machine_index)
        machine: Machine = station.machine[machine_index]

        # 'yield from' can be called in a generator function and runs over the iterator until a StopIteration
        # exception is thrown

        yield from function(env, main_item, machine, factory)

        # Saving the new attribute characteristics (optional)
        if station.tracker is not None:
            station.tracker.track_component(machine, env.now)
        if not station.measurement:
            Tracker.track_nested_item(main_item, env.now, station.station_id)

        if main_item.reject:
            station.release(request)
            station.available_machine.append(machine_index)
            return

        yield next_store.put(main_item)

        station.release(request)

        # The used machine is available again for other processes
        station.available_machine.append(machine_index)

        if is_last_process:
            if not item_data.sink_put_event.triggered:
                item_data.sink_put_event.succeed()
        else:
            # Calling the recursive subsequent processes

            # No local reference is created on the counter, because this attribute is modified
            item_data.counter[process_step + 1] += 1

            if next_process_is_assembly:
                env.process(self.__assembling_process(item_data, process_step + 1, env, factory))
            elif item_data.counter[process_step + 1] % next_demand == 0:
                env.process(self.__machining_process(item_data, process_step + 1, env, factory))

    def __machining_process(self, item_data: OrderData, process_step: int, env: Environment, factory: Factory) -> \
            Generator[events.Event, Any, Any]:
        """Describes a single machining process

        First, frequently used references are stored in local variables to make the following code clearer.
        Subsequently, the individual process steps are executed.

        """

        #####################################
        # Define frequently used references #
        #####################################

        station: StationData = item_data.station[process_step]
        store: FilterStore = item_data.station[process_step].station_store
        demand: int = item_data.demand[process_step]
        item_name: str = item_data.name
        priority: int = item_data.priority
        function: Callable = item_data.function[process_step]
        reject_count: int = 0

        # References that depend on whether it is the last process step in a process chain
        next_store: FilterStore
        is_last_process: bool
        next_process_is_assembly: Optional[bool] = None
        next_demand: Optional[int] = None

        if process_step == len(item_data.station) - 1:
            # Current process step is the last one in this process chain
            is_last_process = True
            next_store = item_data.sink_store
        else:
            is_last_process = False
            next_store = item_data.station[process_step + 1].station_store
            next_process_is_assembly = False if isinstance(item_data.demand[process_step + 1], int) else True
            # An assembly process always has a demand of 1
            next_demand = 1 if next_process_is_assembly else item_data.demand[process_step + 1]

        ##################################
        # Describe the machining process #
        ##################################

        with station.request(priority) as req:
            yield req

            # Removing the workpieces from the store depends on whether the demand is greater than or equal to one
            # note:
            # The type of 'item' is Item, but simpy returns it as type 'FilterStoreGet', to avoid warnings Any is used
            if demand == 1:
                item: Any = yield store.get(lambda x: x.name == item_name and
                                            x.current_process_step == process_step - 1)
                item.current_process_step = process_step
            else:
                item: List[Any] = []
                for _ in repeat(None, demand):
                    item.append((yield store.get(lambda x: x.name == item_name and
                                                 x.current_process_step == process_step - 1)))
                    item[-1].current_process_step = process_step

            # Selecting one of the free machines (criterion: random choice)
            machine_index: int = choice(station.available_machine)
            station.available_machine.remove(machine_index)
            machine: Machine = station.machine[machine_index]

            # 'yield from' can be called in a generator function and runs over the iterator until a StopIteration
            # exception is thrown
            yield from function(env, item, machine, factory)

            # Saving the new attribute characteristics (optional)
            if station.tracker is not None:
                station.tracker.track_component(machine, env.now)
            if not station.measurement:
                Tracker.track_nested_item(item, env.now, station.station_id)

            # Placing the workpieces depends on whether the demand is equal to or greater than one
            if demand == 1:
                if not item.reject:
                    yield next_store.put(item)
                else:
                    reject_count += 1
            else:
                for item_ in item:
                    if not item_.reject:
                        yield next_store.put(item_)
                    else:
                        reject_count += 1

        # The context manager is closed and the machine is released
        station.available_machine.append(machine_index)

        if is_last_process and demand > reject_count:
            if not item_data.sink_put_event.triggered:
                item_data.sink_put_event.succeed()
        else:
            # Calling the recursive subsequent processes
            for _ in repeat(None, demand - reject_count):
                # No local reference is created on the counter, because this attribute is modified
                item_data.counter[process_step + 1] += 1

                if next_process_is_assembly:
                    env.process(self.__assembling_process(item_data, process_step + 1, env, factory))
                elif item_data.counter[process_step + 1] % next_demand == 0:
                    env.process(self.__machining_process(item_data, process_step + 1, env, factory))

    @staticmethod
    def __activate_global_function(function: Callable, env: Environment, factory_data: FactoryData) -> None:
        """Activate a single global function

        """

        # Specifies whether the attribute characteristics of the factory are to be saved
        tracked: bool = False
        if factory_data.tracker is not None:
            tracked = True
        factory = factory_data.factory

        def process():
            while 1:
                # 'yield from' can be called in a generator function and runs over the iterator until a StopIteration
                # exception is thrown
                yield from function(env, factory)

                if tracked:
                    factory_data.tracker.track_component(factory, env.now)

        env.process(process())

    @staticmethod
    def __progress_bar(sim_time: int, env: Environment) -> None:
        """Activates the progress bar """

        def bar():

            # Split the simulation interval into 100 sub intervals
            time_step: int = int((sim_time - 1) / 100)

            for index in range(100):
                j = (index + 1) / 100
                stdout.write('\r')
                stdout.write("simulation progress: [%-20s] %d%%" % ('=' * int(20 * j), 100 * j))
                stdout.flush()

                yield env.timeout(time_step)

        env.process(bar())
