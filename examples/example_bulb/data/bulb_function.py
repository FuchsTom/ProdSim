from random import random

# ---- sources ------------------------

def source_1(env, factory):
    yield env.timeout(1)
    amount = 1
    if 480 <= env.now % 1440 <= 960:
        amount += int(normalvariate(3, 0.8))
    yield amount


def source_2(env, factory):
    yield env.timeout(1)
    yield 2

# ---- sinks --------------------------

# ---- process functions --------------

from random import normalvariate
def bridge_func(env, item, machine, factory):

    if item.attr_b_2:
        item.reject = True

    if machine.wear > 6.2:
        yield env.timeout(2)
        machine.wear = 0

    machine.wear += normalvariate(0.05,0.01)
    yield env.timeout(1)

    yield env.timeout(1)


def mount_func(env, item, machine, factory):

    # To demonstrate how get_rejected works
    if random() < 0.01:
        item.reject = True

    yield env.timeout(1)


def tubolate_func(env, item, machine, factory):
    yield env.timeout(1)


def forming_func(env, item, machine, factory):
    yield env.timeout(1)


def pump_pinch_func(env, item, machine, factory):
    yield env.timeout(1)


def tt(env, item, machine, factory):
    yield env.timeout(1)


def vc_1(env, item, machine, factory):
    yield env.timeout(1)


def vc_2(env, item, machine, factory):
    yield env.timeout(1)


def vc_3(env, item, machine, factory):
    yield env.timeout(1)


def vc_4(env, item, machine, factory):
    yield env.timeout(1)


def vc_5(env, item, machine, factory):
    yield env.timeout(1)

# ---- global functions ---------------

# ---- distributions ------------------
