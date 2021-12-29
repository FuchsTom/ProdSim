""" This file contains all dialog windows where the user can enter data. These are of type dash bootstrap components
(dbc) Modal.
"""

# Since the file can become very large during development, a TOC with unique labels is given
#
# Mdl_change_order     #0001
# Mdl_change_station   #0002
# Mdl_create_files     #0003
# Mdl_add_order        #0004
# Mdl_combine_stations #0005
# Mdl_add_attribute    #0006
# Mdl_edit_factory     #0007


import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

# Change Order #0001
mdl_change_order = dbc.Modal(
    id="modal_change_order",
    centered=True,
    is_open=False,
    children=[
        dbc.ModalHeader(
            dbc.ModalTitle("Change order")
        ),
        dbc.ModalBody(
            children=[
                # Order name
                html.Div(
                    children=[
                        html.Label(
                            'Name:',
                            style={
                                'width': '140px'
                            }
                        ),
                        html.Div(
                            id='order_name_input_',
                            style={
                                'width': '325px',
                                'display': 'inline-block'
                            }
                        )
                    ]
                ),
                # Number stations
                html.Div(
                    children=[
                        html.Label(
                            'Number stations:',
                            style={
                                'width': '140px',
                                'margin-top': '9px'
                            }
                        ),
                        html.Div(
                            id='order_stations_input_',
                            style={
                                'width': '325px',
                                'display': 'inline-block'
                            }
                        )
                    ]
                ),
                # Priority
                html.Div(
                    children=[
                        html.Label(
                            'Priority:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='order_priority_input_',
                            placeholder='priority',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Storage
                html.Div(
                    children=[
                        html.Label(
                            'Storage:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='order_storage_input_',
                            placeholder='storage',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Source
                html.Div(
                    children=[
                        html.Label(
                            'Source:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='order_source_input_',
                            placeholder='source name',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Sink
                html.Div(
                    children=[
                        html.Label(
                            'Sink:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='order_sink_input_',
                            placeholder='sink name',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Horizontal line
                html.Hr(
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Attributes
                html.Div(
                    id='order_attribute_div',
                    children=[
                        html.Label(
                            'Attributes:',
                            style={
                                'width': '140px',
                            }
                        ),
                        html.Div(
                            children=[
                                # Table
                                dash_table.DataTable(
                                    id='order_attribute_input',
                                    columns=[
                                        {"name": 'name', "id": 'name'},
                                        {"name": 'distribution', "id": 'distribution.'},
                                        {"name": 'parameter', "id": 'parameter'}
                                    ],
                                    data=[],
                                    editable=False,
                                    # row_deletable=True,
                                    style_table={
                                        'width': '325px'
                                    }
                                ),
                                # Add component button
                                dbc.Button(
                                    'Add attribute',
                                    id='add_attribute_order',
                                    n_clicks=0,
                                    style={
                                        'height': '',
                                        'margin-top': '7px',
                                        'margin-left': '202px'
                                    }
                                )
                            ],
                            style={
                                'display': 'inline-block',
                                'vertical-align': 'top'
                            }
                        ),
                    ],
                    style={
                        'margin-top': '-9px'
                    }
                )
            ]
        ),
        dbc.ModalFooter(
            html.Div(
                children=[
                    dbc.Button(
                        "Info",
                        id="info_change_order",
                        className="ms-auto",
                        n_clicks=0,
                        style={
                            'margin-right': '8px',
                            'width': '80px'
                        }
                    ),
                    dbc.Button(
                        "Save",
                        id="submit_change_order",
                        className="ms-auto",
                        n_clicks=0,
                        style={
                            'width': '80px'
                        }
                    )
                ]
            )
        ),
    ]
)

# Mdl_change_station #0002
mdl_change_station = dbc.Modal(
    id="modal_change_station",
    centered=True,
    is_open=False,
    children=[
        dbc.ModalHeader(
            dbc.ModalTitle("Change station")
        ),
        dbc.ModalBody(
            children=[
                # Station name
                html.Div(
                    children=[
                        html.Label(
                            'Name:',
                            style={
                                'width': '140px',
                            }
                        ),
                        dcc.Input(
                            id='station_name_input',
                            placeholder='station name',
                            style={
                                'width': '325px'
                            }
                        )
                    ]
                ),
                # Capacity
                html.Div(
                    children=[
                        html.Label(
                            'Capacity:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='station_capacity_input',
                            placeholder='capacity',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Storage
                html.Div(
                    children=[
                        html.Label(
                            'Storage:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='station_storage_input',
                            placeholder='storage',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Measurement
                html.Div(
                    children=[
                        html.Label(
                            'Measurement:',
                            style={
                                'margin-top': '4px',
                                'width': '140px'
                            }
                        ),
                        dcc.Dropdown(
                            id='station_measurement_input',
                            options=[
                                {'label': 'True', 'value': '1'},
                                {'label': 'False', 'value': '0'}
                            ],
                            placeholder='measurement',
                            style={
                                'width': '325px',
                                'height': '20px',
                                'vertical-align': 'top'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px',
                        'display': 'flex'
                    }
                ),
                # Horizontal line
                html.Hr(),
                # Dropdown order
                html.Div(
                    children=[
                        html.Label(
                            'Order:',
                            style={
                                'margin-top': '4px',
                                'width': '140px'
                            }
                        ),

                        dcc.Dropdown(
                            id='station_dd_input',
                            options=[

                            ],
                            placeholder='order',
                            style={
                                'width': '325px',
                                'height': '20px',
                                'vertical-align': 'top'
                            }
                        )

                    ],
                    style={
                        'margin-top': '-8px',
                        'display': 'flex'
                    }
                ),
                # Function
                html.Div(
                    children=[
                        html.Label(
                            'Function:',
                            style={
                                'width': '140px',
                            }
                        ),
                        dcc.Input(
                            id='station_function_input',
                            placeholder='function',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '17px'
                    }
                ),
                # RadioItems
                html.Div(
                    children=[
                        dcc.RadioItems(
                            id='station_radio_input',
                            options=[
                                {'label': 'machining', 'value': 'machining'},
                                {'label': 'assembly', 'value': 'assembly'}
                            ],
                            value='machining',
                            labelStyle={'display': 'inline-block'},
                            inputStyle={"margin-right": "0px"}
                        )
                    ],
                    style={
                        'margin-top': '7px',
                        'margin-left': '140px',
                        'width': '325px'
                    }
                ),
                # Demand
                html.Div(
                    id='station_demand_div',
                    children=[
                        html.Label(
                            'Demand:',
                            style={
                                'width': '140px',
                            }
                        ),
                        dcc.Input(
                            id='station_demand_input',
                            placeholder='demand',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Component
                html.Div(
                    id='station_component_div',
                    children=[
                        html.Label(
                            'Component:',
                            style={
                                'width': '140px',
                            }
                        ),
                        html.Div(
                            children=[
                                # Table
                                dash_table.DataTable(
                                    id='station_cd_input',
                                    columns=[
                                        {"name": 'component', "id": 'component', 'presentation': 'dropdown'},
                                        {"name": 'demand', "id": 'demand'}
                                    ],
                                    data=[],
                                    editable=True,
                                    row_deletable=True,
                                    dropdown={
                                        'component': {
                                            'options': [
                                                {'label': 'test_1', 'value': 'test_1'},
                                                {'label': 'test_2', 'value': 'test_2'}
                                            ]
                                        }
                                    },
                                    style_table={
                                        'width': '325px'
                                    }
                                ),
                                # Add component button
                                dbc.Button(
                                    'Add component',
                                    id='add_row_order',
                                    n_clicks=0,
                                    style={
                                        'height': '',
                                        'margin-top': '7px',
                                        'margin-left': '180.5px'
                                    }
                                )
                            ],
                            style={
                                'display': 'inline-block',
                                'vertical-align': 'top'
                            }
                        ),
                    ],
                    style={
                        'margin-top': '9px',
                        'display': 'none'
                    }
                ),
                # Horizontal line
                html.Hr(
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Attributes
                html.Div(
                    id='station_attribute_div',
                    children=[
                        html.Label(
                            'Attributes:',
                            style={
                                'width': '140px',
                            }
                        ),
                        html.Div(
                            children=[
                                # Table
                                dash_table.DataTable(
                                    id='station_attribute_input',
                                    columns=[
                                        {"name": 'name', "id": 'name'},
                                        {"name": 'distribution', "id": 'distribution.'},
                                        {"name": 'parameter', "id": 'parameter'}
                                    ],
                                    data=[],
                                    editable=False,
                                    # row_deletable=True,
                                    style_table={
                                        'width': '325px'
                                    }
                                ),
                                # Add component button
                                dbc.Button(
                                    'Add attribute',
                                    id='add_attribute_station',
                                    n_clicks=0,
                                    style={
                                        'height': '',
                                        'margin-top': '7px',
                                        'margin-left': '202px'
                                    }
                                )
                            ],
                            style={
                                'display': 'inline-block',
                                'vertical-align': 'top'
                            }
                        ),
                    ],
                    style={
                        'margin-top': '-9px'
                    }
                )
            ]
        ),
        dbc.ModalFooter(
            html.Div(
                children=[
                    dbc.Button("Info", id="info_change_station", className="ms-auto", n_clicks=0,
                               style={'margin-right': '8px', 'width': '80px'}),
                    dbc.Button("Save", id="submit_change_station", className="ms-auto", n_clicks=0,
                               style={'width': '80px'})
                ]
            )
        ),
    ]
)

# Mdl_create_files #0003
mdl_create_files = dbc.Modal(
    id="modal_creat_files",
    centered=True,
    is_open=False,
    children=[
        dbc.ModalHeader(
            dbc.ModalTitle("Create files")
        ),
        dbc.ModalBody(
            children=[
                # Project name
                html.Div(
                    children=[
                        html.Label(
                            'Name:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='name_input',
                            placeholder='project name',
                            style={
                                'width': '325px'
                            }
                        )
                    ]
                ),
                # Path
                html.Div(
                    children=[
                        html.Label(
                            'Path:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='path_input',
                            placeholder='path',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                )

            ]
        ),
        dbc.ModalFooter(
            html.Div(
                children=[
                    dbc.Button("Info", id="info_create_files", className="ms-auto", n_clicks=0,
                               style={'margin-right': '8px', 'width': '80px'}),
                    dbc.Button("Create", id="submit_create_files", className="ms-auto", n_clicks=0,
                               style={'width': '80px'})
                ]
            )
        ),
    ]
)

# Mdl_add_order #0004
mdl_add_order = dbc.Modal(
    id="modal",
    centered=True,
    is_open=False,
    children=[
        dbc.ModalHeader(
            dbc.ModalTitle("Add order")
        ),
        dbc.ModalBody(
            children=[
                # Order Name
                html.Div(
                    children=[
                        html.Label(
                            'Order name:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='order_name_input',
                            placeholder='order name',
                            style={
                                'width': '325px'
                            }
                        )
                    ]
                ),
                # Source
                html.Div(
                    children=[
                        html.Label(
                            'Source name:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='source_name_input',
                            placeholder='source name',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Sink
                html.Div(
                    children=[
                        html.Label(
                            'Sink name:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='sink_name_input',
                            placeholder='sink name',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Order Number Stations
                html.Div(
                    children=[
                        html.Label(
                            'Number stations:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='number_stations_input',
                            placeholder='number stations',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Storage
                html.Div(
                    children=[
                        html.Label(
                            'Storage:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='storage_input',
                            placeholder='storage',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
                # Priority
                html.Div(
                    children=[
                        html.Label(
                            'Priority:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='priority_input',
                            placeholder='priority',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                )

            ]
        ),
        dbc.ModalFooter(
            html.Div(
                children=[
                    dbc.Button("Info", id="info_add_order", className="ms-auto", n_clicks=0,
                               style={'margin-right': '8px', 'width': '60px'}),
                    dbc.Button("Save", id="submit_add_order", className="ms-auto", n_clicks=0,
                               style={'width': '60px'})
                ]
            )
        ),
    ]
)

# Mdl_combine_stations #0005
mdl_combine_stations = dbc.Modal(
    id="modal_combine_stations",
    centered=True,
    is_open=False,
    children=[
        dbc.ModalHeader(
            dbc.ModalTitle("Combine stations")
        ),
        dbc.ModalBody(
            children=[
                # First station
                html.Div(
                    children=[
                        html.Label(
                            'Name station 1:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='cs_station_1',
                            placeholder='first station name',
                            style={
                                'width': '325px'
                            }
                        )
                    ]
                ),
                # Second station
                html.Div(
                    children=[
                        html.Label(
                            'Name station 2:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='cs_station_2',
                            placeholder='second station name',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px'
                    }
                ),
            ]
        ),
        dbc.ModalFooter(
            html.Div(
                children=[
                    dbc.Button("Info", id="cs_info", className="ms-auto", n_clicks=0,
                               style={'margin-right': '8px', 'width': '60px'}),
                    dbc.Button("Save", id="cs_save", className="ms-auto", n_clicks=0,
                               style={'width': '60px'})
                ]
            )
        ),
    ]
)

# Mdl_add_attribute    #0006
mdl_add_attribute = dbc.Modal(
    id="modal_add_attribute",
    centered=False,
    is_open=False,
    style={
        'color': 'gray'
    },
    children=[
        dbc.ModalHeader(
            dbc.ModalTitle("Add attribute"),
            close_button=False
        ),
        dbc.ModalBody(
            children=[
                # Attribute
                html.Div(
                    children=[
                        html.Label(
                            'Attribute name:',
                            style={
                                'width': '140px'
                            }
                        ),
                        dcc.Input(
                            id='attribute_name_input',
                            placeholder='attribute name',
                            style={
                                'width': '325px'
                            }
                        )
                    ]
                ),
                # Distribution
                html.Div(
                    children=[
                        html.Label(
                            'Distribution:',
                            style={
                                'margin-top': '4px',
                                'width': '140px'
                            }
                        ),
                        dcc.Dropdown(
                            id='attr_dist_input',
                            options=[
                                {'label': 'fix', 'value': 'fix'},
                                {'label': 'binary', 'value': 'binary'},
                                {'label': 'binomial', 'value': 'binomial'},
                                {'label': 'normal', 'value': 'normal'},
                                {'label': 'uniform', 'value': 'uniform'},
                                {'label': 'poisson', 'value': 'poisson'},
                                {'label': 'exponential', 'value': 'exponential'},
                                {'label': 'lognormal', 'value': 'lognormal'},
                                {'label': 'chisquare', 'value': 'chisquare'},
                                {'label': 'standard-t', 'value': 'standard-t'}
                            ],
                            placeholder='distribution',
                            style={
                                'width': '325px',
                                'height': '20px',
                                'vertical-align': 'top'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px',
                        'margin-bottom': '17px',
                        'display': 'flex'
                    }
                ),
                # Parameter 1
                html.Div(
                    id='param_one_div',
                    children=[
                        html.Div(
                            id='add_attr_param_one',
                            style={
                                'width': '140px',
                                'display': 'inline-block'
                            }
                        ),
                        dcc.Input(
                            id='add_attr_param_one_input',
                            placeholder='parameter one',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px',
                        'display': 'none'
                    }
                ),
                # Parameter 2
                html.Div(
                    id='param_two_div',
                    children=[
                        html.Div(
                            id='add_attr_param_two',
                            style={
                                'width': '140px',
                                'display': 'inline-block'
                            }
                        ),
                        dcc.Input(
                            id='add_attr_param_two_input',
                            placeholder='parameter two',
                            style={
                                'width': '325px'
                            }
                        )
                    ],
                    style={
                        'margin-top': '7px',
                        'display': 'none'
                    }
                )
            ],
        ),
        dbc.ModalFooter(
            html.Div(
                children=[
                    dbc.Button("Info", id="add_attribute_info", className="ms-auto", n_clicks=0,
                               style={'margin-right': '8px', 'width': '60px'}),
                    dbc.Button("Save", id="add_attribute_save", className="ms-auto", n_clicks=0,
                               style={'width': '60px'})
                ]
            )
        ),
    ]
)

# Mdl_edit_factory #0007
mdl_edit_factory = dbc.Modal(
    id="mdl_edit_factory",
    centered=True,
    is_open=False,
    children=[
        dbc.ModalHeader(
            dbc.ModalTitle("Edit factory")
        ),
        dbc.ModalBody(
            children=[
                # Attributes
                html.Div(
                    id='factory_attribute_div',
                    children=[
                        html.Label(
                            'Functions:',
                            style={
                                'width': '140px',
                            }
                        ),
                        html.Div(
                            children=[
                                # Table
                                dash_table.DataTable(
                                    id='global_function_input',
                                    columns=[
                                        {"name": 'name', "id": 'name'},
                                    ],
                                    data=[],
                                    editable=False,
                                    # row_deletable=True,
                                    style_table={
                                        'width': '325px'
                                    }
                                ),
                                html.Div(
                                    children=[
                                        # Function name input
                                        dcc.Input(
                                            id='function_name_input',
                                            placeholder='function name',
                                            style={
                                                'width': '194px',
                                                'display': 'inline-block',
                                                'vertical-align': 'middle'
                                            }
                                        ),
                                        # Add component button
                                        dbc.Button(
                                            'Add function',
                                            id='add_global_attribute',
                                            n_clicks=0,
                                            style={
                                                'height': '',
                                                'margin-top': '7px',
                                                'margin-left': '10px'
                                            }
                                        )
                                    ],
                                    style={
                                        'display': 'inline-block',
                                        'overflow': 'auto'
                                    }
                                )

                            ],
                            style={
                                'display': 'inline-block',
                                'vertical-align': 'top'
                            }
                        ),
                        # Horizontal line
                        html.Hr(
                            style={
                                'margin-top': '7px'
                            }
                        ),
                        html.Label(
                            'Attributes:',
                            style={
                                'width': '140px',
                            }
                        ),
                        html.Div(
                            children=[
                                # Table
                                dash_table.DataTable(
                                    id='factory_attribute_input',
                                    columns=[
                                        {"name": 'name', "id": 'name'},
                                        {"name": 'distribution', "id": 'distribution.'},
                                        {"name": 'parameter', "id": 'parameter'}
                                    ],
                                    data=[],
                                    editable=False,
                                    # row_deletable=True,
                                    style_table={
                                        'width': '325px'
                                    }
                                ),
                                # Add component button
                                dbc.Button(
                                    'Add attribute',
                                    id='add_attribute_factory',
                                    n_clicks=0,
                                    style={
                                        'height': '',
                                        'margin-top': '7px',
                                        'margin-left': '202px'
                                    }
                                )
                            ],
                            style={
                                'display': 'inline-block',
                                'vertical-align': 'top'
                            }
                        ),
                    ],
                    style={
                        'margin-top': '-9px'
                    }
                )

            ]
        ),
        dbc.ModalFooter(
            html.Div(
                children=[
                    dbc.Button("Info", id="info_edit_factory", className="ms-auto", n_clicks=0,
                               style={'margin-right': '8px', 'width': '60px'}),
                    dbc.Button("Save", id="submit_edit_factory", className="ms-auto", n_clicks=0,
                               style={'width': '60px'})
                ]
            )
        ),
    ]
)
