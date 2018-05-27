from typing import List, Union, Dict, Tuple
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

from classes import Dist, RollDef


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
    plt.xticks([x for x in range(min(rolls), max(rolls) + 1)])
    plt.grid()

    if xmax is not None:
        plt.xlim([0, xmax])

    if ymax is not None:
        plt.ylim([0, ymax])

    if title is not None:
        plt.title(title)
        plt.savefig("plots/{0}.png".format(title))

    plt.show()


class RollDefDashboard(object):
    """ A visualization that summarizes multiple rolldefs"""
    def __init__(self, dists: List[Dist]):

        self.dists = dists

        self._fig = plt.figure(figsize=(20, 12))
        self._grid = plt.GridSpec(12, 2, hspace=.8, wspace=0.5,
                                  top=0.95, bottom=0.05, left=0.05, right=0.95)

        self._hist_ax = self.__hist_ax()
        self._mean_ax = self.__mean_ax()
        self._median_ax = self.__median_ax()
        self._cum_ax = self.__cum_ax()
        self._table_ax = self.__table_ax()

    @classmethod
    def from_rolldefs(self, rolldefs: List[RollDef], n: Union[int, float] = None):
        return RollDefDashboard(dists=[rd.dist(n) for rd in rolldefs])

    def show(self):
        self._pop_hist_ax()
        self._pop_mean_ax()
        self._pop_median_ax()
        self._pop_cum_ax()
        plt.show()

    def __hist_ax(self):
        hist_ax = self._fig.add_subplot(self._grid[:4, 0])
        hist_ax.set_xticks(self.get_x_ticks())
        return hist_ax

    def __mean_ax(self):
        mean_ax = self._fig.add_subplot(self._grid[4:6, 0], sharex=self._hist_ax)
        mean_ax.xaxis.set_visible(False)
        return mean_ax

    def __median_ax(self):
        median_ax = self._fig.add_subplot(self._grid[6:8, 0], sharex=self._hist_ax)
        median_ax.xaxis.set_visible(False)
        return median_ax

    def __cum_ax(self):
        cum_ax = self._fig.add_subplot(self._grid[8:, 0], sharex=self._hist_ax)
        cum_ax.set_xticks(self.get_x_ticks())
        return cum_ax

    def __table_ax(self):
        table_ax = self._fig.add_subplot(self._grid[:, 1])
        return table_ax

    def _pop_hist_ax(self):

        names = self.names()
        colors = self.color_dict().values()
        dists = self.dists_dict().values()
        ax = self._hist_ax

        for n, c, d in zip(names, colors, dists):
            ax.plot(
                d.bins[:-1],
                d.values,
                color=c,
                label=n,
                linewidth=2)
        ax.yaxis.grid()
        ax.set_ylim(0, None)
        ax.legend()
        ax.set_ylabel('Distribution')

    def _pop_mean_ax(self):
        names = self.names()
        colors = self.color_dict().values()
        means = self.means_dict().values()
        ax = self._mean_ax

        for n, c, m in zip(names, colors, means):
            ax.axvline(m, color=c, linewidth=2)

        ax.set_ylabel("Mean")
        ax.legend(means)

    def _pop_median_ax(self):
        names = self.names()
        colors = self.color_dict().values()
        medians = self.medians_dict().values()
        ax = self._median_ax

        for n, c, m in zip(names, colors, medians):
            ax.axvline(m, color=c, linewidth=2, linestyle=':')

        ax.set_ylabel("Median")
        ax.legend(medians)

    def _pop_cum_ax(self):
        names = self.names()
        colors = self.color_dict().values()
        dists = self.dists_dict().values()
        ax = self._cum_ax
        for n, c, d in zip(names, colors, dists):
            ax.plot(
                d.bins[:-1],
                np.cumsum(d.values),
                color=c,
                label=n,
                linewidth=2)
        ax.yaxis.grid()
        ax.set_ylim(0, None)
        ax.legend()
        ax.set_ylabel("Cumulative")

    def names(self):
        return [d.rolldef.name for d in self.dists]
    
    def color_dict(self):
        colors = sns.hls_palette(len(self.dists))
        color_dict = {d.rolldef.name: c for d, c in zip(self.dists, colors)}
        return color_dict

    def get_x_ticks(self):
        all = np.hstack([d.bins for d in self.dists])
        return np.unique(all)

    def get_x_range(self):
        ticks = self.get_x_ticks()
        return min(ticks), max(ticks)

    def add_accuracy(self, n: int):
        """ iteratively adds accuracy to all underlying distributions """
        for d in self.dists:
            d.add_accuracy(n)

    def dists_dict(self) -> Dict[str, Tuple[np.array, np.array]]:
        """ returns a dict of the distributions """
        dists_dict = {d.rolldef.name: d for d in self.dists}
        return dists_dict

    def means_dict(self) -> Dict[str, float]:
        """ returns dict of mean values"""
        mean_dict = {d.rolldef.name: d.mean for d in self.dists}
        return mean_dict

    def medians_dict(self) -> Dict[str, float]:
        """ returns dict of median values """
        median_dict = {d.rolldef.name: d.median for d in self.dists}
        return median_dict