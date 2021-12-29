""" Contains the layout elements for displaying the graph of the app visualize

"""

# Searchable TOC of layout elements
#
# H1_Headline         #0001
# Cyt_Graph           #0002
# Div_graph           #0003

import dash_cytoscape as cyto
from dash import html

# H1_Headline #0001
headline = html.H1(
    'ProdSim Visualizer',
    style={
        'textAlgin': 'center',
        'margin-left': '1vw'
    }
)

# Cyt_Graph #0002
graph = cyto.Cytoscape(
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
        'height': '80vh',
        'width': '55vw',
        'border': 'black solid'
    }
)

# Div_graph #0003
div_graph = html.Div(
    children=[
        graph
    ],
    style={
        'display': 'inline-block',
        'vertical-align': 'top',
        'margin-right': '2vw',
        'margin-left': '1vw'
    }
)
