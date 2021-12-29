"""This file contains all popup and alert windows used to provide helpful information.
"""

# Since the file can become very large during development, a TOC with unique labels is given
#
# Alr_invalid_path          #0001
# Alr_created_files         #0002
# Cfd_add_order             #0003
# Cfd_files_alert           #0004
# Cfd_files_info            #0005
# Cfd_order_info            #0006
# Cfd_combine_stations      #0007
# Cfd_combine_s_alert       #0008
# Cfd_change_o_alert        #0009
# Cfd_change_o_info         #0010
# Alr_saved_change_o        #0011
# Cfd_change_s_alert        #0012
# Alr_saved_change_o        #0013
# Cfd_attribute_alert       #0014
# Cfd_attribute_info        #0015
# Cfd_edit_factory_info     #0016
# Cfd_global_function_alert #0017

import dash_bootstrap_components as dbc
from dash import dcc

# Alr_invalid_path #0001
alr_invalid_path = dbc.Alert(
    "The given path is not valid, try again!",
    color="danger",
    id='invalid_path',
    is_open=False,
    dismissable=True
)

# Alr_created_files #0002
alr_created_files = dbc.Alert(
    "A json an a py file were created!",
    color="success",
    id='created_files',
    is_open=False,
    dismissable=True
)

# Cfd_add_order #0003
cfd_add_order = dcc.ConfirmDialog(
    id='add_order_alert',
    displayed=False,
    message='Error'
)

# Cfd_files_alert #0004
cfd_files_alert = dcc.ConfirmDialog(
    id='create_files_alert',
    displayed=False,
    message='Error'
)

# Cfd_files_info #0005
cfd_files_info = dcc.ConfirmDialog(
    id='create_files_info',
    displayed=False,
    message="The project name must be a string without a space. The files are then saved under the names:"
            "\n\nproject_name_process.json\nproject_name_function.py\n\n The path can be specified relative or "
            "absolute."
)

# Cfd_order_info #0006
cfd_order_info = dcc.ConfirmDialog(
    id='add_order_info',
    displayed=False,
    message="Create new orders:\n\nThe boxes 'Order name' and 'Source name' are required, all other boxes are optional."
            "\nThe boxes 'Order name', 'Source name', 'Sink name' get strings which are not allowed to contain a space."
            " The other boxes take positive integers ('Number stations' can be zero).\n\nDefault values:\nNumber "
            "stations: 0\nStorage: infinite\nPriority: 10"
)

# Cfd_combine_stations #0007
cfd_combine_stations = dcc.ConfirmDialog(
    id='combine_stations_info',
    displayed=False,
    message="Combine two stations:\n\nIf a station is to be used by two or more orders at the same time, then the "
            "stations can be combined in pairs in this dialog.\n\nThe names of the stations to be combined must be "
            "entered in the text fields. The station in the second text field is deleted and set to the station of the "
            "first text field."
)

# Cfd_cs_alert #0008
cfd_cs_alert = dcc.ConfirmDialog(
    id='combine_stations_alert',
    displayed=False,
    message='Error'
)

# Cfd_change_o_alert #0009
cfd_change_o_alert = dcc.ConfirmDialog(
    id='change_order_alert',
    displayed=False,
    message='Error'
)

# Cfd_change_o_info #0010
cfd_change_order_info = dcc.ConfirmDialog(
    id='change_order_info',
    displayed=False,
    message="Here the properties of an order can be adjusted again. However, the name and the number of stations cannot"
            " be changed afterwards."
)

# Alr_saved_change_o #0011
alr_saved_change_o = dbc.Alert(
    "The changes to the order have been saved!",
    color="success",
    id='saved_change_o',
    is_open=False,
    dismissable=True
)

# Cfd_change_s_alert #0012
cfd_change_s_alert = dcc.ConfirmDialog(
    id='change_station_alert',
    displayed=False,
    message='Error'
)

# Alr_saved_change_o #0013
alr_saved_change_s = dbc.Alert(
    "The changes to the station have been saved!",
    color="success",
    id='saved_change_s',
    is_open=False,
    dismissable=True
)

# Cfd_attribute_alert #0014
cfd_attribute_alert = dcc.ConfirmDialog(
    id='add_attribute_alert',
    displayed=False,
    message='Error'
)

# Cfd_attribute_info #0015
cfd_attribute_info = dcc.ConfirmDialog(
    id='cfd_add_attribute_info',
    displayed=False,
    message="Depending on the context from which this window was accessed, an attribute is added to a station, an order"
            " or a factory. \n\nA distribution must be selected (user-defined distributions must be defined manually in"
            " the JSON file). The name of the attribute must be a unique string without spaces. The attribute values of"
            " the distribution must be within the usual intervals as known from mathematics. "
)

# Cfd_edit_factory_info #0016
cfd_edit_factory_info = dcc.ConfirmDialog(
    id='cfd_edit_factory_info',
    displayed=False,
    message="By clicking on the corresponding 'add' buttons, functions and attributes can be added. The attributes can "
            "only be removed in the actual JSON/py output file."
)

# Cfd_global_function_alert #0017
cfd_global_function_alert = dcc.ConfirmDialog(
    id='global_function_alert',
    displayed=False,
    message='Error'
)
