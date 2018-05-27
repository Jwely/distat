import numpy as np
import pandas as pd
from typing import Tuple


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


def combine_dists(
        v1: np.array,
        b1: np.array,
        w1: int,
        v2: np.array,
        b2: np.array,
        w2: int) -> Tuple[np.array, np.array]:
    """
    Combines two distributions into one distribution.

    :param v1: values array from 1st distribution
    :param b1: bins array from 1st distribution (has length v1 + 1)
    :param w1: number of samples in the 1st distribution
    :param v2: values array from 2nd distribution
    :param b2: bins array from 2nd distribution (has length v2 + 1)
    :param w2: number of samples in the 2nd  distribution
    :return:
    """

    # we're going to use pandas for it's out of the box utility for combining
    # inteligently on shared indexes (bins in this case)

    # turn both value, bin sets into dataframes (note the padding)
    d1 = pd.DataFrame({'b': b1, 'v': np.pad(v1, (0, 1), 'constant')})
    d2 = pd.DataFrame({'b': b2, 'v': np.pad(v2, (0, 1), 'constant')})

    # merge on their bin columns, fill nulls, sort them by bins
    df = pd.merge(d1, d2, how='outer', on='b', suffixes=(1, 2))
    df.fillna(0, inplace=True)
    df = df.sort_values(by='b').set_index('b')

    # do the actual weighted average with pandas series
    v_new = ((df['v1'] * w1) + (df['v2'] * w2)) / (w1 + w2)
    b_new = df.reset_index()['b']

    # remove the last value on the value array (which is sure to be zero)
    return np.array(v_new)[:-1], np.array(b_new)


def median_from_dist(values: np.array, bins: np.array):
    """ calculates the median from a distribution """

    # the median is found by finding the first occurance where the
    # cumulative sum is greater than 0.5
    cvals = np.cumsum(values)
    median_id = np.searchsorted(cvals, 0.50)
    return bins[median_id]


def mean_from_dist(values: np.array, bins: np.array):
    """ calculates the mean from a distribution"""
    mean = np.sum(values * bins[:-1])
    return mean