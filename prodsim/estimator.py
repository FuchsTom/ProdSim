from typing import (
    List,
    Callable,
    Dict
)
from json import load, dumps
from os import remove, path
from time import process_time
import functools

from dill.source import getsource

from prodsim.environment import Environment
from prodsim.exception import InvalidFunction


class Estimator:
    """Estimator for estimating the expected simulation time."""

    def __init__(self):

        self.__env = Environment()
        self.__curr_path = path.dirname(__file__)

    @staticmethod
    def timer(func):
        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            start_time = process_time()
            func(*args, **kwargs)
            end_time = process_time()
            return end_time - start_time
        return wrapper_timer

    def est_item(self, track: bool) -> float:
        """Estimates the time for creating a workpiece.

        :param track: Indicates whether the order is being tracked
        :type track: bool
        :return: Estimated simulation time for creating a workpiece without attributes
        :rtype: float

        """

        # Attributes to adjust the accuracy of the measurement
        sim_time = 50_000
        max_memory = 2
        bit_type = 32

        # Measure the simulation time
        self.__env.clear_env()
        self.__env.read_files(self.__curr_path + '/_estimate_process/est_attribute.json',
                              self.__curr_path + '/_estimate_process/est_attribute.py')

        @Estimator.timer
        def simulate():
            if track:
                self.__env.simulate(sim_time=sim_time, max_memory=max_memory, bit_type=bit_type)
            else:
                self.__env.simulate(sim_time=sim_time, track_components=[], max_memory=max_memory, bit_type=bit_type)

        time_item = simulate()

        return time_item / sim_time

    def est_station(self, track: bool) -> float:
        """Estimates the time caused by the recursive process logic.

        :param track: Indicates whether the order is being tracked
        :type track: bool
        :return: Estimated simulation time for simply passing through stations (without functions and item attributes)
        :rtype: float

        """

        # Attributes to adjust the accuracy of the measurement
        sim_time = 50_000
        max_memory = 2
        bit_type = 32

        @Estimator.timer
        def simulate():
            if track:
                self.__env.simulate(sim_time=sim_time, max_memory=max_memory, bit_type=bit_type)
            else:
                self.__env.simulate(sim_time=sim_time, track_components=[], max_memory=max_memory, bit_type=bit_type)

        # Measure the simulation time for two stations
        self.__env.clear_env()
        self.__env.read_files(self.__curr_path + '/_estimate_process/est_station_2.json',
                              self.__curr_path + '/_estimate_process/est_station_2.py')
        time_two_station = simulate()

        # Measure the simulation time for one stations
        self.__env.clear_env()
        self.__env.read_files(self.__curr_path + '/_estimate_process/est_station_1.json',
                              self.__curr_path + '/_estimate_process/est_station_1.py')
        time_one_station = simulate()

        return (time_two_station - time_one_station) / sim_time

    def est_attribute(self, distribution: List[tuple], num_station: int, track: bool) -> float:
        """Estimates the time caused by additional attributes.

        :param distribution: List of attributes to be estimated
        :type distribution: List[tuple]
        :param num_station: Number of stations that workpieces of the order under consideration pass through
        :type num_station: int
        :param track: Indicates whether the order is being tracked
        :type track: bool
        :return: Estimated additional simulation time for additional attributes
        :rtype: float

        """

        # Attributes to adjust the accuracy of the measurement
        sim_time = 50_000
        max_memory = 2
        bit_type = 32

        @Estimator.timer
        def simulate():
            if track:
                self.__env.simulate(sim_time=sim_time, max_memory=max_memory, bit_type=bit_type)
            else:
                self.__env.simulate(sim_time=sim_time, track_components=[], max_memory=max_memory, bit_type=bit_type)

        ######################################
        # Run the simulation with attributes #
        ######################################

        # Create new json input file
        with open(self.__curr_path + '/_estimate_process/est_attribute_with_attr.json', 'w') as file_with_attr:

            with open(self.__curr_path + '/_estimate_process/est_attribute.json', 'r') as process_file:

                process = load(process_file)

                # Add the attributes 'station' and 'function' to the order
                process['order'][0]['station'] = ['station' + str(i) for i in range(num_station)]
                process['order'][0]['function'] = ['function' + str(i) for i in range(num_station)]

                # Add the attributes to the order
                index = 0
                for attribute in distribution:
                    for _ in range(attribute[1]):
                        process['order'][0]['attr' + str(index)] = attribute[0]
                        index += 1

                # Add the station objects
                for i in range(num_station):
                    process['station'].append({'name': 'station' + str(i)})

                json_str = dumps(process)
                file_with_attr.write(json_str)

        # Create new py input file
        with open(self.__curr_path + '/_estimate_process/est_attribute_with_func.py', 'w') as file_with_func:

            with open(self.__curr_path + '/_estimate_process/est_attribute.py') as function_file:

                functions = function_file.read()

                # Add a simple 'timeout-function' for each process step
                for i in range(num_station):
                    functions += '\n\n' + 'def function' + str(i) + '(env, item, machine, factory): \n'
                    functions += '\tyield env.timeout(1)'

                file_with_func.write(functions)

        # Measure the simulation time
        self.__env.clear_env()
        self.__env.read_files(self.__curr_path + '/_estimate_process/est_attribute_with_attr.json',
                              self.__curr_path + '/_estimate_process/est_attribute_with_func.py')
        time_with_attr = simulate()

        #########################################
        # Run the simulation without attributes #
        #########################################

        # Remove the additional attributes from the created file
        with open(self.__curr_path + '/_estimate_process/est_attribute_without_attr.json', 'w') as file_without_attr:

            with open(self.__curr_path + '/_estimate_process/est_attribute_with_attr.json', 'r') as file_with_attr:

                process = load(file_with_attr)

                # Remove additional attributes
                index = 0
                for attribute in distribution:
                    for _ in range(attribute[1]):
                        del process['order'][0]['attr' + str(index)]
                        index += 1

                json_str = dumps(process)
                file_without_attr.write(json_str)

        # Measure the simulation time
        self.__env.clear_env()
        self.__env.read_files(self.__curr_path + '/_estimate_process/est_attribute_without_attr.json',
                              self.__curr_path + '/_estimate_process/est_attribute_with_func.py')
        time_without_attr = simulate()

        # Remove all created files
        remove(self.__curr_path + '/_estimate_process/est_attribute_with_attr.json')
        remove(self.__curr_path + '/_estimate_process/est_attribute_without_attr.json')
        remove(self.__curr_path + '/_estimate_process/est_attribute_with_func.py')

        return (time_with_attr - time_without_attr) / sim_time

    def est_function(self, function: Callable, num_station: int, track: bool, imports: List[str] = None,
                     objects: Dict[str, object] = None, item_attributes: Dict[str, list] = None,
                     machine_attributes: Dict[str, list] = None, factory_attributes: Dict[str, list] = None) -> float:
        """Estimates the time caused by a specific function.

        :param function: List of attributes to be estimated
        :type function: Callable
        :param num_station: Number of stations at which the process function is called
        :type num_station: int
        :param track: Indicates whether the order is being tracked
        :type track: bool
        :param imports: List of all used import statements
        :type imports: List[str], optional
        :param objects: List of all used objects
        :type objects: List[object], optional
        :param item_attributes: List of all item attributes used in the function
        :type item_attributes: Dict[str, list], optional
        :param machine_attributes: List of all machine attributes used in the function
        :type machine_attributes: Dict[str, list], optional
        :param factory_attributes: List of all factory attributes used in the function
        :type factory_attributes: Dict[str, list], optional
        :raises InvalidFunction: Function name is 'function1'
        :return: Estimated time for a single function call
        :rtype: float

        .. note:
           The function must be a top-level function of the python script and the name of function1 is already occupied
           for internal purposes.

        """

        if function.__name__ == 'function1':
            raise InvalidFunction("The function name 'function1' is occupied for internal purposes")

        if imports is None:
            imports = []
        if objects is None:
            objects = {}
        if item_attributes is None:
            item_attributes = {}
        if machine_attributes is None:
            machine_attributes = {}
        if factory_attributes is None:
            factory_attributes = {}

        # empirical correction factor
        emp_fac = 0.94

        # Attributes to adjust the accuracy of the measurement
        sim_time = 50_000
        max_memory = 2
        bit_type = 32

        @Estimator.timer
        def simulate():
            if track:
                self.__env.simulate(sim_time=sim_time, max_memory=max_memory, bit_type=bit_type)
            else:
                self.__env.simulate(sim_time=sim_time, track_components=[], max_memory=max_memory, bit_type=bit_type)

        ################################################
        # Run the simulation with the process function #
        ################################################

        # Create new json input file
        with open(self.__curr_path + '/_estimate_process/est_function_new.json', 'w') as new_process_file:

            with open(self.__curr_path + '/_estimate_process/est_function.json', 'r') as process_file:

                process = load(process_file)

                # Add the attributes 'station' and 'function' to the order
                process['order'][0]['station'] = ['station' + str(i) for i in range(num_station)]
                process['order'][0]['function'] = ['function1' for _ in range(num_station)]

                # Add the attributes to the order
                for name, distr in item_attributes.items():
                    process['order'][0][name] = distr

                # Add the station objects (and there attributes)
                for i in range(num_station):
                    station_dict = {'name': 'station' + str(i)}
                    for name, distr in machine_attributes.items():
                        station_dict[name] = distr
                    process['station'].append(station_dict)

                # Add the factory attributes
                for name, distr in factory_attributes.items():
                    process['factory'][name] = distr

                json_str = dumps(process)
                new_process_file.write(json_str)

        # Measure the simulation time
        self.__env.clear_env()
        self.__env.read_files(self.__curr_path + '/_estimate_process/est_function_new.json',
                              self.__curr_path + '/_estimate_process/est_function.py')
        time_without_func = simulate()

        ###################################################
        # Run the simulation without the process function #
        ###################################################

        # Change the functions to the passes process function
        with open(self.__curr_path + '/_estimate_process/est_function_new.json', 'r') as process_file:

            with open(self.__curr_path + '/_estimate_process/est_function_with_func.json', 'w') as new_process_file:

                process = load(process_file)
                process['order'][0]['function'] = [function.__name__ for _ in range(num_station)]

                json_str = dumps(process)
                new_process_file.write(json_str)

        # Add the passed process function to the py input file
        with open(self.__curr_path + '/_estimate_process/est_function_new.py', 'w') as function_file:

            # Add the imports to the py file
            for import_ in imports:
                function_file.write(import_ + "\n")
            function_file.write("\n \n")

            # Add the objects to the py file
            for name, object_ in objects.items():
                function_file.write(name + ' = ' + str(object_))
            function_file.write("\n \n")

            # Add the default functions (source, function1)
            with open(self.__curr_path + '/_estimate_process/est_function.py', 'r') as base_function_file:

                content = base_function_file.read()
                function_file.write(content)

            # Add the user defined process function
            function_file.write('\n\n' + getsource(function))

        # Measure the simulation time
        self.__env.clear_env()
        self.__env.read_files(self.__curr_path + '/_estimate_process/est_function_with_func.json',
                              self.__curr_path + '/_estimate_process/est_function_new.py')
        time_with_func = simulate()

        # Remove all created files
        remove(self.__curr_path + '/_estimate_process/est_function_with_func.json')
        remove(self.__curr_path + '/_estimate_process/est_function_new.json')
        remove(self.__curr_path + '/_estimate_process/est_function_new.py')

        return (time_with_func - time_without_func) * emp_fac / (sim_time * num_station)
