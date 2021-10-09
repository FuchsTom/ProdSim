from random import normalvariate, random

# ---- sources ------------------------

def infinite_source(env, factory):
    yield 1

# ---- sinks ---------------------------


# Defines the demand distribution over time
time_dict = {1: [0, 4], 2: [4, 8], 3: [8, 12], 4: [12, 16], 5: [16, 20], 6: [20, 24]}
demand_dict = {1: [7, 0.5], 2: [8, 0.7], 3: [20.5, 1], 4: [22, 1.7], 5: [20, 2.5], 6: [12, 1.2]}

def bolt_sink(env, factory):

    demand = 0
    day_time = env.now % 1440

    # Determine the standard demand
    for index, time_interval in time_dict.items():
        if time_interval[0] < day_time/60 < time_interval[1]:
            dis = demand_dict[index]
            demand += int(normalvariate(dis[0], dis[1]))
            break

    # Determining the additional demand
    if random() < 0.004:
        demand += int(abs(normalvariate(250, 20)))

    yield env.timeout(1)

    # Update number of bolts
    factory.number_bolts -= demand

    # Just for output plotting purpose
    factory.current_demand = demand

    yield demand

# ---- process functions --------------

def forging(env, item, machine, factory):

    while True:
        if factory.active_machines < factory.max_active_machines:
            break
        yield env.timeout(1)

    factory.active_machines += 1

    yield env.timeout(1)

    factory.number_bolts += 6

    factory.active_machines -= 1

# ---- global functions ---------------


control_logic = {1000: 5, 2000: 4, 3000: 3, 4000: 2, 5000: 1}

def global_control(env, factory):

    # Set max_active_machines_based on number_bolts
    for quantity in control_logic.keys():
        if factory.number_bolts < quantity:
            factory.max_active_machines = control_logic[quantity]
            break
        factory.max_active_machines = 0

    # Update every time step (minute)
    yield env.timeout(1)

# ---- distributions ------------------
