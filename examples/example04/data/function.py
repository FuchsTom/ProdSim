from random import normalvariate

# ---- sources ------------------------

def source_1(env, factory):
    yield env.timeout(1)
    yield 1

def source_2(env, factory):
    yield env.timeout(1)
    yield 2

# ---- sinks ---------------------------

# ---- process functions --------------

def assemble_figure(env, item, machine, factory):

    # Get the diameters of the assembled items
    d3_1 = item.upper_limb[0].arm.d3
    d3_2 = item.upper_limb[1].arm.d3
    d9_1 = item.leg[0].d9
    d9_2 = item.leg[1].d9
    d10 = item.head.d10

    def get_t(d1, d2):
        return (d2 - d1 - 2)**3 + 20

    # Calculate the tension
    item.t4 = get_t(item.body.d4, d3_1)
    item.t5 = get_t(item.body.d5, d9_1)
    item.t6 = get_t(item.body.d6, d9_2)
    item.t7 = get_t(item.body.d7, d3_2)
    item.t8 = get_t(item.body.d8, d10)

    # Block the machine for the assembly time
    yield env.timeout(1)

def quality_check(env, item, machine, factory):

    # Limits for the tension
    t_min = 17.0
    t_max = 23.0

    def is_reject(t):
        if t <= t_min or t >= t_max:
            item.reject = True
            factory.rejected_id = item.item_id
            return True
        return False

    # Reject items and update profiling attributes
    if is_reject(item.t4):
        machine.r4 += 1
    if is_reject(item.t5):
        machine.r5 += 1
    if is_reject(item.t6):
        machine.r6 += 1
    if is_reject(item.t7):
        machine.r7 += 1
    if is_reject(item.t8):
        machine.r8 += 1
    if is_reject(item.upper_limb[0].t2):
        machine.r2_1 += 1
    if is_reject(item.upper_limb[1].t2):
        machine.r2_2 += 1

    # Block quality machine
    yield env.timeout(1)

def molding(env, item, machine, factory):

    if machine.hole_diameter >= 40.6:
        machine.hole_diameter = 40

    item.d8 = normalvariate(machine.hole_diameter, 0.4)

    machine.hole_diameter += 0.0004

    yield env.timeout(1)

def assemble_limb(env, item, machine, factory):

    d1 = item.hand.d1
    d2 = item.arm.d2

    item.t2 = (d1 - d2 - 2)**3 + 20

    yield env.timeout(1)

# ---- global functions ---------------

def global_update(env, factory):

    yield env.timeout(1)

# ---- distributions ------------------
