from json import load
from os.path import exists
from os import mkdir, path
from shutil import rmtree
from importlib.util import spec_from_file_location, module_from_spec
from inspect import getmembers, isfunction
from typing import List, Tuple, Dict, Any, Union, Optional, Callable, Iterator

from h5py import File
from numpy import savetxt
from simpy import Environment

from prodsim.helper import Helper
from prodsim.components import OrderData, StationData, FactoryData
from prodsim.exception import (
    FileNotFound,
    MissingParameter,
    UndefinedFunction,
    UndefinedObject,
    InvalidType,
    InvalidValue,
    MissingData
)


class FileHandler:
    """The class provides all external read and write functionalities and stores the process data in an internal format

    """

    # In terms of extensibility, the lists contain all optional predefined attributes of the data objects (Order,
    # Station, Factory). To define further predefined attributes they have to be added here and the methods of this
    # class search the input files for them.
    __optional_order_parameter: List[str] = ['priority', 'station', 'function', 'demand', 'component', 'sink',
                                             'storage']
    __optional_station_parameter: List[str] = ['capacity', 'storage', 'measurement']
    __optional_factory_parameter: List[str] = ['function']

    def __init__(self) -> None:

        # The process data is stored in the attributes of the FileHandler object and later distributed to the experts
        # via the blackboard (environment).
        self.order_data_list: List[OrderData] = []
        self.station_data_list: List[StationData] = []
        self.factory_data: Optional[FactoryData] = None

        # This list/ index is used to iterate over all simulation objects passed by the user
        self._iteration_index: int = 0
        self._iteration_list: List[Any] = []

    def sim_objects(self) -> Iterator[Any]:
        """Return a list of all simulation objects"""

        self._iteration_index = 0
        self._iteration_list: List[Any] = [*self.station_data_list, *self.order_data_list, *[self.factory_data]]

        return self

    def __next__(self):
        """Return the next element from the 'iteration_list'"""

        if self._iteration_index < len(self._iteration_list):
            self._iteration_index += 1
            return self._iteration_list[self._iteration_index - 1]
        raise StopIteration

    def __iter__(self):
        """Return the iterator object"""

        return self

    def read_files(self, path_data_file: str, path_function_file: str, env: Environment) -> None:
        """Serves as entry point for the Blackboard to read the input files.

        First the files are opened and passed to the appropriate methods for reading and saving the data.

        """

        # ---- Read data file -----------------------------

        try:
            data: dict = load(open(path_data_file, 'r'))
        except FileNotFoundError:
            raise FileNotFound("The data file '{path}' wasn't found.".format(path=path_data_file))

        # ---- Read function file -------------------------

        spec = spec_from_file_location(path_function_file.split('/')[-1], path_function_file)
        function_module = module_from_spec(spec)
        try:
            spec.loader.exec_module(function_module)
        except FileNotFoundError:
            raise FileNotFound("The function file '{path}' wasn't found.".format(path=path_function_file))
        function_list: List[Tuple[str, Callable]] = getmembers(function_module, isfunction)

        # ---- Filter the custom distributions ------------

        FileHandler.__filter_custom_distribution(function_list)

        # ---- Create orders ------------------------------

        try:
            self.__create_order_data_list(data['order'], function_list, env)
        except KeyError:
            raise MissingParameter("The data file '{path}' doesn't contain the key 'order'.".format(
                path=path_data_file))

        # ---- Create stations ----------------------------

        try:
            self.__create_station_data_list(data['station'], env)
        except KeyError:
            raise MissingParameter("The data file '{path}' doesn't contain the key 'station'.".format(
                path=path_data_file))

        # ---- Update item data list ----------------------

        # This call replaces the string representations of the stations and assembly workpieces with concrete references
        self.__update_item_data_list()

        # ---- Create factory (opt.) ----------------------

        if 'factory' in data:
            self.__create_factory_data(data['factory'], function_list)

    def __create_order_data_list(self, data_list: List[Dict[str, Any]], function_list: List[Tuple[str, Callable]],
                                 env: Environment) -> None:
        """Converting the order Array from the json input file into list of concrete orders"""

        def get_func_by_name(function_name: str) -> Callable:
            # Returns the function object based on the function name, from the passed function file
            for function_tuple in function_list:
                if function_name == function_tuple[0]:
                    return function_tuple[1]
            raise UndefinedFunction("The function '{func_name}' is not defined in the passed file.".format(
                func_name=function_name))

        for index, order_data in enumerate(data_list):
            # The entries from the dictionary object (order_data), are removed in the following individually, edited and
            # then temporarily stored to then pass the constructor of the OrderData class.

            try:
                # Removing the mandatory attributes from the order_data object
                temp: Dict[str, Any] = {'name': order_data.pop('name'),
                                        'source': get_func_by_name(order_data.pop('source'))}
            except KeyError:
                raise MissingParameter(
                    "The order at position {num} in the passed file has no name or source.".format(num=index + 1))

            # Remove all optional predefined attributes set by the user
            for parameter in list(set(order_data.keys()) & set(FileHandler.__optional_order_parameter)):

                if parameter == 'function':
                    temp_function_list: List[Callable] = []
                    for function_name_json in order_data['function']:
                        temp_function_list.append(get_func_by_name(function_name_json))
                    temp['function'] = temp_function_list
                elif parameter == 'sink':
                    temp[parameter] = get_func_by_name(order_data[parameter])
                elif parameter == 'storage':
                    if not isinstance(order_data[parameter], int):
                        raise InvalidType("The storage of the order at position {pos} is of type {type}, but must be "
                                          "'int' instead.".format(pos=index+1, type=(order_data[parameter]).__name__))
                    if not order_data[parameter] > 0:
                        raise InvalidValue("The storage of the order at position {pos} is {val}, but must be greater "
                                           "than zero.".format(pos=index+1, val=order_data[parameter]))
                    temp[parameter] = order_data[parameter]
                else:
                    temp[parameter] = order_data[parameter]

                order_data.pop(parameter)

            # All attributes which are not predefined are considered as custom attributes
            temp['attribute'] = order_data

            # Create OrderData instance and add this to the corresponding list
            self.order_data_list.append(OrderData(**temp, env=env))

    def __create_station_data_list(self, data_list: List[Dict[str, Any]], env: Environment) -> None:
        """Converting the station Array from the json input file into list of concrete stations"""

        for index, station_data in enumerate(data_list):
            # The entries from the dictionary object (station_data), are removed in the following individually, edited
            # and then temporarily stored to then pass the constructor of the OrderData class.

            try:
                # Removing the mandatory attribute 'name' from the station_data object
                temp: Dict[str, Any] = {'name': station_data.pop('name')}
            except KeyError:
                raise MissingParameter(
                    "The station at position {num} in the passed file has no name.".format(num=index + 1))

            # Remove all optional predefined attributes set by the user
            for parameter in list(set(station_data.keys()) & set(FileHandler.__optional_station_parameter)):

                # Perform a few checks to see if the passed values are compliant with the SimPy interface
                if parameter == 'storage':
                    if not isinstance(station_data[parameter], int):
                        raise InvalidType("The storage of the station at position {pos} is of type {type}, but must be "
                                          "'int' instead.".format(pos=index+1, type=(station_data[parameter]).__name__))
                    if not station_data[parameter] > 0:
                        raise InvalidValue("The storage of the station at position {pos} is {val}, but must be greater "
                                           "than zero.".format(pos=index+1, val=station_data[parameter]))
                elif parameter == 'capacity':
                    if not isinstance(station_data[parameter], int):
                        raise InvalidType("The capacity of the station at position {pos} is of type {type}, but must be"
                                          " 'int' instead.".format(pos=index + 1,
                                                                   type=type(station_data[parameter]).__name__))
                    if not station_data[parameter] > 0:
                        raise InvalidValue("The capacity of the station at position {pos} is {val}, but must be greater"
                                           " than zero.".format(pos=index + 1, val=station_data[parameter]))

                temp[parameter] = station_data.pop(parameter)

            # All attributes which are not predefined are considered as custom attributes
            temp['attribute'] = station_data

            # Create StationData instance and add this to the corresponding list
            self.station_data_list.append(StationData(**temp, env=env))

    def __create_factory_data(self, factory_dict: Dict[str, Any], function_list: List[Tuple[str, Callable]]) -> None:
        """Converting the factory Object from the json input file into concrete factory object"""

        def match_name_to_function(function_name: str) -> Callable:
            # Find the global function in the 'function_list' by name
            for function_tuple in function_list:
                if function_name == function_tuple[0]:
                    return function_tuple[1]
            raise UndefinedFunction("The function '{func_name}' is not defined in the passed file.".format(
                func_name=function_name))

        # The entries from the dictionary object (factory_data), are removed in the following individually, edited and
        # then temporarily stored to then pass the constructor of the FactoryData class.
        temp: Dict[str, Any] = {}

        # Remove all optional predefined attributes set by the user
        for parameter in list(set(factory_dict.keys()) & set(FileHandler.__optional_factory_parameter)):

            if parameter == 'function':
                temp_function_list: List[Callable] = []
                for function_name_json in factory_dict['function']:
                    temp_function_list.append(match_name_to_function(function_name_json))
                temp['function'] = temp_function_list
            else:
                temp[parameter] = factory_dict[parameter]

            factory_dict.pop(parameter)

        # All attributes which are not predefined are considered as custom attributes
        temp['attribute'] = factory_dict
        temp['name'] = 'factory'

        # Create FactoryData instance and add this to the corresponding attribute
        self.factory_data = FactoryData(**temp)

    def __update_item_data_list(self) -> None:
        """Replace all strings of the attributes station and component with concrete references to the concrete objects

        """

        def find_element_by_name(name: str, look_up_list: List[Union[StationData, OrderData]]):
            # Find an object in a passed list, by name
            for element in look_up_list:
                if str(element.name) == name:
                    return element
            raise UndefinedObject("The object '{name}' is referenced in the passed data file, but it has never been "
                                  "defined in this file.".format(name=name))

        for order_data in self.order_data_list:

            # ---- Update station list --------------------

            order_data.station = [find_element_by_name(str(station_name), self.station_data_list) for station_name in
                                  order_data.station]

            # ---- Update component list ------------------

            # Build a new list that replaces the original component attribute
            temp_list = []
            for assembly_list in order_data.component:

                if not assembly_list:
                    # No assembly takes place in the current process step
                    temp_list.append([])
                elif isinstance(assembly_list, list):
                    # An assembly takes place in the current process step
                    temp_list.append(
                        [find_element_by_name(item_name, self.order_data_list) for item_name in assembly_list])
                else:
                    raise InvalidType("The object '{obj}' int the component list is of type '{type}', but only type "
                                      "'list' is permitted".format(obj=assembly_list,
                                                                   type=type(assembly_list).__name__))

            order_data.component = temp_list

    @staticmethod
    def __filter_custom_distribution(function_list: List[Tuple[str, Callable]]) -> None:
        """Filter out custom probability distributions from the function file and pass them to the Helper class"""

        distribution_list: List[Tuple[str, Callable]] = []

        for func_tuple in function_list:
            if len(func_tuple[0]) != 1:
                continue
            distribution_list.append(func_tuple)

        Helper.add_user_distribution(distribution_list)

    @staticmethod
    def data_to_csv(path_to_wd: str, remove_column: List[str], keep_original: bool) -> None:
        """Serves as an entry point for Blackboard to export the data in csv format.

        The internal file for caching is read in and each group is exported in the form of a csv file.

        """

        # If the specified destination folder does not exist it will be created to avoid loss of simulation data
        if not exists(path_to_wd):
            mkdir(path_to_wd)
            print("\033[38;2;255;0;0m the path to the folder '{}' doesn't exist, so it was created"
                  "\033[38;2;255;255;255m".format(path_to_wd))

        # Check if the simulation was run and data can be exported
        if not exists(temp_path):
            raise MissingData("The method 'data_to_h5' can only be called after 'simulate'.")

        with File(path.join(path.dirname(__file__) + '/_temp_data/_temp/hdf5.hdf5'), 'r') as hdf:

            # Iterate over each group of the file
            for group_name in hdf:

                g = hdf.get(name=group_name)
                fmt = hdf.attrs['fmt']

                # Create the headers. One for the original file and one for when attributes are to be removed during
                # exporting
                header: str = ''
                header_orig: str = ''
                column_indices: List[int] = []
                for index, attr_name in enumerate(g.attrs['header']):
                    if attr_name not in remove_column:
                        header += ',' + attr_name
                        column_indices.append(index)
                    header_orig += ',' + attr_name

                if len(column_indices) != len(g.attrs['header']) and keep_original:
                    # The user has removed columns and wants to keep the original

                    # Create a new csv file with the suffix '_orig.csv' and write the header and all data
                    with open(path_to_wd + str(group_name) + '_orig.csv', 'a') as f:
                        f.write(header_orig.strip(',') + '\n')
                        for obj_ in g:
                            savetxt(f, g.get(obj_), delimiter=',', fmt=fmt)

                # Create a new csv file with the suffix '_orig.csv' and write the header row, as well as the data of
                # non-removed columns into this file
                with open(path_to_wd + str(group_name) + '.csv', 'a') as f:
                    f.write(header.strip(',') + '\n')
                    for obj_ in g:
                        savetxt(f, g.get(obj_)[:, column_indices], delimiter=',', fmt=fmt)

        # Removing the temporary folder structure to prepare the program for the next simulation run.
        # note: If data_to_csv is not called, then the data from the simulation will remain in the _temp folder until a
        # simulation is started again, or data_to_csv is called in a different context.
        rmtree(path.join(path.dirname(__file__) + '/_temp_data/_temp'))

    @staticmethod
    def data_to_hdf5(path_to_wd: str, file_name: str) -> None:
        """Serves as an entry point for Blackboard to export the data in hdf5 format.

        The internal file for caching is read in and each group is exported in the form of a hdf5 file.

        """
        
        # Path to the temporary hdf5 file
        temp_path: str = path.join(path.dirname(__file__) + '/_temp_data/_temp/hdf5.hdf5')
        
        # If the specified destination folder does not exist it will be created to avoid loss of simulation data
        if not exists(path_to_wd):
            mkdir(path_to_wd)
            print("\033[38;2;255;0;0m the path to the folder '{}' doesn't exist, so it was created"
                  "\033[38;2;255;255;255m".format(path_to_wd))
          
        # Check if the simulation was run and data can be exported
        if not exists(temp_path):
            raise MissingData("The method 'data_to_h5' can only be called after 'simulate'.")
          
        # Save the data
        with File(temp_path, 'a') as hdf:
          
            # Delete unused information
            del hdf.attrs['fmt']
          
        # move the modified hdf5 file and rename it
        move(temp_path, path_to_wd + file_name + ".hdf5")
