""" This module contains the callback functions used in the app ‚define process'.

The utilities used, can be found in prodsim.app.callbacks.define_process.support
"""

# Searchable TOC of callback methods:
#
# Refresh graph         #0001
# Open add order        #0002
# Info add order        #0003
# Add order             #0004
# Open save files       #0005
# Info save files       #0006
# Save files            #0007
# Open combine stations #0008
# Info combine stations #0009
# Combine stations      #0010
# Select node           #0011
# Change order          #0012
# Info change order     #0013
# Change station        #0014
# Add attribute         #0015
# Info add attribute    #0016
# Edit factory          #0017
# Info edit factory     #0018

from json import dump
import os

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from dash import callback_context, no_update

from prodsim.app.callbacks.define_process.support import *

# Counter variables that track how many times a window has been opened
count_add_order: int = 0
count_create_files: int = 0
count_combine_stations: int = 0
count_change_order: int = 0
count_change_station: int = 0

# Variables for caching user input during a dialog interaction
cache_order: dict = {}
cache_attr: dict = {}
selected_station = ''

# Process data
process_data: dict = {
    'order': [],
    'station': [],
    'factory': {
        'function': []
    }
}

# Current dialog (for attribute adding)
curr_dia: Tuple[str, str] = ('', '')


def dp_callbacks(app):

    # Refresh Graph #0001
    @app.callback(
        [Output(component_id='cytoscape', component_property='elements'),
         Output(component_id='cytoscape', component_property='layout')],
        Input(component_id='refresh-graph', component_property='n_clicks')
    )
    def refresh_graph(n_clicks) -> tuple:
        """
        Input: Click on the 'refresh graph' button
        Output: Elements displayed in the cyto-graph

        First all nodes and edges are deleted and based on the currently defined process all nodes and edges are
        redefined. This is because each object must have a unique id, which is ensured by deleting old objects.
        """

        layout = {
                     'name': 'breadthfirst',
                     'roots': []
                 }

        # Starting the app
        if not n_clicks:
            return [], layout

        # Lists in which the elements are created locally
        nodes = []
        edges = []

        # Create new edges and nodes
        for order in process_data['order']:

            # Create a node for each station of the order and one for the final store for each order.
            nodes += [{'data': {'id': station_name, 'label': station_name},
                      'classes': 'black'} for station_name in order['station']] + \
                    [{'data': {'id': order['name'], 'label': order['name']},
                      'classes': 'black triangle'}]

            # Create edges between each station of a job and between the last station of a job and the final memory.
            for i in range(len(order['station'])):

                if i < len(order['station']) - 1:
                    target = order['station'][i + 1]
                else:
                    target = order['name']

                edges.append({'data': {'source': order['station'][i],
                                       'target': target},
                              'classes': 'arrow black'})

                # Create an edge for each assembly relationship.
                # From the end store to the station where the assembly is executed
                if comp := order['component'][i]:

                    for(ass_order) in comp:

                        edges.append({'data': {'source': ass_order,
                                               'target': order['station'][i]},
                                      'classes': 'arrow black'})

        layout['roots'] = root_nodes(process_data['order'])

        return edges + nodes, layout

    # Open add order #0002
    @app.callback(
        Output('modal', 'is_open'),
        Input('add-order', 'n_clicks'),
        State('modal', 'is_open')
    )
    def open_add_order_dialog(n_clicks, is_open) -> bool:
        """
        Input: Click on the 'add order' button and information, if the modal is open
        Output: boolean, if the modal is open

        Opens the modal 'add order'
        """

        if n_clicks:
            return not is_open

        return is_open

    # Info add order #0003
    @app.callback(
        Output(component_id='add_order_info', component_property='displayed'),
        Input(component_id='info_add_order', component_property='n_clicks')
    )
    def info_add_order(n_clicks) -> bool:
        """
        Input: Click on the 'info' button
        Output: boolean, if the modal is open

        Opens the 'add order info' window
        """

        if n_clicks:
            return True

        return False

    # Add order #0004
    @app.callback(
        [Output(component_id='order_name_input', component_property='value'),
         Output(component_id='source_name_input', component_property='value'),
         Output(component_id='sink_name_input', component_property='value'),
         Output(component_id='number_stations_input', component_property='value'),
         Output(component_id='storage_input', component_property='value'),
         Output(component_id='priority_input', component_property='value'),
         Output(component_id='add_order_alert', component_property='displayed'),
         Output(component_id='add_order_alert', component_property='message')],
        [Input(component_id='submit_add_order', component_property='n_clicks'),
         Input(component_id='order_name_input', component_property='value'),
         Input(component_id='source_name_input', component_property='value'),
         Input(component_id='sink_name_input', component_property='value'),
         Input(component_id='number_stations_input', component_property='value'),
         Input(component_id='storage_input', component_property='value'),
         Input(component_id='priority_input', component_property='value')]
    )
    def update_add_order(n_clicks, name_order, name_source, name_sink, num_stations, storage, priority) -> tuple:
        """
        Input: All text fields of the dialog, as well as the submit button, with which the data will be saved.
        Output: All text fields of the window, plus a boolean and a string that can be used to output error messages.

        First, the user input is processed and checked for correctness. If the input is correct, the corresponding
        entries are made in the process file.
        """
        global count_add_order

        # Starting the ap
        if not count_add_order < n_clicks:
            raise PreventUpdate

        # Update page counter
        count_add_order += 1

        # Format user input
        user_input: Dict[str, str] = {
            'order name': name_order,
            'source name': name_source,
            'sink name': name_sink,
            'number stations': num_stations,
            'storage': storage,
            'priority': priority
        }

        # Open error-dialog, if the input is not valid
        if errors := check(process_data, user_input):

            error_msg = "ERROR: \n" + ''.join(str(i + 1) + ". " + error + "\n" for i, error in enumerate(errors))

            return name_order, name_source, name_sink, num_stations, storage, priority, True, error_msg

        # Set the default values, if the user did not specify them
        name_sink = name_sink if name_sink else None
        num_stations = int(num_stations) if num_stations else 0
        storage = int(storage) if storage else None
        priority = int(priority) if priority else 10

        # Add an order-dict to the process_data
        process_data['order'].append(
            {
                'name': name_order,
                'priority': priority,
                'storage': storage,
                'source': name_source,
                'sink': name_sink,
                'station': [name_order + str(i + 1) for i in range(int(num_stations))],
                'function': [name_order + str(i + 1) + "_func" for i in range(int(num_stations))],
                'demand': [1 for _ in range(int(num_stations))],
                'component': [[] for _ in range(int(num_stations))]
            }
        )

        # Add a station-dict to the process_data
        for i in range(int(num_stations)):
            process_data['station'].append(
                {
                    'name': name_order + str(i + 1),
                    'capacity': 1,
                    'storage': None,
                    'measurement': False,
                }
            )

        # Clear all text fields, so the user can add further orders
        return '', '', '', '', '', '', False, ''

    # Open save files #0005
    @app.callback(
        Output(component_id='modal_creat_files', component_property='is_open'),
        Input(component_id='create-files', component_property='n_clicks'),
        State('modal_creat_files', 'is_open')
    )
    def open_create_files(n_clicks, is_open) -> bool:
        """
        Input: Click on the 'refresh graph' button and information, if the modal ist open
        Output: boolean, if the modal is open

        Opens the modal 'create files'
        """

        if n_clicks:
            return not is_open

        return is_open

    # Info save files #0006
    @app.callback(
        Output(component_id='create_files_info', component_property="displayed"),
        Input(component_id='info_create_files', component_property="n_clicks"),
    )
    def create_files_info(n_clicks) -> bool:
        """
        Input: Click on the 'info' button
        Output: boolean, if the modal is open

        Opens the window 'create file info'
        """

        if n_clicks:
            return True

        return False

    # Save files #0007
    @app.callback(
        [Output(component_id='invalid_path', component_property='is_open'),
         Output(component_id='created_files', component_property='is_open'),
         Output(component_id='path_input', component_property='value'),
         Output(component_id='name_input', component_property='value'),
         Output(component_id='create_files_alert', component_property='displayed'),
         Output(component_id='create_files_alert', component_property='message')],
        [Input(component_id='submit_create_files', component_property='n_clicks'),
         Input(component_id='path_input', component_property='value'),
         Input(component_id='name_input', component_property='value')]
    )
    def create_files(n_clicks, path, project_name) -> tuple:
        """
        Input: Path and Filename information, submit-Button
        Output: Alert-, Info-, Success-Window

        Create the .py and .json file based on the global variable process_data
        """
        global count_create_files

        if not count_create_files < n_clicks:
            raise PreventUpdate

        # Update click count
        count_create_files += 1

        # Format user input
        user_input: Dict[str, str] = {
            'path': path,
            'project name': project_name
        }

        # Open error-dialog, if the input is not valid
        if errors := check(process_data, user_input):
            error_msg = "ERROR: \n" + ''.join(str(i + 1) + ". " + error + "\n" for i, error in enumerate(errors))

            return False, False, path, project_name, True, error_msg

        # Check if path is valid
        if path[-1] not in ['/', '\\']:
            path += '/'
        if not os.path.isdir(path):
            return True, False, path, project_name, False, ''

        # Create json file
        with open(path + project_name + '_process.json', 'w') as f:

            _process_data = clear_process_data(process_data)

            dump(_process_data, f, indent=4)

        # Get all process functions, sources and sinks
        process_func: List[str] = []
        source_sink: List[str] = []
        global_func: List[str] = []
        for order in process_data['order']:
            process_func += order['function']
            source_sink += [order['source']]
            if sink := order['sink']:
                source_sink += [sink]
        if g_func := process_data['factory']['function']:
            global_func += g_func

        # Create the python file
        with open(path + project_name + '_function.py', 'w') as f:

            f.write(
                "# ---- process models ---- \n" +
                txt_python_func(process_func, 'p') +
                "# ---- sources and sinks ---- \n" +
                txt_python_func(source_sink, 's') +
                "# ---- global functions ---- \n" +
                txt_python_func(global_func, 'g')
            )

        return False, True, '', '', False, ''

    # Open combine stations #0008
    @app.callback(
        Output(component_id='modal_combine_stations', component_property='is_open'),
        Input(component_id='combine-stations', component_property='n_clicks'),
        State('modal_combine_stations', 'is_open')
    )
    def open_create_files(n_clicks, is_open) -> bool:
        """
        Input: Click on the 'combine stations' button and information, if the modal ist open
        Output: boolean, if the modal is open

        Opens the modal 'create files'
        """

        if n_clicks:
            return not is_open

        return is_open

    # Info combine stations #0009
    @app.callback(
        Output(component_id='combine_stations_info', component_property='displayed'),
        Input(component_id='cs_info', component_property='n_clicks')
    )
    def info_combine_stations(n_clicks) -> bool:
        """
        Input: Click on the 'info' button
        Output: boolean, if the modal is open

        Opens the window 'combine stations info'
        """

        if n_clicks:
            return True

        return False

    # Combine stations #0010
    @app.callback(
        [Output(component_id='cs_station_1', component_property='value'),
         Output(component_id='cs_station_2', component_property='value'),
         Output(component_id='combine_stations_alert', component_property='displayed'),
         Output(component_id='combine_stations_alert', component_property='message')],
        [Input(component_id='cs_save', component_property='n_clicks'),
         Input(component_id='cs_station_1', component_property='value'),
         Input(component_id='cs_station_2', component_property='value')]
    )
    def combine_stations(n_clicks, station_1, station_2) -> tuple:
        """
        Input: Save button in the current dialog and all text fields in the current dialog
        Output: All text fields in the current dialog

        The passed station names are checked and if they are valid, then the station from the second field is deleted
        and replaced by the station from the first field.
        """

        global count_combine_stations

        if not count_combine_stations < n_clicks:
            raise PreventUpdate

        # Update click count
        count_combine_stations += 1

        # Format user input
        user_input: Dict[str, str] = {
            'station name (1)': station_1,
            'station name (2)': station_2
        }

        # check if the input is valid
        if errors := check(process_data, user_input):
            error_msg = "ERROR: \n" + ''.join(str(i + 1) + ". " + error + "\n" for i, error in enumerate(errors))

            return station_1, station_2, True, error_msg

        # Get station indices
        index_1: int = station_by_name(process_data['station'], station_1)
        index_2: int = station_by_name(process_data['station'], station_2)

        # check if the given stations exist
        if index_1 == -1 or index_2 == -1:
            return station_1, station_2, True, "ERROR\n\nThe given station doesn't exist"

        # delete station_2 from the station list
        del process_data['station'][index_2]

        # replace station_2 in the station of the corresponding order
        indices: List[tuple] = order_by_station(process_data['order'], station_2)
        for index in indices:
            process_data['order'][index[0]]['station'][index[1]] = station_1

        return '', '', False, ''

    # Select station #0011
    @app.callback(
        [Output(component_id='modal_change_station', component_property='is_open'),
         Output(component_id='modal_change_order', component_property='is_open'),
         Output(component_id='station_name_input', component_property='value'),
         Output(component_id='station_capacity_input', component_property='value'),
         Output(component_id='station_storage_input', component_property='value'),
         Output(component_id='station_measurement_input', component_property='value'),
         Output(component_id='station_dd_input', component_property='options'),
         Output(component_id='order_name_input_', component_property='children'),
         Output(component_id='order_stations_input_', component_property='children'),
         Output(component_id='order_priority_input_', component_property='value'),
         Output(component_id='order_storage_input_', component_property='value'),
         Output(component_id='order_source_input_', component_property='value'),
         Output(component_id='order_sink_input_', component_property='value')],
        [Input(component_id='cytoscape', component_property='tapNodeData'),
         Input(component_id='add_attribute_station', component_property='n_clicks'),
         Input(component_id='add_attribute_order', component_property='n_clicks'),
         Input(component_id='add_attribute_save', component_property='n_clicks')]
    )
    def select_node(tapped_node, attr_station, attr_order, attr_save) -> tuple:
        """
        Input: click on a node from the graph
        Output: Text fields in the opening dialog box

        A node is clicked by the user. Based on the node ID, it is first differentiated whether it is a station or a
        store. Accordingly, all required information is collected and the corresponding dialog window is opened with
        this information.
        """

        global curr_dia

        # Differentiate which input was triggered
        ctx = callback_context
        nu = no_update
        if not ctx.triggered:
            button_id = ''
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # If a station attribute is to be added, the current dialog is 'closed' temporarily
        if button_id == 'add_attribute_station':
            curr_dia = ('station', tapped_node['id'])
            return (False,) + (nu, ) * 12

        # If an order attribute is to be added, the current dialog is 'closed' temporarily
        if button_id == 'add_attribute_order':
            curr_dia = ('order', tapped_node['id'])
            return (nu,) + (False,) + (nu, ) * 11

        # If the attribute was saved, then the previously closed window will be opened again
        if button_id == 'add_attribute_save':
            if curr_dia[0] == 'station':
                return (True,) + (nu,) * 12
            elif curr_dia[0] == 'order':
                return (nu, ) + (True,) + (nu, ) * 11

            return (nu, ) * 13

        # Start the app
        if tapped_node is None:
            raise PreventUpdate

        if (index := station_by_name(process_data['station'], tapped_node['id'])) != -1:
            # Case: station

            pd = process_data['station'][index]

            # Get all the data about the selected station to be displayed
            s_name: str = pd['name']
            s_capacity: str = pd['capacity']
            s_storage: str = pd['storage'] if pd['storage'] else ''
            measurement: int = int(pd['measurement'])
            dd_options: list = change_station_dropdown(process_data['order'], tapped_node['id'])

            # Prepare the cache variable
            global cache_order, selected_station
            cache_order = get_cache_order(process_data, s_name)
            selected_station = s_name

            return True, False, s_name, s_capacity, s_storage, measurement, dd_options, '', '', '', '', '', ''

        elif (order_index := order_by_name(process_data['order'], tapped_node['id'])) != -1:
            # Case: final-store

            pd = process_data['order'][order_index]

            o_name: str = pd['name']
            num_station: str = str(len(pd['station']))
            priority: str = str(pd['priority'])
            storage: str = str(pd['storage']) if pd['storage'] else ''
            source: str = pd['source']
            sink: str = pd['sink'] if pd['sink'] else ''

            return False, True, '', '', '', 0, [], o_name, num_station, priority, storage, source, sink

    # Change order #0012
    @app.callback(
        [Output(component_id='change_order_alert', component_property='displayed'),
         Output(component_id='change_order_alert', component_property='message'),
         Output(component_id='saved_change_o', component_property='is_open')],
        [Input(component_id='submit_change_order', component_property='n_clicks'),
         Input(component_id='order_priority_input_', component_property='value'),
         Input(component_id='order_storage_input_', component_property='value'),
         Input(component_id='order_source_input_', component_property='value'),
         Input(component_id='order_sink_input_', component_property='value'),
         Input(component_id='order_name_input_', component_property='children')]
    )
    def change_order(n_clicks, priority, storage, source_name, sink_name, order_name) -> tuple:
        """
        Input: Text-input for the order properties
        Output: Alert- and Success-Windows

        Checks, if the user input is valid. If so, the input is added to process_data
        """

        global count_change_order

        # Starting the ap
        if not count_change_order < n_clicks:
            raise PreventUpdate

        # Update page counter
        count_change_order += 1

        # Check if the input is valid
        user_input: Dict[str, str] = {
            'priority': priority,
            'storage': storage,
            'source name': source_name,
            'sink name': sink_name
        }

        # Check if the user input is valid
        if errors := check(process_data, user_input):
            error_msg = "ERROR: \n" + ''.join(str(i + 1) + ". " + error + "\n" for i, error in enumerate(errors))
            return True, error_msg, False

        # Get the index of the selected order
        index_order: int = order_by_name(process_data['order'], order_name)

        # Get the selected order dict by index
        order = process_data['order'][index_order]

        # Update the order dict
        order['priority'] = int(priority) if priority else 10
        order['storage'] = int(storage) if storage else None
        order['source'] = source_name
        order['sink'] = sink_name if sink_name else None

        return False, '', True

    # Info change order #0013
    @app.callback(
        Output(component_id='change_order_info', component_property='displayed'),
        Input(component_id='info_change_order', component_property='n_clicks')
    )
    def change_order_info(n_clicks) -> bool:
        """
        Input: Click on the 'info' button
        Output: boolean, if the modal is open

        Opens the window 'change order info'
        """

        if not n_clicks:
            return False

        return True

    # Change station #0014
    @app.callback(
        [Output(component_id='change_station_alert', component_property='displayed'),
         Output(component_id='change_station_alert', component_property='message'),
         Output(component_id='saved_change_s', component_property='is_open')],
        [Input(component_id='submit_change_station', component_property='n_clicks'),
         Input(component_id='station_name_input', component_property='value'),
         Input(component_id='station_capacity_input', component_property='value'),
         Input(component_id='station_storage_input', component_property='value'),
         Input(component_id='station_measurement_input', component_property='value')]
    )
    def change_station_main(n_clicks, station_name, capacity, storage, measurement) -> tuple:
        """
        Input: Text-input for the station properties
        Output: Alert- and Success-Windows

        Checks, if the user input is valid. If so, the input is added to process_data. It is already a long callback.
        Therefore, there is another callback 'change_station_sub', in which additional station-properties are set.
        """

        global count_change_station, cache_order

        # Starting the ap
        if not count_change_station < n_clicks:
            raise PreventUpdate

        # Update page counter
        count_change_station += 1

        # Check if the input is valid ()
        user_input: Dict[str, str] = {
            'station name': station_name,
            'capacity': str(capacity),
            'storage': str(storage),
            'measurement': str(measurement)
        }

        # Check the direct input
        station_index: int = station_by_name(process_data['station'], selected_station)
        errors = check(process_data, user_input, station_index=station_index)

        # Check the cached data
        for value in cache_order.values():

            # Check if the function name is valid
            errors += check(process_data, {'function': value['function']})

            # Check if the demand is valid
            if value['last_selected'] == 'd':
                errors += check(process_data, {'demand': str(value['demand'])})

            if value['last_selected'] == 'c':
                comp = value['component']

                # Delete entry's with no content
                comp.pop('', None)
                delete_key = []
                for c, d in comp.items():
                    if d == '':
                        delete_key.append(c)
                for key in delete_key:
                    comp.pop(key, None)

                errors += check(process_data, {'demand': str(i) for i in comp.values()})

        # Check if the user input is valid
        if errors:
            error_msg = "ERROR: \n" + ''.join(str(i + 1) + ". " + error + "\n" for i, error in enumerate(errors))
            return True, error_msg, False,

        # Get the selected station dict by index
        station = process_data['station'][station_index]

        # Update the station dict
        station['name'] = station_name
        station['capacity'] = int(capacity) if capacity else 1
        station['storage'] = int(storage) if storage else None
        station['measurement'] = True if measurement == '1' else False

        # Update the station attribute of all involved orders
        orders = process_data['order']
        order_station: List[tuple] = order_by_station(orders, selected_station)
        for o_index, s_index in order_station:
            orders[o_index]['station'][s_index] = station_name

        # Update cached data
        for order, data in cache_order.items():

            # Get the index of the selected station and the current order
            order_index, station_index = order_and_station(process_data['order'], order, selected_station)

            # Update function
            process_data['order'][order_index]['function'][station_index] = data['function']

            # Update demand and component
            # Case: a machining is performed on the selected station in the current order
            if data['last_selected'] == 'd':
                process_data['order'][order_index]['demand'][station_index] = int(data['demand'])
                process_data['order'][order_index]['component'][station_index] = []

            # Case: an assembly is performed on the selected station in the current order
            elif data['last_selected'] == 'c':
                process_data['order'][order_index]['demand'][station_index] = [
                    int(i) for i in data['component'].values()
                ]
                process_data['order'][order_index]['component'][station_index] = [
                    i for i in data['component'].keys()
                ]

        # clear caches
        cache_order = {}

        return False, '', True

    @app.callback(
        [Output(component_id='station_dd_input', component_property='value'),
         Output(component_id='station_function_input', component_property='value'),
         Output(component_id='station_demand_div', component_property='style'),
         Output(component_id='station_demand_input', component_property='value'),
         Output(component_id='station_component_div', component_property='style'),
         Output(component_id='station_cd_input', component_property='dropdown'),
         Output(component_id='station_cd_input', component_property='data'),
         Output(component_id='station_radio_input', component_property='value')],
        [Input(component_id='cytoscape', component_property='tapNodeData'),
         Input(component_id='station_dd_input', component_property='value'),
         Input(component_id='station_radio_input', component_property='value'),
         Input(component_id='station_demand_input', component_property='value'),
         Input(component_id='station_cd_input', component_property='data'),
         Input(component_id='add_row_order', component_property='n_clicks'),
         Input(component_id='station_function_input', component_property='value')],
        [State(component_id='station_demand_div', component_property='style'),
         State(component_id='station_component_div', component_property='style'),
         State(component_id='station_cd_input', component_property='dropdown'),
         State(component_id='station_demand_input', component_property='value')]
    )
    def change_station_sub(tapped_node, selected_order, radio_btn, demand, data, n_click, function_, style_demand,
                           style_comp, dd_opt, curr_demand) -> tuple:
        """
        Input: Tapped node, input-boxes for the station properties to be set
        Output: Input-boxes for the station properties to be set (reset them after valid input)

        Caches the user input and assigns it to 'process_data' after saving.
        """

        nu = no_update
        style_show = {'margin-top': '7px'}
        style_hide = {'margin-top': '7px', 'display': 'none'}

        # Differentiate which input was triggered
        ctx = callback_context
        if not ctx.triggered:
            button_id = ''
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # When the user selects a node from the Graph, the sub dialog boxes should all be set to their default value.
        if button_id == 'cytoscape':
            return None, '', style_show, '', style_hide, {}, [], 'machining'

        # When the user selects an order in the dropdown option, the following fields should be filled with the current
        # content belonging to this order
        if button_id == 'station_dd_input':

            # The user goes back to the default selection himself
            if selected_order is None:
                return None, '', style_demand, '', style_comp, {}, [], radio_btn

            cache = cache_order[selected_order]
            function = cache['function']
            demand = cache['demand']
            dropdown_opt = create_table_dropdown(process_data['order'], selected_order)
            data = [{'component': component, 'demand': demand} for component, demand in cache['component'].items()]

            return selected_order, function, style_demand, demand, style_comp, dropdown_opt, data, radio_btn

        # The user switches from machining to assembly or vice versa
        if button_id == 'station_radio_input':

            if radio_btn == 'machining':
                demand = ''
                so = None
                if selected_order is not None:
                    demand = cache_order[selected_order]['demand']
                    so = selected_order
                return so, function_, style_show, demand, style_hide, {}, [], radio_btn

            else:
                dropdown_opt = {}
                data = []
                so = None
                if selected_order is not None:
                    dropdown_opt = create_table_dropdown(process_data['order'], selected_order)
                    data = [{'component': component, 'demand': demand}
                            for component, demand in cache_order[selected_order]['component'].items()]
                    so = selected_order
                return so, function_, style_hide, '', style_show, dropdown_opt, data, radio_btn

        # Demand
        if button_id == 'station_demand_input':

            # No order is selected
            if selected_order is None:
                return None, function_, style_demand, curr_demand, style_comp, {}, [], radio_btn

            cache = cache_order[selected_order]
            cache['last_selected'] = 'd'
            cache['demand'] = demand

            raise PreventUpdate

        # Component
        if button_id == 'station_cd_input':

            # No order is selected
            if selected_order is None:
                return None, '', style_demand, '', style_comp, {}, [], radio_btn

            cache_order[selected_order]['last_selected'] = 'c'
            new_component = {}
            for entry in data:
                new_component[entry['component']] = entry['demand']
            cache_order[selected_order]['component'] = new_component
            raise PreventUpdate

        # Add row
        if button_id == 'add_row_order':

            if selected_order is None:
                raise PreventUpdate

            # Add an empty row to the table
            new_data = data + [{'component': '', 'demand': ''}]
            return selected_order, function_, style_demand, '', style_comp, dd_opt, new_data, radio_btn

        # Function
        if button_id == 'station_function_input':

            if selected_order is None:
                raise PreventUpdate

            cache_order[selected_order]['function'] = function_
            return selected_order, function_, style_demand, curr_demand, style_comp, dd_opt, data, radio_btn

        return nu, '', nu, '', nu, {}, [], nu

    # Add attribute #0015
    @app.callback(
        [Output(component_id='modal_add_attribute', component_property='is_open'),
         Output(component_id='add_attr_param_one', component_property='children'),
         Output(component_id='add_attr_param_two', component_property='children'),
         Output(component_id='param_one_div', component_property='style'),
         Output(component_id='param_two_div', component_property='style'),
         Output(component_id='add_attribute_alert', component_property='displayed'),
         Output(component_id='add_attribute_alert', component_property='message'),
         Output(component_id='station_attribute_input', component_property='data'),
         Output(component_id='order_attribute_input', component_property='data'),
         Output(component_id='factory_attribute_input', component_property='data'),
         Output(component_id='add_attr_param_one_input', component_property='value'),
         Output(component_id='add_attr_param_two_input', component_property='value'),
         Output(component_id='attribute_name_input', component_property='value'),
         Output(component_id='attr_dist_input', component_property='value')],
        [Input(component_id='add_attribute_station', component_property='n_clicks'),
         Input(component_id='add_attribute_order', component_property='n_clicks'),
         Input(component_id='add_attribute_factory', component_property='n_clicks'),
         Input(component_id='add_attribute_save', component_property='n_clicks'),
         Input(component_id='attr_dist_input', component_property='value'),
         Input(component_id='station_attribute_input', component_property='data'),
         Input(component_id='order_attribute_input', component_property='data'),
         Input(component_id='factory_attribute_input', component_property='data'),
         Input(component_id='cytoscape', component_property='tapNodeData')],
        [State(component_id='add_attr_param_one_input', component_property='value'),
         State(component_id='add_attr_param_two_input', component_property='value'),
         State(component_id='attribute_name_input', component_property='value')]
    )
    def add_attribute(add_station, add_order, add_factory, add_save, dist, station_data, order_data, factory_data,
                      tapped_node, param1, param2, attr_name) -> tuple:
        """
        Input: add-attribute-buttons, attribute-tables, user-input
        Output: Alert-windows, attribute-tables, user-input (reset them after input)

        Opens the 'add-attribute' dialog. Checks if the user input is valid and assigns it to the process_data, as well
        as to the attribute tables, of the corresponding simulation object (station, order, factory).
        """

        # Global reference
        global curr_dia

        # Lazy return
        nu = no_update

        # Style variables
        style_hide = {
            'margin-top': '7px',
            'display': 'none'
        }
        txt_1: str = ''
        txt_2: str = ''
        style_1: Dict[str, str] = style_hide
        style_2: Dict[str, str] = style_hide

        # Differentiate which input was triggered
        ctx = callback_context
        if not ctx.triggered:
            button_id = ''
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Fill attribute table with default values, when opening new dialog
        if button_id == 'cytoscape':

            if (index := station_by_name(process_data['station'], tapped_node['id'])) != -1:
                attr_table = get_attributes(process_data['station'][index], 'station')
                return False, '', '', style_hide, style_hide, False, '', attr_table, nu, nu, nu, nu, nu, nu

            elif (order_index := order_by_name(process_data['order'], tapped_node['id'])) != -1:
                attr_table = get_attributes(process_data['order'][index], 'order')
                return False, '', '', style_hide, style_hide, False, '', nu, attr_table, nu, nu, nu, nu, nu

        # Fill attribute table with default values, when opening new dialog
        if button_id == 'add_attribute_factory':
            attr_table = get_attributes(process_data['factory'], 'factory')
            return True, txt_1, txt_2, style_hide, style_hide, False, '', nu, nu, attr_table, '', '', '', ''

        # Select distribution
        if button_id == 'attr_dist_input':
            txt_1, txt_2, style_1, style_2 = select_distribution(dist)
            return nu, txt_1, txt_2, style_1, style_2, False, '', nu, nu, nu, nu, nu, nu, nu
        elif dist:
            txt_1, txt_2, style_1, style_2 = select_distribution(dist)

        # Open dialog
        if button_id in ['add_attribute_station', 'add_attribute_order']:

            return True, txt_1, txt_2, style_1, style_2, False, '', nu, nu, nu, '', '', '', ''

        # Save the attribute and close the modal
        if button_id == 'add_attribute_save':

            # Open error-dialog, if the input is not valid
            if errors := (check_dist_param(dist, param1, param2) +
                          check(process_data, {'attr. name': attr_name, 'distribution': dist})):
                error_msg = "ERROR: \n" + ''.join(str(i + 1) + ". " + error + "\n" for i, error in enumerate(errors))

                return False, txt_1, txt_2, style_1, style_2, True, error_msg, nu, nu, nu, nu, nu, nu, nu

            # Find index of element, the attribute is to be added
            insert_index: int = find_element_index(process_data, curr_dia)

            # Add the attribute to the corresponding simulation object (override if already defined)
            dist_list: list = create_dist_list(dist, param1, param2)
            new_data = [{'name': attr_name, 'distribution.': dist, 'parameter': str(dist_list)}]
            if insert_index == -1:
                process_data['factory'][attr_name] = dist_list
                return_data = factory_data + new_data
                return False, '', '', style_hide, style_hide, False, '', nu, nu, return_data, nu, nu, nu, nu
            elif curr_dia[0] == 'station':
                process_data['station'][insert_index][attr_name] = dist_list
                return_data = station_data + new_data
                return False, '', '', style_hide, style_hide, False, '', return_data, nu, nu, nu, nu, nu, nu
            elif curr_dia[0] == 'order':
                process_data['order'][insert_index][attr_name] = dist_list
                return_data = order_data + new_data
                return False, '', '', style_hide, style_hide, False, '', nu, return_data, nu, nu, nu, nu, nu

            # return -> just causing a side effect
        return False, txt_1, txt_2, style_1, style_2, False, '', nu, nu, nu, nu, nu, nu, nu

    # Info add attribute #0016
    @app.callback(
        Output(component_id='cfd_add_attribute_info', component_property='displayed'),
        Input(component_id='add_attribute_info', component_property='n_clicks')
    )
    def add_attribute_info(n_clicks) -> bool:
        """
        Input: Click on the 'info' button
        Output: boolean, if the modal is open

        Opens the window 'add attribute info'
        """

        if not n_clicks:
            return False

        return True

    # Edit factory #0017
    @app.callback(
        [Output(component_id='mdl_edit_factory', component_property='is_open'),
         Output(component_id='global_function_input', component_property='data'),
         Output(component_id='function_name_input', component_property='value'),
         Output(component_id='global_function_alert', component_property='displayed'),
         Output(component_id='global_function_alert', component_property='message')],
        [Input(component_id='edit-factory', component_property='n_clicks'),
         Input(component_id='add_attribute_factory', component_property='n_clicks'),
         Input(component_id='add_attribute_save', component_property='n_clicks'),
         Input(component_id='submit_edit_factory', component_property='n_clicks'),
         Input(component_id='add_global_attribute', component_property='n_clicks'),
         Input(component_id='global_function_input', component_property='data')],
        [State(component_id='function_name_input', component_property='value')]
    )
    def open_edit_factory_dialog(edit_factory, add_attr, save_attr, save_edit, add_func, curr_func, func_name) -> tuple:
        """
        Input: edit-factory and add attribute buttons, global functions input
        Output: Alert-windows, global-function-table

        """

        nu = no_update

        global curr_dia

        # Differentiate which input was triggered
        ctx = callback_context
        if not ctx.triggered:
            button_id = ''
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Open Dialog
        if button_id == 'edit-factory':

            return True, nu, nu, False, ''

        # Add attribute
        if button_id == 'add_attribute_factory':
            curr_dia = ('factory', '')
            return False, nu, nu, False, ''

        # Safe Attribute in the attribute-dialog -> open the edit factory dialog again
        if button_id == 'add_attribute_save':
            if curr_dia[0] == 'factory':
                return True, nu, nu, False, ''

        # close the dialog, when saving the changes
        if button_id == 'submit_edit_factory':
            return False, nu, nu, False, ''

        # Add a new global function
        if button_id == 'add_global_attribute':

            # Open error-dialog, if the input is not valid
            if errors := check(process_data, {'global function': func_name}):
                error_msg = "ERROR: \n" + ''.join(str(i + 1) + ". " + error + "\n" for i, error in enumerate(errors))

                return True, nu, nu, True, error_msg

            # Add the function name to the local process data
            process_data['factory']['function'] += [func_name]

            # Add the function name to the table
            new_func = curr_func + [{'name': func_name}]

            return True, new_func, '', False, ''

        # Loading the application
        return False, nu, nu, nu, nu

    # Info edit factory #0018
    @app.callback(
        Output(component_id='cfd_edit_factory_info', component_property='displayed'),
        Input(component_id='info_edit_factory', component_property='n_clicks')
    )
    def info_edit_factory(n_clicks) -> bool:
        """
        Input: Click on the 'info' button
        Output: boolean, if the modal is open

        Opens the window 'edit factory info'
        """

        if n_clicks:
            return True

        return False
