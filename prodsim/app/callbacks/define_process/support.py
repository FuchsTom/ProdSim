"""
This module bundles some functionality that is needed by multiple callbacks or is too large to integrate logically into
a callback function.
"""

# Searchable TOC of support-functions:
#
# root_nodes              #0001
# check                   #0002
# txt_python_func         #0003
# station_by_name         #0004
# order_by_station        #0005
# change_station_dropdown #0006
# order_by_name           #0007
# get_cache_order         #0008
# order_and_station       #0009
# create_table_dropdown   #0010
# select_distribution     #0011
# check_dist_param        #0012
# find_element_index      #0013
# create_dist_list        #0014
# get_attributes          #0015
# clear_process_data      #0016

from typing import List, Dict, Tuple

# root_nodes #0001
def root_nodes(order_list: List[dict]) -> str:
    """Defining the root nodes to arrange the nodes based on them in a tree structure

    Root nodes are all station-nodes that have no predecessor and are not an assembly station

    """

    # Get all orders, which have at least one station
    order_with_process: List[dict] = list(order for order in order_list if len(order['station']) > 0)

    # List of all jobs whose first station is a root node
    first_station_name: List[str] = []

    # Filtering of all stations names that are in the first position in the process and do not perform assembly
    for order_data in order_with_process:
        if isinstance(order_data['demand'][0], list):
            continue
        first_station_name.append(order_data['station'][0])
    first_station_name = list(set(first_station_name))

    # Remove all station names whose stations are not in the first place with respect to another process.
    for order_data in order_list:
        for station in order_data['station'][1:]:
            if station in first_station_name:
                if station == order_data['station'][0]:
                    # Only exception: in the process where the station is again appearance is also the process where
                    # the station is in the first place
                    continue
                first_station_name.remove(station)

    # According to the library dash_cytoscape the following syntax must be used regarding the root nodes
    # '#root_name_1, #root_name_2, ... #root_name_n'
    roots: str = ''
    for station_name in first_station_name:
        roots += '#' + station_name + ', '

    return roots.strip(', ')


# check #0002
def check(process_data: dict, user_input: Dict[str, str], order_index: int = None,
          station_index: int = None) -> List[str]:
    """ In this method all checks are defined, which are executed on the values entered by the user. The key is an
    internal identifier to differentiate the cases and output user-defined error messages. The value is the user's
    entry.

    Used keys:
    1.  'order name' -> Name of an order
    2.  'source name' -> Name of a source
    3.  'sink name' -> Name of a sink
    4.  'number stations' -> Number of stations
    5.  'storage' -> Storage of an order
    6.  'priority' -> Priority of an order
    7.  'station name - (1/2)' -> Name of a station (context: combine stations -> no checks if name is taken)
    8.  'station name' -> Name of a station
    9.  'capacity' -> Capacity of a station
    10. 'measurement' -> If a station is a measurement station
    11. 'function' -> Any kind of function
    12. 'demand' -> Demand
    13. 'attr. name' -> Name of station, order and factory attributes
    14. 'distribution' -> Distribution name of an attribute
    """

    error_list: List[str] = []

    for key, value in user_input.items():

        if key == 'order name':

            # Was a name set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Name with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

            # Name taken
            for index, order in enumerate(process_data['order']):
                if order_index is not None and index == order_index:
                    continue
                if value == order['name']:
                    error_list.append(f"The {key} is already taken")

        elif key == 'source name':

            # Was a name set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Name with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

        elif key == 'sink name':

            # The sink is an optional parameter
            if value is None or value == '':
                continue

            # Name with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

        elif key == 'number stations':

            # The number of stations is an optional parameter
            if value is None or value == '':
                continue

            if not value.isdigit():
                error_list.append(f"{key} is not a positive (>=0) integer")

        elif key == 'storage':

            # The storage of an order is an optional parameter
            if value is None or value == '':
                continue

            if not value.isdigit():
                error_list.append(f"{key} is not a positive integer")
                continue

            if value == '0':
                error_list.append(f"{key} must be greater than zero")

        elif key == 'priority':

            # The storage of an order is an optional parameter
            if value is None or value == '':
                continue

            if not value.isdigit():
                error_list.append(f"{key} is not a positive integer")

        elif key == 'path':

            # Was a path set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Path with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

        elif key == 'project name':

            # Was a project set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Project name with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

        elif key == 'station name (1)' or key == 'station name (2)':

            # Was a name set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Name with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

        elif key == 'station name':

            # Was a name set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Name with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

            # Name taken
            for index, station in enumerate(process_data['station']):
                if station_index is not None and index == station_index:
                    continue
                if value == station['name']:
                    error_list.append(f"The {key} is already taken")

        elif key == 'capacity':

            # The storage of an order is an optional parameter
            if value is None or value == '':
                continue

            if not value.isdigit():
                error_list.append(f"{key} is not a positive integer")
                continue

            if value == '0':
                error_list.append(f"{key} must be greater than zero")

        elif key == 'measurement':

            if value not in ['0', '1']:
                error_list.append(f"No {key} state is selected")

        elif key == 'function':

            # Was a function set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Function with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

        elif key == 'demand':

            # The demand is not an optional parameter
            if value is None or value == '':
                error_list.append(f"A {key} value is missing")
                continue

            if not value.isdigit():
                error_list.append(f"A {key} is not a positive integer")
                continue

            if value == '0':
                error_list.append(f"A {key} is not greater than zero")

        elif key == 'attr. name':

            # Was a name set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Name with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

        elif key == 'global function':

            # Was a function set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

            # Function with space
            if ' ' in value:
                error_list.append(f"The {key} contains a space")

            if value in process_data['factory']['function']:
                error_list.append(f"The function {key} is already defined")

        elif key == 'distribution':

            # Was a distribution set
            if value is None or value == '':
                error_list.append(f"No {key} was set")
                continue

    return error_list


# txt_python_func  #0003
def txt_python_func(func_list: List[str], func_type: str) -> str:
    """This method creates strings from which the python file in which the simulation functions are defined is created.

    func_list contains the names of all process functions for which a string representation should be generated.
    func_type contains the type of function to be created, possible cases are:
    'p' -> process functions
    's' -> sources and sinks
    'g' -> global functions
    """

    # Make a list of unique elements
    func_list = list(set(func_list))

    # Create functions signature based on the function type
    signature: str = ''
    if func_type == 'p':
        signature = 'env, item, machine, factory'
    elif func_type == 's':
        signature = 'env, factory'
    elif func_type == 'g':
        signature = 'env, factory'

    txt_func: str = ''
    for func in func_list:
        txt_func += 'def ' + func + '(' + signature + '):\n\n\tpass\n\n'

    return txt_func


# station_by_name #0004
def station_by_name(station_list: List[dict], station_name: str) -> int:
    """Returns the current index of a station. The starting point is the name of the station. If no station with this
    name exists, -1 is returned.
    """

    for index, station in enumerate(station_list):
        if station['name'] == station_name:
            return index

    return -1


# order_by_station #0005
def order_by_station(order_list: List[Dict], station_name) -> List[tuple]:
    """Returns a list of tuples. The first element of each tuple contains the index of an order that contains the
    station 'station_name'. The second element is the respective index in the station list of the order. Since a station
    can be used by several orders, these tuples are stored in a list.
    """

    indices: List[tuple] = []

    for index, order in enumerate(order_list):
        if station_name in order['station']:
            indices.append((index, order['station'].index(station_name)))

    return indices


# change_station_dropdown #0006
def change_station_dropdown(order_list: List[dict], station_name: str) -> List[dict]:
    """
    This function creates the dropdown options for the 'change station' window. It passes the list of orders and a name
    of a station. Now a structured output is generated, in which all orders are contained, in which this station occurs.
    The output has the following structure:

    [{'label': 'order_name', 'value': 'order_name'}]
    """

    dropdown_opt: List[dict] = []

    for order in order_list:
        if station_name in order['station']:
            order_name: str = order['name']
            dropdown_opt.append({'label': order_name, 'value': order_name})

    return dropdown_opt


# order_by_name #0007
def order_by_name(order_list: List[dict], order_name: str) -> int:
    """This method returns the current index of an order by its name. If the order does not exist, -1 is returned.

    """

    for index, order in enumerate(order_list):
        if order['name'] == order_name:
            return index

    return -1


# get_cache_order #0008
def get_cache_order(process_data, station_name):
    """This method creates a dict intended for caching user input during user interaction. An entry is created for each
    order in which the passed station occurs. This entry stores the function called in this order, as well as all
    components to be assembled. The structure is as follows:

    cache_order = {
        'order_1': {
            'function': 'function_1',
            'component': {
                'component_1': demand_1,
                'component_2': demand_2
            },
            'demand': demand
            'last_selected': 'd'/'c'
        },
        '...'
    }

    """

    cache_dict: dict = {}
    orders: List[dict] = process_data['order']

    # Get a list of tuples with indices, in which order and on which place the station occurs
    order_station = order_by_station(orders, station_name)

    for o_index, s_index in order_station:

        order: dict = orders[o_index]
        order_name: str = order['name']

        cache_dict[order_name] = {
            'function': order['function'][s_index]
        }

        if isinstance(demand := order['demand'][s_index], int):
            cache_dict[order_name]['demand'] = demand
            cache_dict[order_name]['component'] = {}
            cache_dict[order_name]['last_selected'] = 'd'
        else:
            cache_dict[order_name]['component'] = {
                order['component'][s_index][i]: demand[i] for i in range(len(demand))}
            cache_dict[order_name]['demand'] = 0
            cache_dict[order_name]['last_selected'] = 'c'

    return cache_dict


# order_and_station #0009
def order_and_station(order_list: List[dict], order_name: str, station_name: str) -> tuple:
    """ Return an index-tuple containing the index of an order, and the index of a specific station used in it.

    If the order does not exist, or the order does not contain the specific station (-1,-1) ist returned
    """

    for order_index, order in enumerate(order_list):
        if order['name'] == order_name:
            for station_index, station in enumerate(order['station']):
                if station == station_name:
                    return order_index, station_index

    return -1, -1


# create_table_dropdown #0010
def create_table_dropdown(order_list: List[dict], order_name: str) -> dict:
    """ Create the dropdown-options in the context of assembling orders.

    Syntax of the returned dictionary is based on dash.
    """

    dropdown_options = {
        'component': {
            'options': []
        }
    }

    for order in order_list:
        if (name := order['name']) != order_name:
            dropdown_options['component']['options'].append(
                {
                    'label': name,
                    'value': name
                }
            )

    return dropdown_options


# select_distribution #0011
def select_distribution(dist: str) -> tuple:
    """ Return a 4-tuple containing names and style information based on a chosen distribution.

    """

    name_one: str = ''
    name_two: str = ''
    style_one: dict = {
        'margin-top': '7px'
    }
    style_two: dict = {
        'margin-top': '7px'
    }

    if dist == 'fix':

        name_one = 'value'
        style_two['display'] = 'none'

    elif dist == 'binary':

        name_one = 'probability'
        style_two['display'] = 'none'

    elif dist == 'binomial':

        name_one = 'number trials'
        name_two = 'probability'

    elif dist == 'normal':

        name_one = 'mean'
        name_two = 'standard dev.'

    elif dist == 'uniform':

        name_one = 'lower bound'
        name_two = 'upper bound'

    elif dist == 'poisson':

        name_one = 'rate'
        style_two['display'] = 'none'

    elif dist == 'exponential':

        name_one = 'scale'
        style_two['display'] = 'none'

    elif dist == 'lognormal':

        name_one = 'mean'
        name_two = 'standard dev.'

    elif dist == 'chisquare':

        name_one = 'deg. of freedom'
        style_two['display'] = 'none'

    elif dist == 'standard-t':

        name_one = 'deg. of freedom'
        style_two['display'] = 'none'

    return name_one, name_two, style_one, style_two


# check_dist_param #0012
def check_dist_param(dist: str, param_1: str, param_2: str) -> List[str]:
    error_list: List[str] = []
    """ Check if the user-input is valid for a chosen distribution.
    
    Return a list with error-messages. 
    """

    def check_param_int(param: str, param_name: str) -> bool:

        if param is None or param == '':
            error_list.append(f"{param_name} is not set")
            return True

        if not param.isdigit():
            error_list.append(f"{param_name} is not an integer")
            return True

        return False

    def check_param_float(param: str, param_name: str) -> bool:

        if param is None or param == '':
            error_list.append(f"{param_name} is not set")
            return True

        try:
            _ = float(param)
        except ValueError:
            error_list.append(f"{param_name} is not a float")
            return True

        return False

    if dist == 'fix':

        if check_param_float(param_1, 'Value'):
            return error_list

    elif dist == 'binary':

        if check_param_float(param_1, 'Success probability'):
            return error_list

        if float(param_1) > 1 or float(param_1) < 0:
            error_list.append("Success probability is not between 0.0 and 1.0")

    elif dist == 'binomial':

        if check_param_int(param_1, 'Number Trails'):
            return error_list

        if int(param_1) <= 0:
            error_list.append("Number trails is not a positive integer")

        if check_param_float(param_2, 'Probability'):
            return error_list

        if float(param_2) > 1 or float(param_2) < 0:
            error_list.append("Probability is not between 0.0 and ")

    elif dist == 'normal':

        if check_param_float(param_1, 'Mean'):
            return error_list

        if check_param_float(param_2, 'Standard dev.'):
            return error_list

        if float(param_2) < 0:
            error_list.append("Standard dev. is not greater/equal then 0.0")

    elif dist == 'uniform':

        if check_param_float(param_1, 'Lower bound'):
            return error_list

        if check_param_float(param_2, 'Upper bound'):
            return error_list

        if float(param_2) < float(param_1):
            error_list.append("Lower bound is greater then upper bound")

    elif dist == 'poisson':

        if check_param_float(param_1, 'Rate'):
            return error_list

        if float(param_1) <= 0:
            error_list.append("Rate is not greater then zero")

    elif dist == 'exponential':

        if check_param_float(param_1, 'Scale'):
            return error_list

        if float(param_1) <= 0:
            error_list.append("Scale is less/equal then zero")

    elif dist == 'lognormal':

        if check_param_float(param_1, 'Mean'):
            return error_list

        if check_param_float(param_2, 'Standard dev.'):
            return error_list

        if float(param_2) <= 0:
            error_list.append("Standard dev. is less then or equal to zero")

    elif dist == 'chisquare':

        if check_param_float(param_1, 'Deg. of freedom'):
            return error_list

        if float(param_1) <= 0:
            error_list.append("Deg. of freedom is less/equal then zero")

    elif dist == 'standard-t':

        if check_param_float(param_1, 'Deg. of freedom'):
            return error_list

        if float(param_1) <= 0:
            error_list.append("Deg. of freedom is less/equal then zero")

    return error_list


# find_element_index #0013
def find_element_index(process_data: dict, curr_dia: Tuple[str, str]) -> int:
    """ Find the index of a specific station or order within the process data.

    note: this function is used in a context, where already has been checked, if the searched object exists.
    """

    if curr_dia[0] == 'factory':
        return -1

    rel_dict: dict = process_data[curr_dia[0]]

    for index, entry in enumerate(rel_dict):
        if entry['name'] == curr_dia[1]:
            return index


# create_dist_list #0014
def create_dist_list(dist: str, param1: str, param2: str) -> list:
    """ Creates a list with a special syntax describing a distribution

    Syntax: [identifier, param1, param2 (if necessary)]
    """

    dist_list: list = []

    if dist == 'fix':

        dist_list = ["f", float(param1)]

    elif dist == 'binary':

        dist_list = ["b", float(param1)]

    elif dist == 'binomial':

        dist_list = ["i", float(param1), float(param2)]

    elif dist == 'normal':

        dist_list = ["n", float(param1), float(param2)]

    elif dist == 'uniform':

        dist_list = ["u", float(param1), float(param2)]

    elif dist == 'poisson':

        dist_list = ["p", float(param1)]

    elif dist == 'exponential':

        dist_list = ["e", float(param1)]

    elif dist == 'lognormal':

        dist_list = ["l", float(param1), float(param2)]

    elif dist == 'chisquare':

        dist_list = ["c", float(param1)]

    elif dist == 'standard-t':

        dist_list = ["t", float(param1)]

    return dist_list


# get_attributes #0015
def get_attributes(data: dict, case: str) -> List[Dict[str, str]]:
    """ Get all user defined attributes of an order, station or the factory.

    cases: 'station', 'order', 'factory'
    """

    res = []

    pre_defined_station = ['name', 'capacity', 'storage', 'measurement']
    pre_defined_order = ['name', 'priority', 'storage', 'source', 'sink', 'station', 'function', 'demand', 'component']
    pre_defined_factory = ['function']

    if case == 'station':
        compare = pre_defined_station
    elif case == 'order':
        compare = pre_defined_order
    else:
        compare = pre_defined_factory

    dist_ident = {'f': 'fix', 'b': 'binary', 'i': 'binomial', 'n': 'normal', 'u': 'uniform', 'p': 'poisson',
                  'e': 'exponential', 'l': 'lognormal', 'c': 'chisquare', 't': 'standard-t'}

    for key, value in data.items():

        if key not in compare:
            res += [{'name': key, 'distribution.': dist_ident[value[0]], 'parameter': str(value)}]

    return res

# clear_process_data #0016
def clear_process_data(process_data) -> dict:
    """ Create a copy of the process data where all keys with a 'None'-value are removed.

    """

    pd = {
        'order': [],
        'station': [],
        'factory': process_data['factory']
    }

    for order in process_data['order']:
        pd['order'].append({k: v for k, v in order.items() if v is not None})

    for station in process_data['station']:
        pd['station'].append({k: v for k, v in station.items() if v is not None})

    return pd
