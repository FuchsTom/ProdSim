import random

# ---- sources ------------------------

def shaft_source(env, factory):
    yield env.timeout(1)
    yield 1

# ---- sinks ---------------------------

# ---- process functions --------------

def drilling(env, item, machine, factory):

    if random.random() < machine.drill_breakage:
        item.surface += random.normalvariate(2.5, 0.1)

    yield env.timeout(2)

def turning(env, item, machine, factory):

    if machine.wear >= 1:
        machine.wear = 0
        yield env.timeout(10)

    item.surface += machine.wear**2 * 1.5 - 2
    # it's possible to use the machine 50 times, before it has to be maintained
    machine.wear += 0.006
    yield env.timeout(1)

def polishing(env, item, machine, factory):

    item.surface -= 8 - factory.temperature * 0.3

    yield env.timeout(1)

# ---- global functions ---------------


temp_dict = {0: 19, 240: 18, 480: 20, 720: 23, 960: 22, 1200: 20}

def temperature_func(env, factory):

    # determine the current time of day in minutes
    day_time: int = env.now % 1440

    # Set the temperature in the factory based on the time of day
    factory.temperature = temp_dict[day_time]

    yield env.timeout(240)

# ---- distributions ------------------
