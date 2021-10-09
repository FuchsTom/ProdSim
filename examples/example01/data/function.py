# ---- sources ------------------------

def source_1(env, factory):
    yield env.timeout(1)
    yield 1

def source_2(env, factory):
    yield env.timeout(1)
    yield 2

# ---- sinks --------------------------

# ---- process functions --------------

def assemble_gb(env, item, machine, factory):
    yield env.timeout(1)

def quality_check(env, item, machine, factory):
    yield env.timeout(1)

def assemble_gs(env, item, machine, factory):
    yield env.timeout(1)

def heating(env, item, machine, factory):
    yield env.timeout(1)

def turning(env, item, machine, factory):
    yield env.timeout(1)

# ---- global functions ---------------

def glob_func_1(env, factory):
    yield env.timeout(1)

# ---- distributions ------------------
