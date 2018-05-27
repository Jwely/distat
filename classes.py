from typing import Union, List, Tuple
import numpy as np
from util import dist, combine_dists, median_from_dist, mean_from_dist


# Die =====================================================
class Source(object):
    pass


class Die(Source):
    """ base arbitrary die class """

    def __init__(self, sides: Union[int, List[int]]):
        """
        Accepts a single integer, or a list of integers. If given a single integer
        the die will have that many sides, 1-sides. If given a list of integers
        the die will have those sides exactly, including duplicate faces.

        Examples:
            Die(4) produces a die with faces [1,2,3,4]
            Die([0,0,0,1]) produces a die with those specific faces.

        :param sides: Integer number of sides of a standard dice, or a list of face values
        """
        self.sides = sides
        assert isinstance(sides, list) or isinstance(sides, int)

        # Use special face mapper.
        if isinstance(sides, list):
            self._faces = sides
            self._n_sides = len(sides)
            self._mapper = {i + 1: s for i, s in enumerate(self._faces)}

        # dice is standard ascending face values.
        elif isinstance(sides, int):
            self._faces = [i for i in range(1, sides + 1)]
            self._n_sides = sides
            self._mapper = None

    def __rmul__(self, other: int):
        """ defines leading integer multiplicative behavior of die """
        assert isinstance(other, int)
        return [Die(self.sides) for _ in range(other)]

    def __repr__(self):
        """representation of the die """
        if self._mapper is None:
            return f"(D{int(self._n_sides)})"
        else:
            return f"(D[{self._faces}]"

    def __call__(self, n: Union[int, float] = None):
        if n is None:
            n = 1

        # the result is a random side
        result = np.random.randint(1, self._n_sides + 1, int(n))

        # map the result to the actual sides if needed
        if self._mapper is not None:
            print(self._mapper)
            result = np.vectorize(self._mapper.get)(result)

        if n == 1:
            result.reshape(1, 1)

        return result


class D(Die):
    """ shorthand vernacularly named class """
    pass


# Filters =================================================
class Filter(object):

    def __call__(self, arr: np.array):
        pass


class All(Filter):

    def __call__(self, arr: np.array):
        return arr


class Position(Filter):
    """ positional"""
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


class Highest(Filter):

    def __init__(self, n: int = None):

        self.n = n

    def __call__(self, arr: np.array):
        rolls = np.sort(arr)
        return rolls[:, -self.n:]


class Lowest(Filter):

    def __init__(self, n: int = None):
        self.n = n

    def __call__(self, arr: np.array):
        result = np.sort(arr)
        return result[:, :self.n]


# Selectors are 1 dimensional =============================
class Selector(object):
    """
    Selectors do not produce an output of a predictable dimension,
    and thus really only work for 1d -> 1d
    """
    def __call__(self, arr: np.array):
        return arr


class EqualTo(Selector):

    def __init__(self, values: Union[int, List[int]]):
        self.values = values

    def __call__(self, arr: np.array):
        result = np.isin(arr, self.values)
        return result


class LessThan(Selector):

    def __init__(self, less_than: int):
        self.less_than = less_than

    def __call__(self, arr: np.array):
        return arr < self.less_than


class GreaterThan(Selector):

    def __init__(self, greater_than: int):
        self.greater_than = greater_than

    def __call__(self, arr: np.array):
        return arr > self.greater_than


# Aggregator  =============================================
class Aggregator(object):

    def __init__(self, ops: Union[Selector, Filter, List[Union[Selector, Filter]]] = None):

        if ops is None:
            ops = [All()]

        if not isinstance(ops, list):
            ops = [ops]

        assert isinstance(ops, list)
        if isinstance(ops, list):  # should always be true now
            for op in ops:
                assert isinstance(op, Selector) or isinstance(op, Filter)

        self.ops = ops

    def _single_selector(self):

        if len(self.ops) == 1:
            if isinstance(self.ops[0], Selector):
                return True
        return False

    def _dual_selector(self):

        if len(self.ops) == 2:
            if all([isinstance(o, Selector) for o in self.ops]):
                return True
        return False

    def _single_filter(self):
        if len(self.ops) == 1:
            if isinstance(self.ops[0], Filter):
                return True
        return False

    def _dual_filter(self):

        if len(self.ops) == 2:
            if all([isinstance(o, Filter) for o in self.ops]):
                return True
        return False

    def _op(self, arr: np.array):

        if self._single_selector():
            selection = self.ops[0](arr)
            return arr[selection]

        elif self._dual_selector():
            return [arr[o(arr)] for o in self.ops]

        elif self._single_filter():
            return self.ops[0](arr)

        elif self._dual_filter():
            return [o(arr) for o in self.ops]

        else:
            return arr

    def __call__(self, arr: np.array):
        pass


class Sum(Aggregator):

    def __call__(self, arr: np.array):

        result = self._op(arr)
        if self._dual_filter():
            result = np.hstack((result[0], result[1]))
        elif self._dual_selector():
            result = np.sum(result)

        if len(result.shape) > 1:
            return np.sum(result, axis=1)
        else:
            print("TODO: is this a desireable case for Sum?")
            return arr


class Difference(Aggregator):

    def __init__(self, ops):
        super().__init__(ops)

        assert self._dual_selector() or self._dual_filter()

    def __call__(self, arr: np.array):

        result = self._op(arr)
        first = result[0]
        second = result[1]
        return first - second


# Conditional Actions =====================================
class Action(object):

    def __call__(self, arr: np.array, source: Die):
        pass


class ReRoll(Action):

    def __init__(self, selector: Union[Selector, List[Selector]]):
        self.selector = selector

    def select(self, arr: np.array):

        if isinstance(self.selector, list):
            selections = [s(arr) for s in self.selector]
            selection = np.sum(selections)

        elif isinstance(self.selector, Selector):
            selection = self.selector(arr)

        else:
            raise Exception("what?")

        return selection

    def __call__(self, arr: np.array, source: Die):
        selected = self.select(arr)

        n_rerolls = sum(selected)
        if n_rerolls > 0:
            rerolls = source(n_rerolls)
            arr[selected] = rerolls
        return arr


# RollDef =================================================
class RollDef_(Source):
    pass


Operation = Union[Selector, Filter, Aggregator, Action]


class RollDef(RollDef_):
    """
    chains all the things together
    """
    def __init__(self,
                 source: Union[Source, List[Source]],
                 ops: Union[Operation, List[Operation]],
                 name: str = None,
                 desc: str = None,
                 verbose: bool = False):

        if not isinstance(ops, list):
            ops = [ops]

        self.source = source
        self.ops = ops
        self.name = name
        self.desc = desc
        self.verbose = verbose

    def __rmul__(self, other: int):
        """ defines leading integer multiplicative behavior of a roll definition """
        assert isinstance(other, int)
        return [RollDef(self.source, self.ops) for _ in range(other)]

    def _sources(self, n: int = None):
        if isinstance(self.source, list):
            rolls = [s(n) for s in self.source]
            stack = np.column_stack(rolls)
            return stack
        else:
            return self.source(n)

    def __call__(self, n: int = None):

        if n is None:
            n = 1

        # initialize by calling first arg, which should be a source!
        result = self._sources(n)

        if self.verbose:
            print("source", result, result.shape)

        for op in self.ops:

            if isinstance(op, Action):
                result = op(result, self.source)

                if self.verbose:
                    print(op, '\n', result, result.shape)

            elif isinstance(op, Aggregator):
                result = op(result)

                if self.verbose:
                    print(op, '\n', result, result.shape)

            elif isinstance(op, Filter):
                result = op(result)

                if self.verbose:
                    print(op, '\n', result, result.shape)

        return result

    def dist(self, n: Union[int, float] = None):
        """ creates a Dist object from this rolldef """
        return Dist.calc(rolldef=self, n=n)


# Result storage and viz ==================================
class Dist(object):

    def __init__(self,
                 values: np.array,
                 bins: np.array,
                 rolldef: RollDef,
                 mean: float = None,
                 median: float = None,
                 n: int = None):
        """
        Stores the values of a rolldef distribution calculation.

        :param values:
        :param bins:
        :param rolldef:
        :param n:
        """

        self.values = values
        self.bins = bins
        self.rolldef = rolldef
        self.mean = mean
        self.median = median
        self.n = n

    def __call__(self, n: int = None):
        """ relay underlying rolldef calls """
        return self.rolldef(n)

    def add_accuracy(self, n: Union[int, float]) -> Tuple[np.array, np.array]:
        """
        Add additional simulations of the rolldef, updates
        the 'values', 'bins', and 'n', attributes of this class instance.
        """
        added_rolls = self.rolldef(n)
        added_vals, added_bins = dist(added_rolls)
        new_values, new_bins = \
            combine_dists(self.values, self.bins, self.n, added_vals, added_bins, n)

        # update all the attributes to include increased 'n' sims
        self.values = new_values
        self.bins = new_bins
        self.median = median_from_dist(new_values, new_bins)
        self.mean = mean_from_dist(new_values, new_bins)
        self.n = self.n + n
        return self.values, self.bins

    @classmethod
    def calc(cls, rolldef: RollDef, n: Union[int, float] = None):
        """ instantiates from a rolldef and a number of times to roll for histogram """
        if n is None:
            n = 1e6

        rolls = rolldef(n)
        values, bins = dist(rolls)
        return cls(values=values, bins=bins, rolldef=rolldef,
                   mean=np.mean(rolls), median=np.median(rolls), n=n)


if __name__ == "__main__":

    rd = RollDef(
        RollDef(
            4 * RollDef(
                D(6),
                ReRoll(
                    EqualTo(1)
                )
            ),
            Sum(
                Highest(3),
            ),
        ),
        ReRoll(LessThan(15))
    ).dist(5e4)

    dists = [(rd.n, (rd.values, rd.bins))]
    for i in range(10):
        dists.append((rd.n, rd.add_accuracy(5e4)))

    print(dists)


