from typing import List, Union, Callable
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


__author__ = 'Jwely'


class Modifier(object):

    def __init__(self, mod: int = None):
        if mod is None:
            mod = 0
        self.mod = mod

    def __call__(self, arr: np.array):
        return arr + self.mod


class Die(object):

    def __init__(self, sides: int):
        self.sides = sides

    def __repr__(self):
        """representation of the die """
        return f"D{int(self.sides)}"

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

    def __add__(self, other):
        if isinstance(other, Die):
            return Pool([self, other])
        elif isinstance(other, Pool):
            return Pool + other


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
            return Pool(self.dice + [other])

    def __repr__(self):
        """representation of the pool"""
        return "[{}]".format(', '.join([d.__repr__() for d in self.dice]))


class _Op(object):
    """ workaround for typehinting quirk? """

    def __call__(self, arr: np.array):
        return arr


class _Aggregator(object):
    """workaround for typhinting quirk?"""

    def __call__(self, arr: np.array):
        return arr


class Op(_Op):

    def __sub__(self, other):
        def sub(arr: np.array):
            print(self.__class__.__name__, "sub")
            return self(arr) - other(arr)
        return sub

    def __neg__(self):
        def neg(arr: np.array):
            print(self.__class__.__name__, "neg")
            return - self(arr)

        return neg

    def __add__(self, other: Union[int, np.array, _Op, _Aggregator]):
        def add(_other):
            print(self.__class__.__name__, "add")
            if isinstance(_other, _Op) or isinstance(_other, _Aggregator):
                return _other()
            else:
                return np.sum(_other, axis=1)
        return add

    def __pos__(self, other):
        print(self.__class__.__name__, "pos")
        return self.__add__(other)


class Aggregator(_Aggregator):

    def __init__(self,
                 ops: Union[
                     List[Callable[[np.array], np.array]],
                     Op]
                 ):
        if isinstance(ops, list):
            self.ops = ops
        elif isinstance(ops, Aggregator):
            self.ops = ops.ops
        elif isinstance(ops, Op):
            self.ops = [ops]

    def __call__(self, arr: np.array):
        """ chains the list of operations """

        result = arr
        for op in self.ops:
            result = op(result)

        return result

    def __sub__(self, other):
        def sub(arr: np.array):
            print(self.__class__.__name__, "sub")
            return self(arr) - other(arr)
        return sub

    def __add__(self, other: Union[int, np.array, _Op, _Aggregator]):
        def add(_other):
            print(self.__class__.__name__, "add")
            if isinstance(_other, _Op) or isinstance(_other, _Aggregator):
                return _other()
            else:
                return np.sum(_other, axis=1)
        return add


class _Sum(object):

    def __call__(self, arr: np.array):
        print(self.__class__.__name__, arr.shape)
        if len(arr.shape) > 1:
            return np.sum(arr, axis=1)
        else:
            return arr


class Sum(Aggregator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ops += [_Sum()]
        print(self.ops)


class Highest(Op):

    def __init__(self, n: int = None):

        self.n = n

    def __call__(self, arr: np.array):
        print(self.__class__.__name__, arr.shape)
        rolls = np.sort(arr)
        return rolls[:, -self.n:]


class Lowest(Op):
    def __init__(self, n: int = None):
        self.n = n

    def __call__(self, arr: np.array):
        print(self.__class__.__name__, arr.shape)
        rolls = np.sort(arr)
        return rolls[:, :self.n]


class Pos(Op):
    def __init__(self, *args):

        self._ndims = len(args)

        if self._ndims > 1:
            self.slice = slice(*args)
        else:
            self.slice = args[0]

        print(self.slice)

    def __call__(self, arr: np.array):
        print(self.__class__.__name__)
        result = arr[:, self.slice]
        if self._ndims == 1:
            return result.reshape(-1,1)
        else:
            return result


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

    def __init__(self, pool: Pool, agg: Aggregator = None, mod: Modifier = None):
        """ combines a pool and an aggregator to produce a rolled result """
        # dummy function for aggregator
        if agg is None:
            agg = Op()

        if mod is None:
            mod = Modifier(0)

        self.pool = pool
        self.agg = agg
        self.mod = mod

        print(self.pool)

    def __call__(self, *args):
        p = self.pool(*args)
        b = self.agg(p)
        c = self.mod(b)
        print(p)
        print(b)
        print(c)
        return c


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
    pass
    # syntax examples
    # roll = Roll(2 * D(20), Lowest(1), Modifier(0))
    # histogram(roll(1e6))

    #roll = Roll(4 * D(6), Highest(3))
    #roll = Roll(3 * D(6))
    #histogram(roll(1e6))

    #roll = Roll(4 * D(6), Sum(Highest(2)) - Sum(Lowest(2)))
    #r = roll(1e6)
    #histogram(r)
