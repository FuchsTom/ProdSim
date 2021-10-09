def source1(env, factory):
    yield env.timeout(1)
    yield 1


def function1(env, item, machine, factory):
    yield env.timeout(1)
