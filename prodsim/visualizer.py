from __future__ import annotations
from typing import List, TYPE_CHECKING
from os import path

from dash import Dash, html
import dash_bootstrap_components as dbc

# Import the layout elements
import prodsim.app.layout.define_process.base as base
import prodsim.app.layout.define_process.modal as modal
import prodsim.app.layout.define_process.popup as popup
import prodsim.app.layout.visualize_process.graph as graph
import prodsim.app.layout.visualize_process.table as table

# Import the callback functions
from prodsim.app.callbacks.define_process.callbacks import dp_callbacks
from prodsim.app.callbacks.visualize_process.callbacks import vis_callbacks

if TYPE_CHECKING:
    from prodsim.filehandler import FileHandler
    from prodsim.components import StationData, OrderData


class Visualizer:
    """Serves to visualize production processes and to define new processes via gui

    """

    @classmethod
    def visualize(cls, filehandler: FileHandler) -> None:
        """Entry point method for the Blackboard to start visualization"""

        assets_path = path.join(path.dirname(__file__) + '/app/assets/')
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder=assets_path)

        cls.__visualize_app(filehandler.order_data_list, filehandler.station_data_list, app)

        app.run_server(debug=True)

    @staticmethod
    def __visualize_app(order_data_list: List[OrderData], station_data_list: List[StationData],
                        app: Dash) -> None:
        """Defines the layout and the callbacks of the application

        defined in:
        layout -> prodsim.app.layout.visualize_process
        callbacks -> prodsim.app.callbacks.visualize_process
        """

        # layout
        app.layout = html.Div(
            children=[
                # graph
                graph.headline,
                graph.div_graph,

                # table
                table.div_table
            ]
        )

        # callbacks
        vis_callbacks(app, order_data_list, station_data_list)

    @classmethod
    def define_process(cls):
        """Entry point method for the Blackboard to start the process definition"""

        assets_path = path.join(path.dirname(__file__) + '/app/assets/')
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder=assets_path)

        cls.__dp_app(app)

        app.run_server(debug=True)

    @staticmethod
    def __dp_app(app: Dash) -> None:
        """Defines the layout and the callbacks of the application

        defined in:
        layout -> prodsim.app.layout.visualize_process
        callbacks -> prodsim.app.callbacks.visualize_process
        """

        # layout
        app.layout = html.Div(
            children=[
                # popup
                popup.alr_invalid_path,
                popup.alr_created_files,
                popup.alr_saved_change_o,
                popup.cfd_add_order,
                popup.cfd_files_alert,
                popup.cfd_files_info,
                popup.cfd_order_info,
                popup.cfd_combine_stations,
                popup.cfd_cs_alert,
                popup.cfd_change_o_alert,
                popup.cfd_change_order_info,
                popup.cfd_change_s_alert,
                popup.alr_saved_change_s,
                popup.cfd_attribute_alert,
                popup.cfd_attribute_info,
                popup.cfd_edit_factory_info,
                popup.cfd_global_function_alert,

                # modal
                modal.mdl_change_order,
                modal.mdl_change_station,
                modal.mdl_create_files,
                modal.mdl_add_order,
                modal.mdl_combine_stations,
                modal.mdl_add_attribute,
                modal.mdl_edit_factory,

                # base
                base.headline,
                base.div_graph,
                base.div_buttons
            ]

        )

        # callbacks
        dp_callbacks(app)
