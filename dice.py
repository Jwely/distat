from typing import List, Union, Callable
import numpy as np
import matplotlib.pyplot as plt


__author__ = 'Jwely'


class Modifier(object):

    def __init__(self, mod: int = None):
        if mod is None:
            mod = 0
        self.mod = mod

    def __call__(self, other, *args):
        def modified(other, *args):
            return other(*args) + self.mod
        return modified


class Die(object):

    def __init__(self, sides: int):
        self.sides = sides

    def __call__(self, n:  Union[int, float] = None):
        """ number of dice rolled decided when called """
        if n is None:
            n = 1

        result = np.random.randint(1, self.sides + 1, int(n))

        if n == 1:
            result.reshape(1, 1)

        return result

    def __rmul__(self, other: int):
        """ defines leading integer multiplicative behavior of die """
        assert isinstance(other, int)
        return Pool([self for _ in range(other)])


class D(Die):
    """ shorthand class for a Die"""
    pass


class Pool(object):

    def __init__(self, dice: List[Die]):
        """ A simple collection of multiple dice """
        self.dice = dice

    def __call__(self, *args):
        rolls = [d(*args) for d in self.dice]
        return np.column_stack(rolls)

    def __add__(self, other):
        """ modifies contents of dice pool """
        if isinstance(other, Pool):
            return Pool(self.dice + other.dice)
        elif isinstance(other, Die):
            return Pool(self.dice + other)


class Highest(object):

    def __init__(self, n: int):

        self.n = n

    def __call__(self, pool: Pool, *args):
        rolls = np.sort(pool(*args))
        return rolls[:, -self.n]


class Lowest(object):
    def __init__(self, n: int):
        self.n = n

    def __call__(self, pool: Pool, *args):
        rolls = np.sort(pool(*args))
        return rolls[:, self.n]


class Add(object):
    def __call__(self, pool: Pool, *args):
        rolls = np.sum(pool(*args))
        return rolls

Aggregator = Union[Highest, Lowest, Add]


class Check(object):

    def __init__(self, agg: Aggregator, min: int = None, max: int = None):
        self.agg = agg
        self.min = min
        self.max = max

    def __call__(self, pool: Pool, *args):
        rolls = self.agg(pool, *args)
        if self.min is not None and self.max is not None:
            return self.min < rolls < self.max
        elif self.min is not None:
            return self.min < rolls
        elif self.max is not None:
            return self.max > rolls
        else:
            return rolls


class Roll(object):

    def __init__(self, pool: Pool, agg: Aggregator = None):
        """ combines a pool and an aggregator to produce a rolled result """
        # dummy function for aggregator
        if agg is None:
            agg = Add()

        self.pool = pool
        self.agg = agg

    def __call__(self, *args):
        return self.agg(self.pool, *args)


def histogram(rolls, title=None, xmax=None, ymax=None):
    """
    :param rolls:   one dimensional matrix to plot
    :param title:   title to put on plot and save the image as
    :param xmax:    maximum x value to use on plot
    :param ymax:    maximum y value to use on plot
    """

    if len(rolls.shape) != 1:
        rolls = np.sum(rolls, axis=1)

    plt.hist(rolls, bins=range(min(rolls), max(rolls) + 2),
             align="left", edgecolor='k', facecolor="darksalmon",
             density=True, rwidth=0.9)
    plt.axvline(np.mean(rolls), color="navy", linestyle="--", linewidth=2)
    plt.axvline(np.median(rolls), color="black", linestyle=":", linewidth=2)
    plt.legend(["mean = {:0.2f}".format(np.mean(rolls)),
                "median = {:0.0f}".format(np.median(rolls)),
                "histogram"])
    plt.ylabel("Rate of occurrence")
    plt.xlabel("Value")
    plt.xticks([x for x in range(min(rolls), max(rolls)+1)])
    plt.grid()

    if xmax is not None:
        plt.xlim([0, xmax])

    if ymax is not None:
        plt.ylim([0, ymax])

    if title is not None:
        plt.title(title)
        plt.savefig("plots/{0}.png".format(title))

    plt.show()


# now we can very quickly do monte carlo simulations on various dice rolls
if __name__ == "__main__":

    # syntax examples
    # roll = Roll(2 * D(20), Highest(1))
    # histogram(roll(1e6))

    # this doesnt work! it should!
    roll = Roll(4 * D(6), Add(Highest(3)))
    histogram(roll(1e6))

    # rolls = roll(3 * D(6, dims))
    # histogram(rolls, "3_summed_3D6", ymax=0.2)
    #
    # rolls = highest(3, roll(4 * D(6, dims)))
    # histogram(rolls, '3_highest_4D6', ymax=0.2)
    #
    # rolls = highest(1, roll(2 * D(20, dims)))
    # histogram(rolls, "highest_of_2_d20", ymax=0.2)
    #
    # rolls = lowest(1, roll(2 * D(20, dims)))
    # histogram(rolls, "lowest_of_2_d20", ymax=0.2)
    #
    # rolls = highest(3, roll(5 * D(6, dims)))
    # histogram(rolls, "3_highest_5D6", ymax=0.2)
    #
    # rolls = highest(3, roll(6 * D(6, dims)))
    # histogram(rolls, "3_highest_6D6", ymax=0.2)