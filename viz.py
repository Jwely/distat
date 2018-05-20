from typing import Tuple

import numpy as np
from matplotlib import pyplot as plt


def dist(rolls: np.array) -> Tuple[np.array, np.array]:
    """ Computes the distribution of a rolls result"""
    hist = np.histogram(
        a=rolls,
        bins=range(min(rolls), max(rolls) + 2),
        density=True)

    return hist


def cumulative_dist(rolls: np.array) -> Tuple[np.array, np.array]:
    """ accumulates the distribution """
    values, bins = dist(rolls)
    return np.cumsum(values), bins


def histogram1(rolls, title=None, xmax=None, ymax=None):
    """
    :param rolls:   one dimensional matrix to plot
    :param title:   title to put on plot and save the image as
    :param xmax:    maximum x value to use on plot
    :param ymax:    maximum y value to use on plot
    """

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