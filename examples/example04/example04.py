from prodsim import Environment

# import pandas as pd
# import matplotlib.pyplot as plt

# The following code generates a plot of the number of rejected workpieces by reasons r6, r7, r8. To execute this code
# first the simulation has to be run and the libraries pandas and matplotlib must be installed.
#
# def plot_rejected():
#
#     data = pd.read_csv('./output/quality_check.csv')
#
#     plt.plot(data['time'], data['r8'], label='r8')
#     plt.plot(data['time'], data['r7'], label='r7')
#     plt.plot(data['time'], data['r6'], label='r6')
#
#     plt.xlabel('Sim. time')
#     plt.ylabel('Number rejected figures')
#     plt.title('Rejections over time by rejection reason')
#     plt.legend(loc='upper left')
#
#     plt.savefig('./output/rejected_profile.png')

# The code below combines all the individual output files into a single file that maps individual figures line by line.
#
# def merge():
#
#     # Station id, where workpieces are observed (The station_id of 1
#     # corresponds to the station 'assemble_figure' - see process.json)
#     station_id: int = 1
#     path = './output/'
#
#     def get_df(name: str, num_main_args: int, sub: bool = True, amount: int = None):
#
#         index_col, labels = 'item_id', ['station_id']
#         if sub:
#             index_col, labels = 'comp', ['station_id', 'item_id']
#
#         # set 'index_col' as row index, and remove the column 'time' for all assemble objects by usecols (+3)
#         iter_csv = pd.read_csv(path + name + '.csv', usecols=[i for i in range(
#             num_main_args + 3)], iterator=True, chunksize=10_000, index_col=index_col)
#
#         # build DataFrame and remove the columns 'labels'
#         temp_df = pd.concat([chunk[chunk['station_id'] == station_id] for chunk in iter_csv]).drop(labels=labels, axis=1)
#
#         # if there are multiple objects split the dataframe an return them as a list
#         if amount is None:
#             return temp_df
#         return [temp_df.groupby('comp').nth(i).add_suffix('-%s' % i) for i in range(amount)]
#
#     # First the subcomponents of 'upper_limb' are combined
#     upper_limb = get_df("upper_limb", 1, sub=False)
#     arm = get_df("arm", 2)
#     hand = get_df("hand", 1)
#
#     # merge the DataFrames by their index and change the index to 'comp'.
#     upper_limb = pd.concat([upper_limb, arm, hand], axis=1).reindex(upper_limb.index).set_index('comp')
#     upper_limb = [upper_limb.groupby('comp').nth(i).add_suffix('-%s' % i) for i in range(2)]
#     del arm, hand
#
#     # After the 'upper_limb' file has been combined, the figure file itself can be combined
#     figure = get_df("figure", 5, sub=False)
#     head = get_df("head", 1)
#     body = get_df("body", 5)
#     legs = get_df("leg", 1, amount=2)
#
#     figure = pd.concat([figure, head, legs[0], legs[1], upper_limb[0], upper_limb[1], body], axis=1)
#     del head, legs, upper_limb, body
#
#     # Safe the DataFrame and remove the index
#     figure.to_csv(path + 'figure_merged.csv', sep=',', index=False)


if __name__ == '__main__':

    # Create a new simulation environment
    env = Environment()

    # Read in the process files
    env.read_files('./data/process.json', './data/function.py')

    # Inspect and visualize the production process (optional)
    # env.inspect()
    # env.visualize()

    # Start the simulation
    env.simulate(sim_time=4320, progress_bar=True)

    # Export the data
    env.data_to_csv('./output/')

    # Plot the simulation output (optional)
    # plot_rejected()

    # Merge the output files to a single figure-file (optional)
    # merge()
