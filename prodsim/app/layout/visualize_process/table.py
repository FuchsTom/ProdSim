""" Contains the layout elements for displaying the table of the app visualize

"""

# Searchable TOC of layout elements
#
# Lbl_order           #0001
# Dwn_dropdown        #0002
# Lbl_order_data      #0003
# Tbl_item            #0004
# Lbl_station         #0005
# Tbl_station         #0006
# Div_table           #0007


from dash import html, dcc, dash_table

# Lbl_order #0001
lbl_order = html.Label(
    'Order:',
    style={
        'font-size': '20px'
    }
)

# Dwn_dropdown #0002
dwn_dropdown = dcc.Dropdown(
    id='item_dropdown',
    options=[],
    value=-1,
    style={
        'width': '38vw',
        'margin-bottom': '1vw',
        'margin-top': '0.4vw',
        'border-color': 'black'
    },
    placeholder="Select an item"
)

# Lbl_order_data #0003
lbl_order_data = html.Label(
    'Order Data:',
    style={'font-size': '20px'}
)

# Tbl_item #0004
tbl_item = dash_table.DataTable(
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
)

# Lbl_station #0005
lbl_station = html.Label(
    'Station Data:',
    style={
        'font-size': '20px'
    }
)

# Tbl_station #0006
tbl_station = dash_table.DataTable(
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
)

# Div_table #0007
div_table = html.Div(
    children=[
        lbl_order,
        dwn_dropdown,
        lbl_order_data,
        tbl_item,
        lbl_station,
        tbl_station
    ],
    style={
        'display': 'inline-block',
        'vertical-align': 'top',
        'margin-right': '1vw'
    }
)
