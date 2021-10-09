from typing import List, Any, Union, Optional, Dict
from os import path

from h5py import File
from numpy import empty, isnan, nan

from prodsim.components import (
    OrderData,
    StationData,
    FactoryData,
    Item,
    Machine,
    Factory,
    Component
)

class Tracker:
    """Provides all functions for caching the simulation data during a simulation run"""

    # Dictionary of all orders to be tracked
    __tracked_orders: Dict[str, OrderData] = {}

    # Currently used row in the numpy array
    __tracked_sim_obj: List[Any] = []

    def __init__(self, max_memory_size: float, dtype: int, num_attr: int, name: str) -> None:

        self.name = name
        self.num_attr = num_attr

        # Number of temporary csv files of the current component
        self.num_temp_file: int = 0

        # Indicates how many rows have been read into the current array.
        self.current_arr_num: int = 0

        # determinate the data type and the bytes per array entry
        self.dtype_: str
        byte_per_entry: int
        if dtype == 16:
            self.dtype_ = 'float16'
            byte_per_entry = 2
        elif dtype == 32:
            self.dtype_ = 'float32'
            byte_per_entry = 4
        else:
            self.dtype_ = 'float64'
            byte_per_entry = 8

        # Calculate allowed array length so that the allowed amount of memory is not exceeded.
        # memory usage = rows * columns * byte_per_entry
        # cut off the result with 'int()'
        # 1_000_000 is used because, the unit of 'max_memory_size' is [Mb]
        self.max_arr_length = int(max_memory_size * 1_000_000 / num_attr / byte_per_entry)

        # Create the numpy array of the calculated size and fill it with nan's
        self.arr = empty((self.max_arr_length, self.num_attr), dtype=self.dtype_)
        self.arr[:] = nan

    @staticmethod
    def set_tracked_orders(tracked_orders: Dict[str, Any]) -> None:
        """Setting the tracked_orders attribute"""

        Tracker.__tracked_orders = tracked_orders

    @staticmethod
    def clear_tracked_orders() -> None:
        """Reset the tracked_orders attribute"""

        Tracker.__tracked_orders = {}

    @staticmethod
    def set_tracked_sim_obj(tracked_sim_obj: List[Any]) -> None:
        """Setting the tracked_sim_obj attribute"""

        Tracker.__tracked_sim_obj = tracked_sim_obj

    @staticmethod
    def clear_tracked_sim_obj() -> None:
        """Reset the tracked_sim_obj attribute"""

        Tracker.__tracked_sim_obj = {}

    @staticmethod
    def setup_file(bit_type: int, assemble_items: List[str]) -> None:
        """Create the h5 file to cache the simulation data starting from the numpy arrays

        For each component to be tracked, a group is created in the h5 file

        """

        # Round according to the selected bit_type
        fmt: str
        if bit_type == 16:
            fmt = '%.4g'
        elif bit_type == 32:
            fmt = '%.8g'
        else:
            fmt = '%.16g'

        # Create h5 file
        with File(path.join(path.dirname(__file__) + '/_temp_data/_temp/hdf5.hdf5'), 'w') as hdf:

            # set the formatting standard as a file attribute
            hdf.attrs['fmt'] = fmt

            for sim_obj in Tracker.__tracked_sim_obj:

                # create a group with the name of the tracked component
                g = hdf.create_group(name=sim_obj.name)

                # Adding the user-defined attributes to the header
                header_list: List[str] = [key for key in sim_obj.attribute.keys()]

                # Adding the Default Attributes to the Header
                if isinstance(sim_obj, OrderData):
                    header_list.append('item_id')
                    header_list = sorted(header_list)
                    if sim_obj.name in assemble_items:
                        header_list.append('comp')
                    header_list.extend(['station_id', 'time'])
                elif isinstance(sim_obj, StationData):
                    header_list.append('machine_nr')
                    header_list = sorted(header_list)
                    header_list.append('time')
                elif isinstance(sim_obj, FactoryData):
                    header_list = sorted(header_list)
                    header_list.append('time')

                # set header as an group attribute
                g.attrs['header'] = header_list

    @staticmethod
    def track_nested_item(item: Union[Item, List[Item]], time: float, station_id: int, comp: Optional[int] = None) \
            -> None:
        """Decode the assembly structure of a given workpiece via recursive method calls for each assembly hierarchy
        level and then call the concrete tracker method for items.

        """

        # ---- Track the top-level item(s) ----------------

        # Check whether it is a single item or multiple items in a list
        single_item: bool
        item_id: Optional[int, List[int]]
        tracked: bool
        name: str
        if isinstance(item, list):
            single_item = False
            item_id = [item[i].item_id for i in range(len(item))]
            tracked = item[0].name in Tracker.__tracked_orders
            name = item[0].name
        else:
            single_item = True
            item_id = item.item_id
            tracked = item.name in Tracker.__tracked_orders
            name = item.name

        # Call the concrete track method
        if tracked:
            if single_item:
                Tracker.__tracked_orders[name].tracker.track_component(item, time, station_id, comp)
            else:
                for item_ in item:
                    Tracker.__tracked_orders[name].tracker.track_component(item_, time, station_id, comp)

        # ---- Track the sub items of item ----------------

        def track_sub_item(main_item: Item, index_: int = None):
            # Recursively call the method 'track_nested_item' for all assembly item in the hierarchy level below item

            for sub_item_name in main_item.assembled_item_dict.keys():
                # Loop over all assembled workpieces

                # If workpieces of an order were mounted to the main workpiece in different process steps, then these
                # are provided from the second time with the prefix '_' and a continuous suffix. To get access to the
                # OrderData object of this assembly workpiece, the name must be cleaned of these components.
                # sub_item_name_clean: str = sub_item_name
                # if sub_item_name[0] == '_':
                #    sub_item_name_clean = sub_item_name[1:-1]

                # Recursively call the current method for the sub items
                if index_ is None:
                    Tracker.track_nested_item(
                        main_item.__getattribute__(sub_item_name), time, station_id, item_id)
                else:
                    Tracker.track_nested_item(
                        main_item.__getattribute__(sub_item_name), time, station_id, item_id[index_])

        if single_item:
            track_sub_item(item)
        else:
            for index, item_ in enumerate(item):
                track_sub_item(item_, index)

    def track_component(self, component: Component, time, process_step: int = None, comp: int = None) -> None:
        """Store the current component attribute values in the corresponding numpy array"""

        if self.current_arr_num < self.max_arr_length:
            # Current cache-numpy-array is not filled yet

            row: int = self.current_arr_num
            num_attr: int = self.num_attr

            # Saving the predefined columns at the end of the respective row vector
            if isinstance(component, Item):
                if comp is not None:
                    self.arr[row][num_attr - 3] = comp
                self.arr[row][num_attr - 2] = process_step
                self.arr[row][num_attr - 1] = time
            elif isinstance(component, Machine):
                self.arr[row][num_attr - 1] = time
            elif isinstance(component, Factory):
                self.arr[row][num_attr - 1] = time

            # Saving the user-defined attributes by iterating over them
            for index, value in enumerate(component.values()):
                self.arr[row][index] = value

            self.current_arr_num += 1
        else:
            # Cache the current numpy-array in the h5 file and delete the array
            self.__cache_data_memory_wise()
            del self.arr

            # Create a new array
            self.arr = empty((self.max_arr_length, self.num_attr), dtype=self.dtype_)
            self.arr[:] = nan

            # reset the counter
            self.current_arr_num = 0

            # recursive call
            self.track_component(component, time, process_step, comp)

    def __cache_data_memory_wise(self) -> None:
        """Caches the numpy array of a tracker instance in the temporary h5 file"""

        with File(path.join(path.dirname(__file__) + '/_temp_data/_temp/hdf5.hdf5'), 'r+') as hdf:

            # Get the group
            g = hdf.get(self.name)

            # Create dataset from numpy array
            g.create_dataset(name=str(self.num_temp_file), data=self.arr, dtype=self.dtype_)

        # Increase the file counter
        self.num_temp_file += 1

    def cache_data_final(self) -> None:
        """Caches the numpy array of a tracker instance in the temporary h5 file, after simulation end"""

        with File(path.join(path.dirname(__file__) + '/_temp_data/_temp/hdf5.hdf5'), 'r+') as hdf:

            # Get the group
            g = hdf.get(self.name)

            # Create dataset from numpy array, and remove all 'nan' rows
            g.create_dataset(name=str(self.num_temp_file), data=self.arr[~isnan(self.arr).all(axis=1)],
                             dtype=self.dtype_)
