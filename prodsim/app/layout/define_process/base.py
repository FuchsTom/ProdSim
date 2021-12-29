"""This file contains all components that form the basis of the web application and are open regardless of the current
dialog.

The base is the graph and the top-level buttons for interaction.
"""

# Since the file can become very large during development, a TOC with unique labels is given
#
# H1_Headline         #0001
# Cyt_Graph           #0002
# Btn_add_order       #0003
# Btn_create_files    #0004
# Btn_edit_factory    #0005
# Btn_refresh_graph   #0006
# Btn_combine_station #0007
# Div_Buttons         #0008
# Div_Graph           #0009

from dash import html
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

# H1_Headline #0001
headline = html.H1(
    'ProdSim - Define process',
    className="Test",
    style={
        'textAlgin': 'center',
        'margin-left': '1vw'
    },
    id='header'
)

# Cyt_Graph #0002
cytoscape = cyto.Cytoscape(
    id='cytoscape',
    elements=[],
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
    ],
    layout={
        'name': 'breadthfirst',
        'roots': []
    },
    style={
        'height': '85vh',
        'width': '98vw',
        'border': 'black solid'
    }
)

# Btn_add_order #0003
btn_add_order = dbc.Button(
    'Add order',
    id='add-order',
    style={
        'margin-top': '1vw',
        "width": '18vw',
        'font-size': '15px',
        'margin-right': '1vw'
    },
    color='dark',
    outline=True
)

# Btn_create_files #0004
btn_create_files = dbc.Button(
    'Create files',
    id='create-files',
    style={
        'margin-top': '1vw',
        "width": '18vw',
        'font-size': '15px',
        'margin-left': '1vw'
    },
    color='danger',
    outline=True
)

# Btn_edit_factory #0005
btn_edit_factory = dbc.Button(
    'Edit factory',
    id='edit-factory',
    style={
        'margin-top': '1vw',
        "width": '18vw',
        'font-size': '15px',
        'margin-left': '1vw',
        'margin-right': '1vw'
    },
    color='dark',
    outline=True
)

# Btn_refresh_graph #0006
btn_refresh_graph = dbc.Button(
    'Refresh graph',
    id='refresh-graph',
    style={
        'margin-top': '1vw',
        "width": '18vw',
        'font-size': '15px',
        'margin-left': '1vw',
        'margin-right': '1vw'
    },
    color='danger',
    outline=True
)

# Btn_combine_station #0007
# Btn_refresh_graph #0006
btn_combine_stations = dbc.Button(
    'Combine stations',
    id='combine-stations',
    style={
        'margin-top': '1vw',
        "width": '18vw',
        'font-size': '15px',
        'margin-left': '1vw',
        'margin-right': '1vw'
    },
    color='dark',
    outline=True
)

# Div_Buttons #0008
div_buttons = html.Div(
    children=[
        btn_add_order,
        btn_edit_factory,
        btn_combine_stations,
        btn_refresh_graph,
        btn_create_files
    ],
    style={
        'display': 'inline-block',
        'vertical-align': 'top',
        'margin-right': '1vw',
        'margin-left': '1vw'
    }
)

# Div_Graph #0009
div_graph = html.Div(
    children=[
        cytoscape
    ],
    style={
        'display': 'inline-block',
        'vertical-align': 'top',
        'margin-right': '2vw',
        'margin-left': '1vw'
    }
)
