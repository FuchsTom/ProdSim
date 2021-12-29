"""
This module bundles some functionality that is needed by multiple callbacks or is too large to integrate logically into
a callback function.
"""

# Searchable TOC of support-functions:
#
# create_nodes            #0001
# create_edges            #0002
# create_root_nodes       #0003
# create_dropdown_options #0004

from __future__ import annotations
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from prodsim.components import StationData, OrderData


# create_nodes #0001
def create_nodes(station_data_list: List[StationData], order_data_list: List[OrderData]) -> List[Dict[str, Any]]:
    """Creates a node for each station and order in the production process"""

    # The nodes are saved in the proper format of the library dash_cytoscape:
    # {'data':{'id': .., 'label': ..}, 'classes': ..}

    # Iterate over each station and order
    # The name of each simulation object serves as 'id' and 'label'
    return [{'data': {'id': station.name, 'label': station.name}, 'classes': 'black'}
            for station in station_data_list] + \
           [{'data': {'id': order.name, 'label': order.name + '-store'}, 'classes': 'black triangle'}
            for order in order_data_list]

# create edges #0002
def create_edges(order_data_list: List[OrderData]) -> List[Dict[str, Any]]:
    """Creates the edges between the visited stations and the final memory for each job"""

    # The edges are saved in the proper format of the library dash_cytoscape:
    # {'data':{'source': .., 'target': .., 'label': ..}, 'classes': '..'}

    edges = []

    for order_data in order_data_list:

        for process_step_index, predecessor_station in enumerate(order_data.station[:-1]):
            successor_station: StationData = order_data.station[process_step_index + 1]
            # Create an edge for each predecessor-successor pair. This iterates only up to the penultimate station,
            # since the last station has no successor.

            edges.append({'data': {'source': predecessor_station.name, 'target': successor_station.name},
                          'classes': 'arrow black'})

        if order_data.station:
            # If there is at least one station in the order, the last station is connected to the final store
            edges.append({'data': {'source': order_data.station[-1].name, 'target': order_data.name},
                          'classes': 'arrow black'})

        for process_step_index, component_list in enumerate(order_data.component):
            # Adding the edges for assembly process steps. The end stores of the assembly workpieces are connected
            # to the assembly stations

            if component_list:
                for component in component_list:
                    edges.append({'data': {'source': component.name,
                                           'target': order_data.station[process_step_index].name},
                                  'classes': 'dashed arrow black'})

    return edges

# create_root_nodes #0003
def create_root_nodes(order_data_list: List[OrderData]) -> str:
    """Defining the root nodes to arrange the nodes based on them in a tree structure

    Root nodes are all station-nodes that have no predecessor and are not an assembly station

    """

    # Root nodes are all nodes that have no predecessor and are not an assembly station
    order_with_process: List[OrderData] = list(order for order in order_data_list if len(order.station) > 0)

    # List of all jobs whose first station is a root node
    first_station_name: List[str] = []

    # Filtering of all stations names that are in the first position in the process and do not perform assembly
    for order_data in order_with_process:
        if isinstance(order_data.demand[0], list):
            continue
        first_station_name.append(order_data.station[0].name)
    first_station_name = list(set(first_station_name))

    # Remove all station names whose stations are not in the first place with respect to another process.
    for order_data in order_data_list:
        for station_data in order_data.station[1:]:
            if station_data.name in first_station_name:
                if station_data.name == order_data.station[0].name:
                    # Only exception: in the process where the station is again appearance is also the process where
                    # the station is in the first place
                    continue
                first_station_name.remove(station_data.name)

    # According to the library dash_cytoscape the following syntax must be used regarding the root nodes
    # '#root_name_1, #root_name_2, ... #root_name_n'
    roots: str = ''
    for station_name in first_station_name:
        roots += '#' + station_name + ', '

    return roots.strip(', ')

# create_dropdown_options #0004
def create_dropdown_options(order_data_list: List[OrderData]) -> List[Dict[str, Any]]:
    """Creating the dropdown options"""

    # Using the syntax of dash, for each order in the process
    # {'label': .., 'value': ..}
    return [{'label': data.name, 'value': data.name} for data in order_data_list]
