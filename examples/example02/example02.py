from prodsim import Environment

# This code is used to plot the data
# To run this code matplotlib and pandas must be installed

# import matplotlib.pyplot as plt
# import pandas as pd
#
# def plot_surface():
#
#     surface_data = pd.read_csv('./output/shaft.csv')
#
#     labels = ['drill', 'lathe', 'polisher']
#
#     for index, label in enumerate(labels):
#         plt.plot(surface_data[surface_data['station_id'] == index]['time'],
#                  surface_data[surface_data['station_id'] == index]['surface'], label=label)
#
#     plt.xlabel('Sim. time')
#     plt.ylabel('Surface roughness')
#     plt.title('Surface over simulated time')
#     plt.legend(loc='upper right')
#
#     plt.savefig('./output/shaft_surface.png')

if __name__ == '__main__':

    # Create simulation environment
    env = Environment()

    # Read in the process files
    env.read_files('./data/process.json', './data/function.py')

    # Inspect and visualize (optional)
    # env.inspect()
    # env.visualize()

    # Start the simulation
    env.simulate(sim_time=4320, track_components=['shaft'], progress_bar=True)

    # Export the simulation data
    env.data_to_csv(path_to_wd='./output/', remove_column=['item_id'], keep_original=False)

    # Plot 'surface' over simulation time (optional)
    # plot_surface()
