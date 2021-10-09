from prodsim import Environment

# from pandas import read_csv, concat
from itertools import tee

def simulate():

    # Create a new simulation environment
    env = Environment()

    # Read in the process files
    env.read_files('./data/bulb_process.json', './data/bulb_function.py')

    # Inspect and visualize the production process (optional)
    # env.inspect()
    # env.visualize()

    # Start the simulation
    # To ensure that the output files can still be viewed without problems, only a simulation time of 1000 is used here
    env.simulate(sim_time=1_000, progress_bar=True, max_memory=2, bit_type=32)

    # Export the data
    env.data_to_csv('./output/')

# def merge():
#
#     # Station id, where workpieces are observed
#     station_id: int = 8
#     path: str = './output/'
#
#     def get_df(name: str, num_attr: int, sub: bool = True, amount: int = None):
#         index_col, labels = 'item_id', ['station_id']
#         if sub:
#             index_col, labels = 'comp', ['station_id', 'item_id']
#         # set 'index_col' as row index, and remove the column 'time' for all assemble objects by usecols (+3)
#         iter_csv = read_csv(path + name + '.csv', usecols=[i for i in range(
#             num_attr + 3)], iterator=True, chunksize=10_000, index_col=index_col)
#         # build DataFrame and remove the columns 'labels'
#         temp_df = concat([chunk[chunk['station_id'] == station_id] for chunk in iter_csv]).drop(labels=labels, axis=1)
#         # if there are multiple objects split the dataframe an return them as a list
#         if amount is None:
#             return temp_df
#         return [temp_df.groupby('comp').nth(i).add_suffix('-%s' % i) for i in range(amount)]
#
#     bridge = get_df("bridge", 0, sub=False)
#     qb = get_df("quartz_bar", 6, amount=2)
#     mw = get_df("b_mo_wire", 2, amount=2)
#
#     # merge the DataFrames by their index and change the index to 'comp'.
#     bridge_df = concat([bridge, qb[0], qb[1], mw[0], mw[1]], axis=1).reindex(bridge.index).set_index('comp')
#     del qb, mw, bridge
#
#     housing = get_df("housing", 5, sub=False)
#     tu = get_df("tube", 1)
#     ca = get_df("capsule", 1)
#
#     housing_df = concat([housing, tu, ca], axis=1).reindex(housing.index).set_index('comp')
#     del tu, ca, housing
#
#     inner_part = get_df('inner_part', 7, sub=False)
#     co = get_df('coil', 0)
#     mw = get_df('m_mo_wire', 2, amount=2)
#     mf = get_df('mo_foil', 2, amount=2)
#
#     inner_part_df = concat([inner_part, co, mw[0], mw[1], mf[0], mf[1], bridge_df], axis=1).reindex(inner_part.index). \
#         set_index('comp')
#     del bridge_df, co, mw, mf, inner_part
#
#     bulb = get_df('bulb', 1, sub=False)
#     bulb_df = concat([bulb, inner_part_df, housing_df], axis=1).reindex(bulb.index)
#     del bulb, inner_part_df, housing_df
#
#     bulb_df.to_csv('./output/bulb_merged.csv', sep=',', index=False)
#
# def get_rejected():
#     # Station id, where workpieces are observed
#     station_id: int = 2
#     path: str = './output/'
#
#     def get_df(name: str, num_main_args: int, sub: bool = True, amount: int = None):
#         index_col, labels = 'item_id', ['station_id']
#         if sub:
#             index_col, labels = 'comp', ['station_id', 'item_id']
#         # set 'index_col' as row index, and remove the column 'time' for all assemble objects by usecols (+3)
#         iter_csv = read_csv(path + name + '.csv', usecols=[i for i in range(
#             num_main_args + 3)], iterator=True, chunksize=10_000, index_col=index_col)
#         # build DataFrame and remove the columns 'labels'
#         temp_df = concat([chunk[chunk['station_id'] == station_id] for chunk in iter_csv]).drop(labels=labels, axis=1)
#         # if there are multiple objects split the dataframe an return them as a list
#         if amount is None:
#             return temp_df
#         return [temp_df.groupby('comp').nth(i).add_suffix('-%s' % i) for i in range(amount)]
#
#     bridge = get_df("bridge", 0, sub=False)
#     qb = get_df("quartz_bar", 6, amount=2)
#     mw = get_df("b_mo_wire", 2, amount=2)
#
#     # merge the DataFrames by their index and change the index to 'comp'.
#     bridge_df = concat([bridge, qb[0], qb[1], mw[0], mw[1]], axis=1).reindex(bridge.index).set_index('comp')
#     del qb, mw, bridge
#
#     iter_1, iter_2 = tee(read_csv(path + 'inner_part.csv', usecols=[i for i in range(10)],
#                                   iterator=True, chunksize=10_000, index_col='item_id'))
#
#     temp_2 = concat([chunk[chunk['station_id'] == 2] for chunk in iter_1]).drop(labels=['station_id'], axis=1)
#     temp_8 = concat([chunk[chunk['station_id'] == 8] for chunk in iter_2]).drop(labels=['station_id'], axis=1)
#
#     inner_part = temp_2[~temp_2.index.isin(temp_8.index)][:-1]
#
#     co = get_df('coil', 0)
#     mw = get_df('m_mo_wire', 2, amount=2)
#     mf = get_df('mo_foil', 2, amount=2)
#
#     inner_part_df = concat([inner_part, co, mw[0], mw[1], mf[0], mf[1], bridge_df], axis=1).reindex(inner_part.index)
#     del bridge_df, co, mw, mf, inner_part
#
#     inner_part_df.drop(labels=['comp'], axis=1).to_csv(path + 'inner_part_rejected.csv', sep=',', index=True)


if __name__ == '__main__':

    simulate()

    # merge()

    # get_rejected()

