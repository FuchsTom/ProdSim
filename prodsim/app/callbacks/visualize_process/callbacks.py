""" This module contains the callback functions used in the app ‚visualize'.

The utilities used, can be found in prodsim.app.callbacks.visualize_process.support
"""

# Searchable TOC of callback methods:
#
# order_select_graph   #0001
# order_select_table   #0002
# station_select_table #0003

from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional, TYPE_CHECKING
from copy import deepcopy

from dash.dependencies import Output, Input

from prodsim.app.callbacks.visualize_process.support import (
    create_nodes,
    create_edges,
    create_root_nodes,
    create_dropdown_options
)

if TYPE_CHECKING:
    from prodsim.components import StationData, OrderData

# Global attributed, that hold information about the graph and the dropdown options
glob_nodes: Optional[List[Dict[str, Any]]] = None
glob_edges: Optional[List[Dict[str, Any]]] = None
glob_root_nodes: Optional[str] = None
dropdown_options: Optional[List[Dict[str, Any]]] = None


def vis_callbacks(app, order_data_list: List[OrderData], station_data_list: List[StationData]):

    # Global attributes
    global glob_nodes, glob_edges, glob_root_nodes, dropdown_options
    glob_nodes = create_nodes(station_data_list, order_data_list)
    glob_edges = create_edges(order_data_list)
    glob_root_nodes = create_root_nodes(order_data_list)
    dropdown_options = create_dropdown_options(order_data_list)

    # order_select_graph  # 0001
    @app.callback(
        [Output(component_id='cytoscape', component_property='elements'),
         Output(component_id='item_dropdown', component_property='options')],
        Input(component_id='item_dropdown', component_property='value')
    )
    def order_select_graph(order_name: str) -> tuple:
        """Defines the behavior of the graph when the user selects an order from the drop-down menu

        The path of the job is highlighted in red in the graph

        """

        # You cannot define a node or edge twice. Therefore, the edges and nodes set must be copied and the desired
        # edges and nodes must be deleted and replaced with red elements.
        nodes: List[Dict[str, Any]] = deepcopy(glob_nodes)
        edges: List[Dict[str, Any]] = deepcopy(glob_edges)

        if type(order_name) != str:
            # When the app is started, this callback method is called with the value -1. To catch this case the
            # basis nodes and edges are returned
            return nodes + edges, dropdown_options

        # Get the station and component list of an order by the orders name
        def get_order_attributes(search_order_name: str) -> Tuple[List[StationData], List[List[Optional[OrderData]]]]:

            for order_data in order_data_list:
                if order_data.name == search_order_name:
                    return order_data.station, order_data.component

        # Changes the color of an edge
        def change_edge_color(edge_source: str, edge_target: str, old_classes: str, new_classes: str):
            edges.remove({'data': {'source': edge_source,
                                   'target': edge_target},
                          'classes': old_classes})
            edges.append({'data': {'source': edge_source,
                                   'target': edge_target},
                          'classes': new_classes})

        # Changes the color of a node
        def change_node_color(node_id: str, node_label: str, old_classes: str, new_classes: str):
            element = {'data': {'id': node_id,
                                'label': node_label},
                       'classes': old_classes}
            if element in nodes:
                nodes.remove(element)
            nodes.append({'data': {'id': node_id,
                                   'label': node_label},
                          'classes': new_classes})

        station_data_list_: List[StationData]
        component_data_list: List[List[Optional[OrderData]]]
        station_data_list_, component_data_list = get_order_attributes(order_name)

        if station_data_list_:

            # Update all predecessor-successor edges of the order ()
            for process_step_index, predecessor_station in enumerate(station_data_list_[:-1]):
                successor_station: StationData = station_data_list_[process_step_index + 1]
                change_edge_color(predecessor_station.name, successor_station.name, 'arrow black', 'arrow red')

            # Update the edge from the Last Station to the Final Store
            change_edge_color(station_data_list_[-1].name, order_name, 'arrow black', 'arrow red')

            # Update all edges from assembly workpiece final stores to the appropriate assembly stations and the
            # final stores themselves
            for process_step_index, component_list in enumerate(component_data_list):
                if component_list:
                    for component in component_list:
                        change_edge_color(component.name, station_data_list_[process_step_index].name,
                                          'dashed arrow black', 'dashed arrow red')
                        change_node_color(component.name, component.name + '-store',
                                          'black triangle', 'red triangle')

            # Also, the start station is updated
            change_node_color(station_data_list_[0].name, station_data_list_[0].name, 'black', 'red')

        # Also, the final store of the order is updated
        change_node_color(order_name, order_name + '-store', 'black triangle', 'red triangle')

        return nodes + edges, dropdown_options

    # order_select_table #0002
    @app.callback(
        Output(component_id='item_table', component_property='data'),
        Input(component_id='item_dropdown', component_property='value')
    )
    def order_select_table(order_name: str) -> List[Dict[str, Any]]:
        """Defines the behavior of the table (Order Data) when the user selects an order from the drop-down menu

        The information shown in the table (Order Data) will be updated

        """

        # When starting the app and removing a selection, no string of the selected items is passed, but a number.
        # In this case, all standard nodes and edges are simply returned in black and the method call is terminated.
        if type(order_name) != str:
            return []

        # Returns the order object by name
        def get_order_by_name(search_order_name: str) -> OrderData:
            for order_data_ in order_data_list:
                if order_data_.name == search_order_name:
                    return order_data_

        order_data: OrderData = get_order_by_name(order_name)

        # Adding the data that each job has
        table_data: List[Dict[str, Any]] = [{'attribute': 'name', 'value': order_data.name},
                                            {'attribute': 'priority', 'value': order_data.priority},
                                            {'attribute': 'source', 'value': order_data.source.__name__}]

        # Adding the table entry 'sink', depending on whether the user has specified a sink
        if order_data.sink is not None:
            table_data.append({'attribute': 'sink', 'value': order_data.sink.__name__})
        else:
            table_data.append({'attribute': 'sink', 'value': 'default sink'})

        # Adding all attributes and their distributions to the table
        for attribute_name, attribute_value in order_data.attribute.items():
            table_data.append({'attribute': attribute_name, 'value': str(attribute_value)})

        return table_data

    # station_select_table #0003
    @app.callback(
        Output(component_id='station_table', component_property='data'),
        Input(component_id='item_dropdown', component_property='value'),
        Input(component_id='cytoscape', component_property='tapNodeData')
    )
    def station_select_table(order_name: str, station_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Defines the behavior of the table (Station Data) when the user selects a station from the process graph

        The information shown in the table (Station Data) will be updated. In addition to the selected station, the
        information shown in the nag also depends on the selected job.

        """

        # List containing the information to be displayed in the table.
        table_data: List[Dict[str, Any]] = []

        # Returns the order object by name
        def get_order_data_by_name(search_order_name: str) -> OrderData:
            for order_data_ in order_data_list:
                if order_data_.name == search_order_name:
                    return order_data_

        # Returns the station object by name
        def get_station_data_by_name(search_station_name: str) -> StationData:
            for station_data_ in station_data_list:
                if station_data_.name == search_station_name:
                    return station_data_

        # Returns a list of indices where the station is located in the process (order) under consideration.
        def get_process_index(item_data_: OrderData, station_name) -> List[int]:
            index_list_: List[int] = []
            for index_, station_data_ in enumerate(item_data_.station):
                if station_data_.name == station_name:
                    index_list_.append(index_)
            return index_list_

        # There are three different combinatorial possibilities from the various selection options

        # ---- No station is selected -----------------

        # If no station was selected, the table does not contain any data
        if station_info is None:
            return table_data

        # ---- Selected station -----------------------

        station_data: StationData = get_station_data_by_name(station_info['id'])

        if station_info['label'][-6:] == '-store':
            # Selected node is a final store

            order_data: OrderData = get_order_data_by_name(station_info['id'])

            # Add row 'name' to the table
            table_data.append({'properties': 'name', 'value': station_info['id']})

            # Add row 'storage' to the table
            if order_data.storage == float('inf'):
                table_data.append({'properties': 'storage', 'value': 'infinite'})
            else:
                table_data.append({'properties': 'storage', 'value': order_data.storage})

            # All possible data was collected
            return table_data
        else:
            # Selected node is a station

            # Add rows 'name', 'capacity' and 'measurement' to the table
            table_data.append({'properties': 'name', 'value': station_data.name})
            table_data.append({'properties': 'capacity', 'value': station_data.capacity})
            table_data.append({'properties': 'measurement', 'value': station_data.measurement})

            # Add row 'storage' to the table
            if station_data.storage == float('inf'):
                table_data.append({'properties': 'storage', 'value': 'infinite'})
            else:
                table_data.append({'properties': 'storage', 'value': station_data.storage})

            # Add the user-defined attributes to the table
            for attribute_name, attribute_value in station_data.attribute.items():
                table_data.append({'properties': attribute_name, 'value': str(attribute_value)})

        # ---- Also an order is selected --------------

        if type(order_name) != str:
            # When starting the app no station is selected and order_name is -1 by default. This case is bypassed
            return table_data

        order_data: OrderData = get_order_data_by_name(order_name)
        index_list: List[int] = get_process_index(order_data, station_info['id'])
        function_list: List[str] = []
        # If the selected station is not part of the order, index_list is empty
        # The string represents the name of the item and the list represents the demand of this particular item at
        # a specific index step
        demand_dict: Dict[str, List[int]] = {order_data.name: []} if index_list else {}

        for loop_num, index in enumerate(index_list):

            # Add the name of the function at process step 'index' to the function_list
            function_list.append(order_data.function[index].__name__)

            if order_data.component[index]:
                # The 'index'-process step is an assembly

                # In case of an assembly the demand is always 1
                demand_dict[order_data.name].append(1)

                # Get the names of all assembled items
                assembled_components: Dict[str, int] = {order_data_.name: index_ for index_, order_data_ in
                                                        enumerate(order_data.component[index])}

                # Check if the demand_dict already keys are in the assembled items at this process step
                # if yes: add the related demand
                # if no: add 0
                for key, value in demand_dict.items():

                    if key == order_data.name:
                        # The main item is already handled
                        continue

                    if key in assembled_components:
                        demand_dict[key].append(order_data.demand[index][assembled_components[key]])
                        assembled_components.pop(key)
                    else:
                        demand_dict[key].append(0)

                # Since already existing items have been removed from the dict 'assembled_components' there are now
                # only new items in the dictionary.
                # The lists must be padded with zeros up to the current 'loop_num', since they did not occur
                # previously
                for component_name, component_index in assembled_components.items():
                    demand_dict[component_name] = [0] * loop_num + \
                                                  [order_data.demand[index][component_index]]
            else:
                # The 'index'-process step is a machining

                # Add the demand of the main item
                demand_dict[order_data.name].append(order_data.demand[index])

                # Add the demand 0 for all others items
                for key, value in demand_dict.items():
                    if key == order_data.name:
                        continue
                    demand_dict[key].append(0)

        # Add the functions and the demand to the table
        if function_list:
            table_data.append({'properties': 'function', 'value': str(function_list)})
        if demand_dict:
            for key, value in demand_dict.items():
                table_data.append({'properties': 'demand-' + key, 'value': str(value)})

        return table_data
