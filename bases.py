import numpy as np

"""
python 3.6 type hinting seems to introduce some circular logic obstacles.

Perhaps this is due to "bad" design choices, but i don't think so.

See Rule_ class for explanation on multiple objects interacting
See Op_ class for explanation on customized magic method behavior with
objects of the same type.
"""


class Die_(object):
    pass


class Rule_(object):
    """
    Rules are given to Die instances as a way to modify their
    output, but themselves take Die instances as arguments for
    the case of rerolling, where a result is refused according
    to the rule and a new one is fetched.

    This creates momentarily circular logic, creating a disallowed
    scenario where:
        Die objects requiring Rule definition to run
        and Rule objects requiring Die definition to run

    These base classes make this instead:
        Die objects point to Die_ (child class), and Rule_ (type hint)
        Rule objects point to Die_ (type hint) and Rule_ (child class)

    """

    # signature
    def __call__(self, result: np.array, die: Die_):
        return result


class Selector_(object):
    """
    base class for Op objects. This class has defined magic method
    behavior for interacting with other Op instances, and for type hinting
    a class is not allowed to refer to it's own definition. Thus this
    base class is ued.
    """
    # signature
    def __call__(self, arr: np.array):
        return arr


class Aggregator_(object):
    # signature
    def __call__(self, arr: np.array):
        return arr


class Sum_(object):
    # signature
    def __call__(self, arr: np.array):
        if len(arr.shape) > 1:
            return np.sum(arr, axis=1)
        else:
            return arr


