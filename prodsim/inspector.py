"""This module bundles all possible checks regarding the input files.

The goal in designing this module was to keep the other modules free of check-structures as much as possible. Ideally,
the functions of this module are called once after creating new input files.

No freedom from errors is guaranteed and no errors of a content nature are identified. Only common errors that occur
when creating the input file and do not lead to a termination when reading the files are detected.

If tests are missing in this file, they can easily be added. The following overview gives a guide where the
corresponding checks have to be integrated.

"""

# There are four major methods in the Inspector class. One for stations, orders, factory and the user defined attributes
# Within the methods for stations and orders, all corresponding objects are iterated over and the individual attributes
# are checked for each object in turn. With regard to the user-defined attributes, the method for user-defined
# attributes is called.
#
# Since this module is quite long, the individual tests are provided with unique labels. The search function can be used
# to quickly navigate to these chapters.
#
# Inspector
# |-- __inspect_station    label
# |   |-- name             #0001
# |   |-- capacity         #0002
# |   |-- storage          #0003
# |   |-- measurement      #0004
# |-- __inspect_item
# |   |-- name             #0005
# |   |-- priority         #0006
# |   |-- storage          #0007
# |   |-- source/ sink     #0008
# |   |-- station          #0009
# |   |-- demand           #0010
# |   |-- component        #0011
# |   |-- function         #0012
# |-- __inspect_factory
# |   |-- function         #0013
# |-- __inspect_attribute
# |   |-- b                #0014
# |   |-- n                #0015
# |   |-- f                #0016
# |   |-- u                #0017
# |   |-- p                #0018
# |   |-- e                #0019
# |   |-- l                #0020
# |   |-- c                #0021
# |   |-- t                #0022
# |   |-- i                #0023

from __future__ import annotations
from typing import List, Any, Callable, TYPE_CHECKING
import inspect
import warnings
from time import sleep, time
import sys
import traceback

import simpy

import prodsim.exception

if TYPE_CHECKING:
    # avoid circular imports, since these imports are only used for type hinting
    from prodsim.filehandler import FileHandler
    from prodsim.components import StationData, OrderData, FactoryData


class Inspector:
    """Contains all functions to inspect the input files"""

    # This attribute is only used to create test functions.
    __env = simpy.Environment()

    def __init__(self):

        # counts the number of exceptions and warnings, that occur in the inspection
        self.__warning_count: int = 0
        self.__exception_count: int = 0

        # lists, which all traceback massages of exceptions and warnings
        self.__warning_tracebacks: List[str] = []
        self.__exception_tracebacks: List[str] = []

    def inspect(self, filereader: FileHandler) -> None:
        """Serves as an entry point for the Blackboard.

        From here all inner methods are called to inspect the files.

        """

        self.__inspect_station(filereader.station_data_list)
        self.__inspect_order(filereader.order_data_list, filereader.factory_data)

        if filereader.factory_data is not None:
            self.__inspect_factory(filereader.factory_data)

        self.__print_results()

    def __print_results(self) -> None:

        print('WARNINGS-------------------')
        for str_ in self.__warning_tracebacks:
            print(str_)

        print('EXCEPTIONS-----------------')
        for str_ in self.__exception_tracebacks:
            print(str_)

        print('---------------------------')
        print('Number of Warnings:    {num}'.format(num=self.__warning_count))
        print('Number of Exceptions:  {num}'.format(num=self.__exception_count))
        print('---------------------------')

    def __inspect_station(self, station_data_list: List[StationData]) -> None:
        """Inspects all stations of the given production process"""

        # Turn matching warnings into exceptions
        warnings.filterwarnings('error')

        # Serves to display the process bar
        number_stations: int = len(station_data_list)

        for index, station_data in enumerate(station_data_list):
            # Iterate over all passed stations

            # Serves to display the process bar
            j = (index+1)/number_stations
            sys.stdout.write('\r')
            sys.stdout.write("progress station: [%-20s] %d%%  %s" % ('=' * int(20 * j), 100 * j, station_data.name))
            sys.stdout.flush()
            sleep(1/number_stations)

            # ---- name ----------------------------------- #0001

            try:
                # Check if the name is a string
                if not isinstance(station_data.name, str):
                    warnings.warn(
                        "The name of the station at position {num} is of type '{type}', but should be 'string' instead."
                        "".format(num=index + 1, type=type(station_data.name).__name__), prodsim.exception.BadType)
                try:
                    # Check if the name stats with '_'
                    if station_data.name[0] == '_':
                        raise prodsim.exception.InvalidValue(
                            "The name of the station at position {num} starts with '_', but this name is reserved for "
                            "internal purpose only.".format(num=index + 1))
                except prodsim.exception.InvalidValue:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1
            except Warning:
                self.__warning_tracebacks.append(traceback.format_exc())
                self.__warning_count += 1

            # ---- capacity ------------------------------- #0002

            # If the capacity isn't an int -> FileHandler will raise a InvalidType Error
            # If the capacity isn't greater than zero -> FileHandler will raise a InvalidValue Error

            # ---- storage ------------------------------- #0003

            # If the storage isn't an int -> FileHandler will raise a InvalidType Error
            # If the storage isn't greater than zero -> FileHandler will raise a InvalidValue Error

            # ---- measurement ---------------------------- #0004

            try:
                # Check if measurement is of type bool
                if not isinstance(station_data.measurement, bool):
                    raise prodsim.exception.InvalidType(
                        "The attribute measurement of the station at position '{pos}' is of type '{type}', but should "
                        "be of type 'bool'.".format(pos=index + 1, type=type(station_data.measurement).__name__))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            # ---- attributes -----------------------------

            for attribute_name, attribute_value in station_data.attribute.items():
                self.__inspect_attribute(attribute_value, attribute_name, index, "station")

        # Styling the output
        print()

    def __inspect_order(self, order_data_list: List[OrderData], factory_data: FactoryData) -> None:
        """Inspects all stations of the given production process"""

        # Turn matching warnings into exceptions
        warnings.filterwarnings('error')

        # Serves to display the process bar
        number_stations: int = len(order_data_list)

        for index, order_data in enumerate(order_data_list):
            # Iterate over all passed orders

            # Serves to display the process bar
            j = (index + 1) / number_stations
            sys.stdout.write('\r')
            sys.stdout.write("progress order:   [%-20s] %d%%  %s" % ('=' * int(20 * j), 100 * j, order_data.name))
            sys.stdout.flush()
            sleep(1 / number_stations)

            # ---- name ----------------------------------- #0005

            try:
                # Check if the name is of type 'str'
                if not isinstance(order_data.name, str):
                    warnings.warn(
                        "The name of the order at position {num} is of type '{type}', but should be 'string' instead."
                        "".format(num=index + 1, type=type(order_data.name).__name__), prodsim.exception.BadType)
                try:
                    # Check if the name stats with '_'
                    if order_data.name[0] == '_':
                        raise prodsim.exception.InvalidValue(
                            "The name of the order at position {num} starts with '_', but this name is reserved for "
                            "internal purpose only.".format(num=index + 1))
                except prodsim.exception.InvalidValue:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1
            except Warning:
                self.__warning_tracebacks.append(traceback.format_exc())
                self.__warning_count += 1

            # ---- priority ------------------------------- #0006

            try:
                # Check if the type of priority is 'int'
                if not isinstance(order_data.priority, int):
                    raise prodsim.exception.InvalidType(
                        "The priority of the order at position {num} is of type '{type}', but must be an 'int' instead."
                        "".format(num=index + 1, type=type(order_data.priority).__name__))
                try:
                    # Check if the priority is greater than zero (only if priority is of type 'int')
                    if order_data.priority <= 0:
                        raise prodsim.exception.InvalidValue(
                            "The value of the priority of the order at position {num} is {value}, but must be greater "
                            "than 0.".format(num=index + 1, value=order_data.priority))
                except prodsim.exception.InvalidValue:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            # ---- storage ------------------------------- #0007

            # If the storage isn't an int -> FileHandler will raise a InvalidType Error
            # If the storage isn't greater than zero -> FileHandler will raise a InvalidValue Error

            # ---- source/ sink  -------------------------- #0008

            source_sink: List[Callable] = [order_data.source]

            if order_data.sink is not None:
                source_sink.append(order_data.sink)

            for func in source_sink:
                try:
                    # Check if the object is a generator function
                    if not inspect.isgeneratorfunction(func):
                        raise prodsim.exception.InvalidFunction(
                            "The source/ sink '{func_name}' is not a generator function."
                            "".format(func_name=func.__name__))
                except prodsim.exception.InvalidFunction:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1
                    # The following checks are only made if the source is a generator function
                    continue

                # Get the signature als a list of strings
                signature: List[str] = str(inspect.signature(func)).replace(" ", "")[1:-1].split(",")

                # check if the signature takes exactly two argument
                try:
                    if len(signature) != 2 or signature[0] == '':
                        raise prodsim.exception.InvalidSignature(
                            "A source/ sink function takes exactly two arguments, but the source '{func_name}' doesn't "
                            "take exactly two.".format(func_name=func.__name__))
                except prodsim.exception.InvalidSignature:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1
                    # The following checks are only made if the source takes one argument
                    continue

                try:
                    # Check if the argument is names 'env'
                    if signature[0] != 'env' or signature[1] != 'factory':
                        warnings.warn(
                            "The argument of a source/ sink function should be called ('env', 'factory'), but the "
                            "argument of the function '{func_name}' is called '{arg_name}' instead.".format(
                                func_name=func.__name__, arg_name=signature[0]),
                            prodsim.exception.BadSignature)
                except Warning:
                    self.__warning_tracebacks.append(traceback.format_exc())
                    self.__warning_count += 1

                # Create a source generator of this particular source
                factory = None
                if factory_data is not None:
                    factory = factory_data.build_factory()

                source_gen = func(Inspector.__env, factory)

                next_yield: Any = next(source_gen)

                try:
                    # Check if the type of the first yielded object is 'simpy.Timeout'
                    if type(next_yield) != simpy.Timeout:
                        warnings.warn(
                            "The type of the first yielded object of the source/ sink '{source}' is not 'simpy.Timeout'"
                            ", this could lead to an infinite loop.".format(source=func.__name__),
                            prodsim.exception.BadYield)
                except Warning:
                    self.__warning_tracebacks.append(traceback.format_exc())
                    self.__warning_count += 1

                try:
                    # If the first yield isn't a timeout-event, than it must be an int
                    if type(next_yield) != simpy.Timeout and type(next_yield) != int:
                        raise prodsim.exception.InvalidYield(
                            "The source/ sink '{source}', doesn't yield a timeout-event or an int at the first yield."
                            "".format(source=func.__name__))
                except prodsim.exception.InvalidYield:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1
                    continue

                # Get all other yielded objects
                yielded_obj: List[str] = []
                max_loop_time: float = 0.1

                try:
                    # Check if the source contains an infinite loop
                    t1: float = time()
                    for obj_ in source_gen:
                        yielded_obj.append(obj_)
                        if time() - t1 > max_loop_time:
                            raise prodsim.exception.InfiniteLoop(
                                "The source '{source}' may contain an infinite loop.".format(
                                    source=func.__name__))
                except prodsim.exception.InfiniteLoop:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1

                try:
                    # Check if all yielded objects are of type simpy.Timeout or int
                    if not all([type(obj_) in [simpy.Timeout, int] for obj_ in yielded_obj]):
                        raise prodsim.exception.InvalidYield(
                            "The source/ sink '{source}' yields an object, which is not of type 'simpy.Timeout' or "
                            "'int'.".format(source=func.__name__))
                except prodsim.exception.InvalidYield:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1

            # ---- station -------------------------------- #0009

            # If a used station isn't defined -> FileHandler will raise a UndefinedObject Error

            # ---- demand --------------------------------- #0010

            try:
                # Check if there is an list entry for every station
                if len(order_data.demand) != len(order_data.station):
                    raise prodsim.exception.MissingParameter(
                        "The demand list of the order at position {num} has not the same length as the station list."
                        "".format(num=index+1))
            except prodsim.exception.MissingParameter:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                # The following check are only possible if the length is correct
                continue

            for demand_index, demand in enumerate(order_data.demand):

                if isinstance(demand, list):
                    # Case: Assembling process

                    for inner_demand_index, demand_ in enumerate(demand):

                        try:
                            # Check if comp_num is of type 'int'
                            if not isinstance(demand_, int):
                                raise prodsim.exception.InvalidType(
                                    "The demand list of the order at position {num} contains at index '{pos}' a list. "
                                    "The element at position '{in_pos}' in this list is of type '{type}', but should "
                                    "be 'int' instead.".format(num=index+1, pos=demand_index+1,
                                                               in_pos=inner_demand_index+1,
                                                               type=type(demand_).__name__))
                        except prodsim.exception.InvalidType:
                            self.__exception_tracebacks.append(traceback.format_exc())
                            self.__exception_count += 1
                            continue

                        try:
                            # Check if comp_num is of type 'int' (only if demand_ is of type 'int')
                            if demand_ <= 0:
                                raise prodsim.exception.InvalidValue(
                                    "The demand list of the item at position {num} contains at index '{pos}' a list. "
                                    "The element at position '{in_pos}' in this list has the value '{val}', but should "
                                    "be greater than zero".format(num=index+1, pos=demand_index+1,
                                                                  in_pos=inner_demand_index+1, val=demand_))
                        except prodsim.exception.InvalidValue:
                            self.__exception_tracebacks.append(traceback.format_exc())
                            self.__exception_count += 1
                else:
                    # Case: Machining process
                    try:
                        # Check if demand is type 'int'
                        if not isinstance(demand, int):
                            raise prodsim.exception.InvalidType(
                                "The demand list of the order at position {num} contains an Element of type '{type}', "
                                "at position '{pos}' but only 'int' and Lists of 'int' are allowed.".format(
                                    num=index+1, type=type(demand).__name__, pos=demand_index+1))
                    except prodsim.exception.InvalidType:
                        self.__exception_tracebacks.append(traceback.format_exc())
                        self.__exception_count += 1
                        continue
                    try:
                        # Check if the demand is greater than 0 (only if demand is of type 'int')
                        if demand <= 0:
                            raise prodsim.exception.InvalidValue(
                                "The demand list of the order at position {num} contains at position {pos} an integer "
                                "with the value {val}, but only positive values are allowed.".format(
                                    num=index + 1, pos=demand_index + 1, val=demand))
                    except prodsim.exception.InvalidValue:
                        self.__exception_tracebacks.append(traceback.format_exc())
                        self.__exception_count += 1

            # ---- component ------------------------------ #0011

            # If a used order isn't defined -> FileHandler will raise a UndefinedObject Error

            try:
                # Check if there is an list entry for every station
                if len(order_data.component) != len(order_data.station):
                    raise prodsim.exception.MissingParameter(
                        "The component list of the order at position {num} has not the same length as the station list."
                        "".format(num=index+1))
            except prodsim.exception.MissingParameter:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                continue

            try:
                # Check if there is an component entry for every demand entry
                if len(order_data.component) != len(order_data.demand):
                    raise prodsim.exception.MissingParameter(
                        "The component list of the order at position {num} has not the same length as the demand list."
                        "".format(num=index+1))
            except prodsim.exception.MissingParameter:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                continue

            for comp_index, component in enumerate(order_data.component):
                # Check if component and demand have the same data structure

                if not component:
                    # Case: Machining process
                    try:
                        # Check if demand also implies an assembling
                        if isinstance(order_data.demand[comp_index], list):
                            raise prodsim.exception.InvalidValue(
                                "The component list of the order at position {pos} implies that in the process step "
                                "{step} is a machining process takes place, but the demand list implies an assembly."
                                "".format(pos=index+1, step=comp_index+1))
                    except prodsim.exception.InvalidValue:
                        self.__exception_tracebacks.append(traceback.format_exc())
                        self.__exception_count += 1
                else:
                    # Case: Assembling process

                    try:
                        # Check: The component list implies an assembly, but the demand list implies a machining
                        if not isinstance(order_data.demand[comp_index], list):
                            raise prodsim.exception.InvalidValue(
                                "The element at position {in_pos} in the component list of the order at position {pos} "
                                "implies that in this process step an assembly takes place, but the demand list implies"
                                " a machining process.".format(in_pos=comp_index+1, pos=index+1))
                    except prodsim.exception.InvalidValue:
                        self.__exception_tracebacks.append(traceback.format_exc())
                        self.__exception_count += 1
                        continue

                    try:
                        # Check if the length of the component is the same as the length of the demand list
                        if len(component) != len(order_data.demand[comp_index]):
                            raise prodsim.exception.MissingParameter(
                                "The element at position {in_pos} in the component list of the order at position {pos} "
                                "implies that in there are {num_ass} items involved process step. But the demand list "
                                "has {num_dem} elements.".format(in_pos=comp_index+1, pos=index+1,
                                                                 num_ass=len(component),
                                                                 num_dem=len(order_data.demand[comp_index])))
                    except prodsim.exception.MissingParameter:
                        self.__exception_tracebacks.append(traceback.format_exc())
                        self.__exception_count += 1

            # ---- function ------------------------------- #0012

            try:
                # Check the length of the function list
                if len(order_data.function) != len(order_data.station):
                    raise prodsim.exception.MissingParameter(
                        "The number of stations of order '{item_name}' doesn't match the number of functions.".format(
                            item_name=order_data.name))
            except prodsim.exception.MissingParameter:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            for function_index, function in enumerate(order_data.function):

                # Get the signature of the functions a list
                signature: List[str] = str(inspect.signature(function)).replace(" ", "")[1:-1].split(",")

                try:
                    # Check if the function has exactly four arguments
                    if len(signature) != 4:
                        raise prodsim.exception.InvalidSignature(
                            "A process function takes exactly four arguments, but the function '{func_name}' doesn't "
                            "take exactly four.".format(func_name=function.__name__, count=len(signature)))
                    try:
                        # Check if the argument are named right
                        if any([signature[0] != 'env', signature[1] != 'item', signature[2] != 'machine',
                                signature[3] != 'factory']):
                            warnings.warn(
                                "The signature of a process function should be (env, item, machine, factory), but in "
                                "the function '{func_name}' at least one argument has a different name."
                                "".format(func_name=function.__name__), prodsim.exception.BadSignature)
                    except Warning:
                        self.__warning_tracebacks.append(traceback.format_exc())
                        self.__warning_count += 1
                except prodsim.exception.InvalidSignature:
                    self.__exception_tracebacks.append(traceback.format_exc())
                    self.__exception_count += 1
                    continue

                try:
                    # Check if the function is a generator
                    if not inspect.isgeneratorfunction(function):
                        warnings.warn("The function '{func_name}' from the function file doesn't yield a timeout-event."
                                      "".format(func_name=function.__name__), prodsim.exception.BadYield)
                except Warning:
                    self.__warning_tracebacks.append(traceback.format_exc())
                    self.__warning_count += 1
                    continue

            # ---- attribute ------------------------------

            for attribute_name, attribute_value in order_data.attribute.items():
                self.__inspect_attribute(attribute_value, attribute_name, index, "order")

        # Styling the output
        print()

    def __inspect_factory(self, factory_data: FactoryData) -> None:
        """Inspects the factory object of the given production process"""

        # Turn matching warnings into exceptions
        warnings.filterwarnings('error')

        # Serves to display the process bar
        number_stations: int = 1
        sys.stdout.write('\r')
        sys.stdout.write("factory:          [%-20s] %d%%  %s" % ('=' * int(20 * 1), 100 * 1, 'factory'))
        sys.stdout.flush()
        sleep(1 / number_stations)

        # Styling the output
        print()

        # ---- function ----------------------------------- #0013

        for function in factory_data.function:

            try:
                # Check if the global function is a generator
                if not inspect.isgeneratorfunction(function):
                    raise prodsim.exception.InvalidFunction(
                        "The function '{func_name}' from the function file is not a generator function. A global "
                        "function must yield at least one timeout-event."
                        "".format(func_name=function.__name__))
            except prodsim.exception.InvalidFunction:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                continue

            # Get the signature of the functions a list
            signature: List[str] = str(inspect.signature(function)).replace(" ", "")[1:-1].split(",")

            try:
                # Check if the function takes exactly two arguments
                if len(signature) != 2:
                    raise prodsim.exception.InvalidSignature(
                        "A global function takes exactly two argument, but the function '{func_name}' takes {num_parm}."
                        "".format(func_name=function.__name__, num_parm=len(signature)))
            except prodsim.exception.InvalidSignature:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                continue

            try:
                # Check if the arguments are named right
                if signature[0] != 'env' or signature[1] != 'factory':
                    warnings.warn("The parameters of the global function '{func_name}' should be 'env' and 'factory', "
                                  "but instead it is ('{para_name_1}','{para_name_2}')."
                                  "".format(func_name=function.__name__, para_name_1=signature[0],
                                            para_name_2=signature[1]), prodsim.exception.BadSignature)
            except Warning:
                self.__warning_tracebacks.append(traceback.format_exc())
                self.__warning_count += 1

            # Create a source generator of this particular source
            function_gen = function(Inspector.__env, factory_data.build_factory())

            # Get all other yielded objects
            yielded_obj: List[str] = []
            max_loop_time: float = 0.1

            try:
                # Check if the function contains an infinite loop
                t1: float = time()
                for obj_ in function_gen:
                    yielded_obj.append(obj_)
                    if time() - t1 > max_loop_time:
                        raise prodsim.exception.InfiniteLoop(
                            "The global function '{func}' may contain an infinite loop.".format(
                                func=function_gen.__name__))
            except prodsim.exception.InfiniteLoop:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            try:
                # Check if all yielded objects are of type simpy.Timeout
                if not all([type(obj_) in [simpy.Timeout] for obj_ in yielded_obj]):
                    raise prodsim.exception.InvalidYield(
                        "The global function'{func}' yields an object, which is not of type 'simpy.Timeout'."
                        "".format(func=function_gen.__name__))
            except prodsim.exception.InvalidYield:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

        # ---- attributes ---------------------------------

        for attribute_name, attribute_value in factory_data.attribute.items():
            self.__inspect_attribute(attribute_value, attribute_name, 0, 'factory')

    def __inspect_attribute(self, attr_value: List[Any], attr_name: str, index: int, sim_type: str) -> None:
        """Inspecting the attributes of the simulation objects of the given production process

        This method is called starting from the individual checks of the simulation objects

        """

        # ---- General checks -----------------------------

        # The Helper also raises some errors, if the attributes arent lists

        try:
            # Check if the Attribute is a list
            if not isinstance(attr_value, list):
                raise prodsim.exception.InvalidType(
                    "The attribute '{attr_name}' of the {s_type} at position {num} is of type '{type}', but must be a "
                    "'list' instead.".format(
                        attr_name=attr_name, num=index + 1, type=type(attr_value).__name__, s_type=sim_type))
        except prodsim.exception.InvalidType:
            self.__exception_tracebacks.append(traceback.format_exc())
            self.__exception_count += 1
            return

        try:
            # Check if the list has a least one argument
            if len(attr_value) == 0:
                raise prodsim.exception.InvalidFormat(
                    "The list of the attribute '{attr_name}' of the {s_type} at position {num} has no elements.".format(
                        attr_name=attr_name, num=index + 1, s_type=sim_type))
        except prodsim.exception.InvalidFormat:
            self.__exception_tracebacks.append(traceback.format_exc())
            self.__exception_count += 1
            return

        # ---- Attribute case 'b' ------------------------- #0014

        if attr_value[0] == "b":

            try:
                # Check if the length of the attribute list is two
                if len(attr_value) != 2:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} is supposed to be binary "
                        "distributed, but the given list has length {length}, but should have length 2 instead.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                # No further checks can be performed
                return

            try:
                # Check if the second element in the passed list is of type float or int
                if not isinstance(attr_value[1], (float, int)):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type float"
                        "".format(attr_val=attr_value, attr=attr_name, num=index + 1, type=type(attr_value[1]).__name__,
                                  s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                # No further checks can be performed
                return

            try:
                # Check whether the second list entry is in the interval between 0 and 1 (only if 'int' or 'float')
                if attr_value[1] > 1 or attr_value[1] < 0:
                    raise prodsim.exception.InvalidValue(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file has the value '{val}', but should be between 0.0"
                        " and 1.0".format(attr_val=attr_value, attr=attr_name, num=index + 1, val=attr_value[1],
                                          s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 'n' ------------------------- #0015

        if attr_value[0] == "n":

            try:
                # Check if the length of the attribute list is three
                if len(attr_value) != 3:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be normally distributed, but the given list has length {length}, but should have length 3 "
                        "instead.".format(attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                # No further checks can be performed
                return

            try:
                # Check if the the second and third argument is of type 'int' or 'float
                if not isinstance(attr_value[1], (int, float)) or not isinstance(attr_value[2], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The second or third element of the attribute value '{attr_val}' of the attribute '{attr}' of "
                        "the {s_type} at position {num} in the passed file is not of type int or float".format(
                            attr_val=attr_value, attr=attr_name, num=index + 1, s_type=sim_type))

            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                # No further checks can be performed
                return

            try:
                # Check if the standard deviation is greater or equal zero
                if attr_value[2] < 0:
                    raise prodsim.exception.InvalidValue(
                        "The standard deviation of the attribute '{attr}' of the {s_type} at position {num} in the "
                        "passed file is '{val}', but should be greater or equal to zero.".format(
                            attr=attr_name, num=index + 1, val=attr_value[2], s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 'f' ------------------------- #0016

        if attr_value[0] == "f":

            try:
                # Check if the length of the attribute list is two
                if len(attr_value) != 2:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be a fix value, but the given list has length {length}, but should have length 2 instead."
                        "".format(attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                # No further checks can be performed
                return

            try:
                # Check if the value is of type 'int' or 'float'
                if not isinstance(attr_value[1], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 'u' ------------------------- #0017

        if attr_value[0] == 'u':

            try:
                # Check if the length of the attribute list is three
                if len(attr_value) != 3:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be a uniform distributed, but the given list has length {length}, but should have length 3 "
                        "instead.".format(attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the second element is of type 'int' or 'float'
                if not isinstance(attr_value[1], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the third element is of type 'int' or 'float'
                if not isinstance(attr_value[2], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The third element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[2]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the third element is equal or larger then the second
                if attr_value[1] > attr_value[2]:
                    raise prodsim.exception.InvalidValue(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be uniform distributed, but the second element is larger than the third, what is not "
                        "allowed.".format(attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 'p' ------------------------- #0018

        if attr_value[0] == 'p':

            try:
                # Check if the length of the attribute list is two
                if len(attr_value) != 2:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be a poisson distributed, but the given list has length {length}, but should have length 2 "
                        "instead.".format(attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the second element is of type 'int' or 'float'
                if not isinstance(attr_value[1], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the second element is larger or equal than zero
                if attr_value[1] < 0:
                    raise prodsim.exception.InvalidValue(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be poisson distributed, but the second element is less than zero.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 'e' ------------------------- #0019

        if attr_value[0] == 'e':

            try:
                # Check if the length of the attribute list is two
                if len(attr_value) != 2:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be a exponential distributed, but the given list has length {length}, but should have "
                        "length 2 instead.".format(attr_name=attr_name, num=index + 1, length=len(attr_value),
                                                   s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the second element is of type 'int' or 'float'
                if not isinstance(attr_value[1], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the second element is larger or equal than zero
                if attr_value[1] <= 0:
                    raise prodsim.exception.InvalidValue(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be exponential distributed, but the second element is less than zero.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 'l' ------------------------- #0020

        if attr_value[0] == 'l':

            try:
                # Check if the length of the attribute list is three
                if len(attr_value) != 3:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be a lognormal distributed, but the given list has length {length}, but should have length "
                        "3 instead.".format(attr_name=attr_name, num=index + 1, length=len(attr_value),
                                            s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the second element is of type 'int' or 'float'
                if not isinstance(attr_value[1], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the third element is of type 'int' or 'float'
                if not isinstance(attr_value[2], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The third element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[2]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the third element is larger or equal than zero
                if attr_value[2] < 0:
                    raise prodsim.exception.InvalidValue(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be lognormal distributed, but the third element is less than zero.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 'c' ------------------------- #0021

        if attr_value[0] == 'c':

            try:
                # Check if the length of the attribute list is two
                if len(attr_value) != 2:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be a chisquare distributed, but the given list has length {length}, but should have length "
                        "2 instead.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the second element is of type 'int' or 'float'
                if not isinstance(attr_value[1], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the second element is larger than zero (NOT equal)
                if attr_value[1] <= 0:
                    raise prodsim.exception.InvalidValue(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be chisquare distributed, but the second element is less than or equal to zero.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 't' ------------------------- #0022

        if attr_value[0] == 't':

            try:
                # Check if the length of the attribute list is two
                if len(attr_value) != 2:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be a standard-t distributed, but the given list has length {length}, but should have length"
                        " 2 instead.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the second element is of type 'int' or 'float'
                if not isinstance(attr_value[1], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int or "
                        "float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                        type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the second element is larger than zero (NOT equal)
                if attr_value[1] <= 0:
                    raise prodsim.exception.InvalidValue(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is supposed "
                        "to be standard-t distributed, but the second element is less than or equal to zero.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- Attribute case 'i' ------------------------- #0023

        if attr_value[0] == 'i':

            try:
                # Check if the length of the attribute list is three
                if len(attr_value) != 3:
                    raise prodsim.exception.InvalidFormat(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is "
                        "supposed to be a binomial distributed, but the given list has length {length}, but should "
                        "have length 3 instead.".format(
                            attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidFormat:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the second element is of type 'int'
                if not isinstance(attr_value[1], int):
                    raise prodsim.exception.InvalidType(
                        "The second element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int "
                        "".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                  type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the value of the third element is of type 'int' or 'float'
                if not isinstance(attr_value[2], (int, float)):
                    raise prodsim.exception.InvalidType(
                        "The third element of the attribute value '{attr_val}' of the attribute '{attr}' of the "
                        "{s_type} at position {num} in the passed file is of type '{type}', but should be type int "
                        "or float.".format(attr_val=attr_value, attr=attr_name, num=index + 1,
                                           type=type(attr_value[1]).__name__, s_type=sim_type))
            except prodsim.exception.InvalidType:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1
                return

            try:
                # Check if the second element is larger than zero (NOT equal)
                if attr_value[1] <= 0:
                    raise prodsim.exception.InvalidValue(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is "
                        "supposed to be binomial distributed, but the second element (n) is less than or equal to "
                        "zero.".format(attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            try:
                # Check if the third element is in [0,1]
                if attr_value[2] < 0 or attr_value[2] > 1:
                    raise prodsim.exception.InvalidValue(
                        "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file is "
                        "supposed to be binomial distributed, but the third element (p) is not in the interval "
                        "[0,1]".format(attr_name=attr_name, num=index + 1, length=len(attr_value), s_type=sim_type))
            except prodsim.exception.InvalidValue:
                self.__exception_tracebacks.append(traceback.format_exc())
                self.__exception_count += 1

            return

        # ---- no matching identifier ---------------------

        try:
            raise prodsim.exception.NotSupportedParameter(
                warnings.warn(
                    "The attribute '{attr_name}' of the {s_type} at position {num} in the passed file has an non pre "
                    "defined identifier '{id}'. No checks are performed for this attribute.".format(
                        attr_name=attr_name, num=index + 1, id=attr_value[0], s_type=sim_type),
                    prodsim.exception.NotDefined))
        except Warning:
            self.__warning_tracebacks.append(traceback.format_exc())
            self.__warning_count += 1
