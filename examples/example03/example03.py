from prodsim import Environment

# This code is used to plot the data
# To run this code matplotlib, numpy and pandas must be installed

# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np
#
# def plot_demand():
#
#     def moving_average(x, w):
#         return np.convolve(x, np.ones(w), 'valid')/w
#
#     data = pd.read_csv('./output/factory.csv')
#     data_without_outlier = data[(data['time'] >= 1440) & (data['current_demand'] <= 100)]
#
#     fig, ax1 = plt.subplots()
#     color = 'tab:blue'
#     ax1.set_xlabel('Sim. time')
#     ax1.set_ylabel('Bolts in store', color=color)
#     ax1.plot(data[data['time'] >= 1440]['time'], data[data['time'] >= 1440]['number_bolts'], color=color)
#     ax1.tick_params(axis='y', labelcolor=color)
#
#     ax2 = ax1.twinx()
#     color = 'tab:red'
#     ax2.set_ylabel('Demand', color=color)
#     ax2.plot(data_without_outlier['time'][:-19],
#              moving_average(data_without_outlier['current_demand'], 20), color=color)
#     ax2.tick_params(axis='y', labelcolor=color)
#     ax2.set_ylim([0, 50])
#
#     fig.tight_layout()
#     plt.savefig('./output/demand_bolts.png')

if __name__ == '__main__':

    # Create simulation environment
    env = Environment()

    # Read in the process files
    env.read_files('./data/process.json', './data/function.py')

    # Inspect and visualize (optional)
    # env.inspect()
    # env.visualize()

    # Start the simulation
    env.simulate(sim_time=5760, progress_bar=True, track_components=['factory'])

    # Export the simulation data
    env.data_to_csv('./output/')

    # Plot 'surface' over simulation time (optional)
    # plot_demand()
