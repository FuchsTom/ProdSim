from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
import copy

from dash import Dash, dcc, html, dash_table
import dash_cytoscape as cyto
from dash.dependencies import Input, Output

if TYPE_CHECKING:
    # avoid circular imports, since these imports are only used for type hinting
    from prodsim.filehandler import FileHandler
    from prodsim.components import StationData, OrderData


class Visualizer:
    """Serves to visualize the production process to control the input files

    Starts an interactive web application on a local server

    """

    def __init__(self) -> None:

        # Interactive web-application
        self.__app: Optional[Dash] = None

        # Basic data about the graph
        self.__nodes: Optional[List[Dict[str, Any]]] = None
        self.__edges: Optional[List[Dict[str, Any]]] = None
        self.__root_nodes: Optional[str] = None

        # Additional data: Dropdown menu selection options
        self.__dropdown_options: Optional[List[Dict[str, Any]]] = None

    def visualize(self, filehandler: FileHandler) -> None:
        """Entry point method for the Blackboard to start visualization"""

        # Create the app outside of __init__, otherwise every app created in __init__ will be started in case of
        # multiple simulation runs.
        self.__app = Dash('ProdSim_app')

        self.__create_nodes(filehandler.station_data_list, filehandler.order_data_list)
        self.__create_edges(filehandler.order_data_list)
        self.__create_root_nodes(filehandler.order_data_list)

        self.__create_dropdown_options(filehandler.order_data_list)

        self.__define_app(filehandler.order_data_list, filehandler.station_data_list)

        self.__app.run_server(debug=True)

    def __create_nodes(self, station_data_list: List[StationData], order_data_list: List[OrderData]) -> None:
        """Creates a node for each station and order in the production process"""

        # The nodes are saved in the proper format of the library dash_cytoscape:
        # {'data':{'id': .., 'label': ..}, 'classes': ..}

        # Iterate over each station and order
        # The name of each simulation object serves as 'id' and 'label'
        self.__nodes = [{'data': {'id': station.name, 'label': station.name}, 'classes': 'black'}
                        for station in station_data_list] + \
                       [{'data': {'id': order.name, 'label': order.name + '-store'}, 'classes': 'black triangle'}
                        for order in order_data_list]

    def __create_edges(self, order_data_list: List[OrderData]) -> None:
        """Creates the edges between the visited stations and the final memory for each job"""

        # The edges are saved in the proper format of the library dash_cytoscape:
        # {'data':{'source': .., 'target': .., 'label': ..}, 'classes': '..'}

        self.__edges = []

        for order_data in order_data_list:

            for process_step_index, predecessor_station in enumerate(order_data.station[:-1]):
                successor_station: StationData = order_data.station[process_step_index + 1]
                # Create an edge for each predecessor-successor pair. This iterates only up to the penultimate station,
                # since the last station has no successor.

                self.__edges.append({'data': {'source': predecessor_station.name, 'target': successor_station.name},
                                     'classes': 'arrow black'})

            if order_data.station:
                # If there is at least one station in the order, the last station is connected to the final store
                self.__edges.append({'data': {'source': order_data.station[-1].name, 'target': order_data.name},
                                     'classes': 'arrow black'})

            for process_step_index, component_list in enumerate(order_data.component):
                # Adding the edges for assembly process steps. The end stores of the assembly workpieces are connected
                # to the assembly stations

                if component_list:
                    for component in component_list:
                        self.__edges.append({'data': {'source': component.name,
                                                      'target': order_data.station[process_step_index].name},
                                             'classes': 'dashed arrow black'})

    def __create_root_nodes(self, order_data_list: List[OrderData]) -> None:
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

        self.__root_nodes = roots.strip(', ')

    def __create_dropdown_options(self, order_data_list: List[OrderData]) -> None:
        """Creating the dropdown options"""

        # Using the syntax of dash, for each order in the process
        # {'label': .., 'value': ..}
        self.__dropdown_options = [{'label': data.name, 'value': data.name} for data in order_data_list]

    def __define_app(self, order_data_list: List[OrderData], station_data_list: List[StationData]) -> None:
        """Defines the layout and the callbacks of the later web application"""

        ################################
        # Define the Layout of the app #
        ################################

        self.__app.layout = html.Div(children=[

            # The following layout was chosen

            # ======================================================== #
            #                                                          #
            #  Headline (ProdSim)                                      #
            #  _______________________________                         #
            # | Cytoscape (Graph)             |  Label (Order)         #
            # |                               |  Dropdown (Order)      #
            # |              O                |                        #
            # |              |                |  Label (Order Data)    #
            # |              A   A            |  Table (Order Data)    #
            # |             / \ /             |                        #
            # |            O   O              |  Label (Station Data)  #
            # |            |   |              |  Table (Station Data)  #
            # |            A   O              |                        #
            # |                |              |                        #
            # |                A              |                        #
            # |_______________________________|                        #
            #                                                          #
            # ======================================================== #

            # Headline (ProdSim)
            html.H1('ProdSim Visualizer',
                    style={'textAlgin': 'center'}),

            html.Div(
                children=[

                    # Cytoscape (Graph)
                    cyto.Cytoscape(
                        id='cytoscape',
                        elements=self.__nodes + self.__edges,

                        stylesheet=[
                            # Group selectors
                            {'selector': 'node', 'style': {'content': 'data(label)'}},
                            {'selector': 'edge', 'style': {'curve-style': 'bezier'}},
                            # Class selectors
                            {'selector': '.red', 'style': {'background-color': 'red', 'line-color': 'red',
                                                           'target-arrow-color': 'red'}},
                            {'selector': '.black', 'style': {'background-color': 'black', 'line-color': 'black',
                                                             'target-arrow-color': 'black'}},
                            {'selector': '.triangle', 'style': {'shape': 'triangle'}},
                            {'selector': '.arrow', 'style': {'target-arrow-shape': 'triangle'}},
                            {'selector': '.dashed', 'style': {'line-style': 'dashed'}}
                            # {'selector': '.black_node', 'style': {'background-color': 'black'}},
                            # {'selector': '.red_edge', 'style': {'line-color': 'red'}},
                            # {'selector': '.red_node', 'style': {'background-color': 'red'}},
                            # {'selector': '.black_edge', 'style': {'line-color': 'black'}}
                        ],
                        layout={
                            'name': 'breadthfirst',
                            'roots': self.__root_nodes
                        },
                        style={
                            'height': '80vh',
                            'width': '55vw',
                            'border': 'black solid'
                        }
                    )
                ],
                style={'display': 'inline-block',
                       'vertical-align': 'top',
                       'margin-right': '2vw',
                       'margin-left': '1vw'}
            ),

            html.Div(
                children=[

                    # Label (Order)
                    html.Label(
                        'Order:',
                        style={'font-size': '20px'}
                    ),

                    # Dropdown (Order)
                    dcc.Dropdown(
                        id='item_dropdown',
                        options=self.__dropdown_options,
                        value=-1,
                        style={'width': '38vw', 'margin-bottom': '1vw', 'margin-top': '0.4vw', 'border-color': 'black'},
                        placeholder="Select an item"
                    ),

                    # Label (Order Data)
                    html.Label(
                        'Order Data:',
                        style={'font-size': '20px'}
                    ),

                    # Table (Order Data)
                    dash_table.DataTable(
                        id='item_table',
                        columns=[
                            {'name': 'properties', 'id': 'attribute'},
                            {'name': 'value', 'id': 'value'}
                        ],
                        style_table={
                            'width': '38vw',
                            'overflowX': 'auto',
                            'margin-top': '0.4vw',
                            'margin-bottom': '1vw'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'attribute'},
                             'minWidth': '100px', 'width': '100px'}
                        ],
                        style_cell={
                            'textAlign': 'left',
                            'whitespace': 'normal',
                            'height': 'auto',
                            'border': '1px solid black'
                        },
                        style_header={
                            'fontWeight': 'bold',
                            'backgroundColor': 'rgb(230, 230, 230)'
                        }
                    ),

                    # Label (Station Data)
                    html.Label(
                        'Station Data:',
                        style={'font-size': '20px'}
                    ),

                    # Table (Station Data)
                    dash_table.DataTable(
                        id='station_table',

                        columns=[
                            {'name': 'properties', 'id': 'properties'},
                            {'name': 'value', 'id': 'value'}
                        ],
                        style_cell_conditional=[
                            {'if': {'column_id': 'properties'},
                             'minWidth': '100px', 'width': '100px'}
                        ],
                        style_cell={
                            'textAlign': 'left',
                            'whitespace': 'normal',
                            'height': 'auto',
                            'border': '1px solid black'
                        },
                        style_header={
                            'fontWeight': 'bold',
                            'backgroundColor': 'rgb(230, 230, 230)'
                        },
                        fixed_columns={'headers': True, 'data': 1},
                        style_table={
                            'width': '38vw',
                            'minWidth': '38vw',
                            'maxWidth': '38vw',
                            'overflowX': 'auto',
                            'margin-bottom': '2vw',
                            'margin-top': '0.4vw'
                        },
                    ),

                ],
                style={'display': 'inline-block',
                       'vertical-align': 'top',
                       'margin-right': '1vw'}
            )
        ])

        #################################
        # Define the callback functions #
        #################################

        @self.__app.callback(
            Output(component_id='cytoscape', component_property='elements'),
            Input(component_id='item_dropdown', component_property='value')
        )
        def order_select_graph(order_name: str) -> List[Dict[str, Any]]:
            """Defines the behavior of the graph when the user selects a order from the drop-down menu

            The path of the job is highlighted in red in the graph

            """

            # You cannot define a node or edge twice. Therefore, the edges and nodes set must be copied and the desired
            # edges and nodes must be deleted and replaced with red elements.
            nodes: List[Dict[str, Any]] = copy.deepcopy(self.__nodes)
            edges: List[Dict[str, Any]] = copy.deepcopy(self.__edges)

            if type(order_name) != str:
                # When the app is started, this callback method is called with the value -1. To catch this case the
                # basis nodes and edges are returned
                return nodes + edges

            # Get the station and component list of an order by the orders name
            def get_order_attributes(search_order_name: str) \
                    -> Tuple[List[StationData], List[List[Optional[OrderData]]]]:

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
                # final stores themself
                for process_step_index, component_list in enumerate(component_data_list):
                    if component_list:
                        for component in component_list:
                            change_edge_color(component.name, station_data_list_[process_step_index].name,
                                              'dashed arrow black', 'dashed arrow red')
                            change_node_color(component.name, component.name + '-store',
                                              'black triangle', 'red triangle')

                # Also the start station is updated
                change_node_color(station_data_list_[0].name, station_data_list_[0].name, 'black', 'red')

            # Also the final store of the order is updated
            change_node_color(order_name, order_name + '-store', 'black triangle', 'red triangle')

            return nodes + edges

        @self.__app.callback(
            Output(component_id='item_table', component_property='data'),
            Input(component_id='item_dropdown', component_property='value')
        )
        def order_select_table(order_name: str) -> List[Dict[str, Any]]:
            """Defines the behavior of the table (Order Data) when the user selects a order from the drop-down menu

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

        @self.__app.callback(
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
                    # The 'index'-process step is a assembly

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

                    # Add the demand 0 for all other items
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
