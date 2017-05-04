__author__ = 'Jwely'

import numpy
import matplotlib.pyplot as plt

class D(object):
    """
    Simple dice class that allows more natural syntax for rolling dice

    for example
        4*D(6) will return a list of 4 dice objects

    :param sides:   number of sides on die
    :param dim      size of the array, for when parallel sets of rolls are desired
    """

    def __init__(self, sides, dim=None):
        self.sides = sides
        if dim is not None:
            self.dim = int(dim)
        else:
            self.dim = 1

    def __rmul__(self, other):
        """ defines leading integer multiplicative behavior of die """

        if isinstance(other, int):
            return [D(self.sides, self.dim) for i in range(other)]
        elif isinstance(other, float):
            return [D(self.sides, self.dim) for i in range(int(other))]
        else:
            raise Exception("Can only have integer numbers of die")

    def roll(self):
        return numpy.random.randint(1, self.sides + 1, self.dim)


def highest(num, rolls):
    """ returns the highest "num" of dice from rolls matrix """
    ordered = numpy.sort(rolls)
    return ordered[:, -num:]


def lowest(num, rolls):
    """ returns the lowest 'num' of dice from rolls matrix """
    ordered = numpy.sort(rolls)
    return ordered[:, :num]


def bestof(n_best, n_pool):
    pass


def roll(dice):
    """
    :param dice:    list containing D objects and/or constants
    :return:        A roll matrix, depending on the dim of input D
    """

    dim = [item.dim for item in dice if isinstance(item, D)]
    if len(list(set(dim))) > 1:
        raise Exception("dice must have same dimensions")

    out = numpy.ndarray((int(dim[0]), len(dice)), dtype="int")

    for i, item in enumerate(dice):
        if isinstance(item, D):
            out[:, i] = item.roll()
        elif isinstance(item, int):
            out[:, i] = numpy.ndarray(len(dice)) + item

    return out


def histogram(rolls, title=None, xmax=None, ymax=None):
    """
    :param rolls:   one dimensional matrix to plot
    :param title:   title to put on plot and save the image as
    :param xmax:    maximum x value to use on plot
    :param ymax:    maximum y value to use on plot
    """

    if len(rolls.shape) != 1:
        rolls = numpy.sum(rolls, axis=1)

    plt.hist(rolls, bins=range(min(rolls), max(rolls) + 2),
             align="left", edgecolor='k', facecolor="darksalmon",
             normed=True, rwidth=0.9)
    plt.axvline(numpy.mean(rolls), color="navy", linestyle="--", linewidth=2)
    plt.axvline(numpy.median(rolls), color="black", linestyle=":", linewidth=2)
    plt.legend(["mean = {:0.2f}".format(numpy.mean(rolls)),
                "median = {:0.0f}".format(numpy.median(rolls)),
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
        plt.savefig("{0}.png".format(title))

    plt.show()


# now we can very quickly do monte carlo simulations on various dice rolls
if __name__ == "__main__":

    dims = 1e7

    # syntax examples
    rolls = roll(3 * D(6, dims))
    histogram(rolls, "3_summed_3D6", ymax=0.2)

    rolls = highest(3, roll(4 * D(6, dims)))
    histogram(rolls, '3_highest_4D6', ymax=0.2)

    rolls = highest(1, roll(2 * D(20, dims)))
    histogram(rolls, "highest_of_2_d20", ymax=0.2)

    rolls = lowest(1, roll(2 * D(20, dims)))
    histogram(rolls, "lowest_of_2_d20", ymax=0.2)

    rolls = highest(3, roll(5 * D(6, dims)))
    histogram(rolls, "3_highest_5D6", ymax=0.2)

    rolls = highest(3, roll(6 * D(6, dims)))
    histogram(rolls, "3_highest_6D6", ymax=0.2)