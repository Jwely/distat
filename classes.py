from typing import List, Union, Callable

import matplotlib
import numpy as np

from bases import Die_, Rule_, Selector_, Aggregator_, Sum_

matplotlib.use('TkAgg')

__author__ = 'Jwely'
__all__ = [
    "Modifier",
    "Die",
    "D",
    "Maximize",
    "Reroll",
    "Pool",
    "Selector",
    "Aggregator",
    "Sum",
    "Highest",
    "Lowest",
    "Pos",
    "RollDef"
]


class Modifier(object):

    def __init__(self, mod: int = None):
        if mod is None:
            mod = 0
        self.mod = mod

    def __call__(self, arr: np.array):
        return arr + self.mod


class Die(Die_):

    def __init__(self, sides: int, rule: Rule_ = None):
        """

        :param sides: number of sides on the dice
        :param rule: rule to apply, such as reroll 1's one time Reroll(1)
        """
        if rule is None:
            rule = Rule_()

        self.rule = rule
        self.sides = sides

    def __repr__(self):
        """representation of the die """
        return f"(D{int(self.sides)}: {self.rule})"

    def _roll(self, n: Union[int, float] = None):
        if n is None:
            n = 1

        result = np.random.randint(1, self.sides + 1, int(n))

        if n == 1:
            result.reshape(1, 1)

        return result

    # TODO: inconsistent with other classes to not use __call__
    # TODO: Is .roll() more readable? could the others be more readable too?
    # TODO: Pool class also uses .roll()
    def roll(self, n:  Union[int, float] = None):
        """ number of dice rolled decided when called """
        result = self._roll(n)
        return self.rule(result, self)

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
    """ shorthand vernacularly named class """
    pass


class Maximize(Rule_):
    """ maximizes the roll on the die, setting all results to the number of sides"""
    # TODO: probably useless. but helps for very simple tests!
    def __call__(self, result: np.array, die: Die):
        result = result * 0 + die.sides
        return result


class Reroll(Rule_):
    def __init__(self,
                 values: Union[int, List[int]] = None,
                 less_than: int = None,
                 greater_than: int = None,
                 n_allowed: int = 1):
        """

        :param values: individual values on the dice to reroll
        :param n_allowed: number of rerolls to allow, defaults to one.
        """
        # takes exactly one argument
        assert any([arg is not None for arg in [values, less_than, greater_than]])

        if isinstance(values, int):
            values = [values]

        self.values = values
        self.less_than = less_than
        self.greater_than = greater_than
        self.n_allowed = n_allowed

    def __call__(self, result: np.array, die: Die):
        """
        examines results for values that meet the reroll criteria,
        then replaces the numbers with new rolls. Executes up to
        self.n_allowed times.

        :param result:
        :param die:
        :param _n:
        :return:
        """
        _n = 0

        # TODO: Significantly increases compute time! can indexing be more efficient?
        while _n < self.n_allowed:
            reroll_indexer = np.zeros(result.shape).astype(bool)

            # add to the indexer based on each logical check
            if self.values is not None:
                reroll_indexer += np.isin(result, self.values)

            if self.less_than is not None:
                reroll_indexer += result < self.less_than

            if self.greater_than is not None:
                reroll_indexer += result > self.greater_than

            n_rerolls = sum(reroll_indexer)
            if n_rerolls > 0:
                rerolls = die._roll(n_rerolls)
                result[reroll_indexer] = rerolls

            _n += 1

        return result

    def __repr__(self):
        if self.values is not None:
            return f"reroll {self.values}"
        if self.less_than is not None:
            return f"reroll < {self.less_than}"
        if self.greater_than is not None:
            return f"reroll > {self.greater_than}"


class Pool(object):

    def __init__(self, dice: List[Die]):
        """ A simple collection of multiple dice """
        self.dice = dice

    def roll(self, *args):
        rolls = [d.roll(*args) for d in self.dice]
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


class Selector(Selector_):
    """
    Defines base behavior for chaining multiple
    operations together
    """
    def __sub__(self, other):
        def sub(arr: np.array):
            return self(arr) - other(arr)
        return sub

    def __neg__(self):
        def neg(arr: np.array):
            return - self(arr)

        return neg

    def __add__(self, other: Union[int, np.array, Selector_, Aggregator_]):
        def add(_other):
            if isinstance(_other, Selector_) or isinstance(_other, Aggregator_):
                return _other()
            else:
                return np.sum(_other, axis=1)
        return add

    def __pos__(self, other):
        return self.__add__(other)


class Aggregator(Aggregator_):

    def __init__(self,
                 ops: Union[
                     List[Callable[[np.array], np.array]],
                     Selector]
                 ):
        if isinstance(ops, list):
            self.ops = ops
        elif isinstance(ops, Aggregator):
            self.ops = ops.ops
        elif isinstance(ops, Selector):
            self.ops = [ops]

    def __call__(self, arr: np.array):
        """ chains the list of operations """

        result = arr
        for op in self.ops:
            result = op(result)

        return result

    def __sub__(self, other):
        def sub(arr: np.array):
            return self(arr) - other(arr)
        return sub

    def __add__(self, other: Union[int, np.array, Selector_, Aggregator_]):
        def add(_other):
            if isinstance(_other, Selector_) or isinstance(_other, Aggregator_):
                return _other()
            else:
                return np.sum(_other, axis=1)
        return add


# def Sum(agg: Aggregator):
#     agg.ops += [Sum_()]
#     return agg

class Sum(Aggregator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not isinstance(self.ops[-1], Sum_):
            self.ops += [Sum_()]


class Highest(Selector):

    def __init__(self, n: int = None):

        self.n = n

    def __call__(self, arr: np.array):
        rolls = np.sort(arr)
        return rolls[:, -self.n:]


class Lowest(Selector):
    def __init__(self, n: int = None):
        self.n = n

    def __call__(self, arr: np.array):
        rolls = np.sort(arr)
        return rolls[:, :self.n]


class Pos(Selector):
    def __init__(self, *args):
        """
        a position operator selects dice by simple index position
        the arguments are as those of a slice object.
        """
        self._ndims = len(args)

        if self._ndims > 1:
            self.slice = slice(*args)
        else:
            self.slice = args[0]

    def __call__(self, arr: np.array):
        result = arr[:, self.slice]
        if self._ndims == 1:
            return result.reshape(-1, 1)
        else:
            return result


class RollDef(object):
    """
    Defines a Roll of the dice, including the pool of dice to be thrown,
    the way to aggregate those dice, and modifiers to apply to the roll.

    Instantiating a RollDef just defines the roll, to get results use
    the __call__ method via

        RollDef()   # computes the roll just one time.
        RollDef(n)  # computes the roll "n" times (useful for monte-carlo simulation)

    Using an "n" value of 1e6 is much less than 1s to compute in most cases.
    """
    def __init__(self,
                 pool: Union[Pool, Die],
                 agg: Aggregator = None,
                 mod: Modifier = None,
                 name: str = None,
                 desc: str = None):
        """
        :param pool: A Pool instance or a single Die
        :param agg: An Aggregator instance, defaults to pass through Op()
        :param mod: A Modifier instance, defaults to Modifier(0)
        :param name: Special name to give to this roll definition
        :param desc: Full description to give to this roll definition
        """
        # dummy function for aggregator
        if agg is None:
            agg = Selector()

        if mod is None:
            mod = Modifier(0)

        self.pool = pool
        self.agg = agg
        self.mod = mod

        self.name = name
        self.desc = desc

    def __call__(self, *args):
        pooled = self.pool.roll(*args)
        aggregated = self.agg(pooled)
        modified = self.mod(aggregated)
        return modified


