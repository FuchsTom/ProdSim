from prodsim import Environment

if __name__ == '__main__':

    # create new simulation environment
    env = Environment()

    # read input files
    env.read_files('./data/process.json', './data/function.py')

    # Inspect the process data (uncomment)
    # env.inspect()

    # Visualize the process data (uncomment)
    env.visualize()
