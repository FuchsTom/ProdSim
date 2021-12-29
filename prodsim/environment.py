from typing import List

import simpy

from prodsim.filehandler import FileHandler
from prodsim.visualizer import Visualizer
from prodsim.simulator import Simulator
from prodsim.inspector import Inspector
from prodsim.exception import MissingData
from prodsim.components import Component
from prodsim.helper import Helper
from prodsim.tracker import Tracker


class Environment:
    """Execution Environment for the event-based production simulation."""

    def __init__(self):

        self.__env = simpy.Environment()

        self.__filehandler: FileHandler = FileHandler()
        self.__visualizer: Visualizer = Visualizer()
        self.__simulator: Simulator = Simulator()
        self.__inspector: Inspector = Inspector()

    def read_files(self, path_data_file: str, path_function_file: str) -> None:
        """Reads in the process input files.

        :param path_data_file: Path to the JSON file with the process data
        :type path_data_file: str
        :param path_function_file: Path to the py file with the function definitions
        :type path_function_file: str
        :raises FileNotFoundError: Files could not be found
        :raises MissingParameter: The 'order' or 'station' array is not defined in the process file or an order or
            station object has no name
        :raises UndefinedFunction: One of the referenced functions cannot be found in the function file
        :raises UndefinedObject: One of the referenced orders or stations cannot be found in the data file
        :raises InvalidType: The component list has an element that is not of type list, or the capacity of an order or
            station is not of type int
        :raises InvalidValue: The capacity of an order or station is not greater than zero
        :raise NotSupportedParameter: One of the values of the user-defined factory attributes has an undefined
            identifier

        """

        self.__filehandler.read_files(path_data_file, path_function_file, self.__env)

    def inspect(self) -> None:
        """Checks the passed input files for errors of logical and syntactic nature.

        :raises MissingData: ``read_files`` was not called, or the data read in does not contain the arrays
                             'order' and 'station'

        .. note::

           This method is only a support and does not guarantee an error-free simulation run.

        """

        # Check whether an input file has been read in
        if not self.__filehandler.order_data_list and not self.__filehandler.station_data_list:
            raise MissingData("Either no data was read in or the data read in does not contain 'order' or 'station'. ")

        self.__inspector.inspect(self.__filehandler)

    def visualize(self) -> None:
        """Launches an interactive web application to display the input data.
        This method initiates a local development app on a flask server on localhoast:8050.

        :raises MissingData: ``read_files`` was not called or the data read in does not contain the 'order' or 'station'
            array

        .. note::

           This method initiates a local development app on a flask server on localhoast:8050.

        """

        # Check whether an input file has been read in
        if not self.__filehandler.order_data_list and not self.__filehandler.station_data_list:
            raise MissingData("Either no data was read in or the data read in does not contain 'order' or 'station'. ")

        self.__visualizer.visualize(self.__filehandler)

    def simulate(self, sim_time: int, track_components: List[str] = None, progress_bar: bool = False,
                 max_memory: float = 2, bit_type: int = 32) -> None:
        """Starts the simulation run.

        :param sim_time: Simulated time
        :type sim_time: int
        :param track_components: List of strings representing components whose process data is to be stored
        :type track_components: List[str], optional
        :param progress_bar: Specifies whether a progress bar should be displayed
        :type progress_bar: bool, optional
        :param max_memory: Maximal size of a single a numpy data array [Mb]
        :type max_memory: float, optional
        :param bit_type: Bit type with which the values are stored
        :type bit_type: int, optional
        :raises MissingData: ``read_files`` was not called or the data read in does not contain 'order' or 'station'

        """

        # Check whether an input file has been read in
        if not self.__filehandler.order_data_list and not self.__filehandler.station_data_list:
            raise MissingData("Either no data was read in or the data read in does not contain 'order' or 'station'. ")

        self.__simulator.simulate(self.__filehandler, sim_time, self.__env, track_components, progress_bar, max_memory,
                                  bit_type)

    def data_to_csv(self, path_to_wd: str, remove_column: List[str] = None, keep_original: bool = True) -> None:
        """Exports the simulation data to csv files.

        :param path_to_wd: Path to the target directory
        :type path_to_wd: str
        :param remove_column: List of labels whose columns are removed before saving
        :type remove_column: List[str], optional
        :param keep_original: Keep an additional original file without removed columns
        :type keep_original: bool, optional
        :raises MissingData: ``simulate`` was not called before

        .. note::

           If the passed folder does not exist, then the program creates it.

        """

        if remove_column is None:
            remove_column = []

        self.__filehandler.data_to_csv(path_to_wd, remove_column, keep_original)
    
    def data_to_hdf5(self, path_to_wd: str, file_name: str) -> None:
        """Exports the simulation data to hdf5 files.
    
        Creates a hdf5 file in which each simulation object is stored a group. The metadata ('header') of each
        simulation object is stored in an attribute and the simulation data in datasets of size max_memory.
    
        :param path_to_wd: Path to the target directory
        :type path_to_wd: str
        :param file_name: Name of the hdf5 file
        :type file_name: str
        :raises MissingData: ``simulate`` was not called before
    
        .. note::
    
           If the passed folder does not exist, then the program creates it.
    
        """

        self.__filehandler.data_to_hdf5(path_to_wd, file_name)

    def clear_env(self) -> None:
        """Reinitialize the environment object between two different simulation runs.

        After calling this method, a new process must be read in.

        """

        # Resetting the blackboard. All experts are provided with fresh attributes
        self.__init__()

        # Reset all static attributes of classes that are not part of the blackboard structure
        Component.clear_cache()
        Tracker.clear_tracked_orders()
        Tracker.clear_tracked_sim_obj()
        Helper.clear_ud_switch_dict()

    def define_process(self) -> None:
        """Launches an interactive web application to define a new production process.
        This method initiates a local development app on a flask server on localhoast:8050.

        """

        self.__visualizer.define_process()