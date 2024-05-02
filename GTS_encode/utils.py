"""Useful functions to support the encoding of mangopare sensors
- inflection_data - Identification of inflection points
- extract_upcast - Extraction of upcast measurements
- pres - conversion of depth (m) to pressure (Pa)
"""

import numpy as np
import xarray as xr
import pandas as pd
import pdb
import datetime
import os

def generate_identifier(day,hour,minute):
    first_identifier = "IOVE01"
    second_identifier = "NZKL"
    date_identifier = "".join(day,hour,minute)
    name = " ".join([first_identifier,second_identifier,date_identifier])
    return name

def break_down_wmo_id(wmo_id):
    id_series, issuer_of_identifier, issue_number, local_id = wmo_id.split('-')
    return id_series, issuer_of_identifier, issue_number, local_id

def inflection_points(data):
    """Identifies the location of the inflection points in a dataset"""
    diff = data[1:] - data[:-1]
    inflection_index = np.where(np.sign(diff[:-1]) != np.sign(diff[1:]))[0] + 1
    if len(inflection_index) == 1:
        return inflection_index
    else:
        big_changes = np.where(
            np.diff(inflection_index) > 2
        )  # to just consider non-continuos inflection points
        return inflection_index[big_changes]


def extract_upcast(ds):
    """Extracts the upcast from a dataset or dataframe with mangopare format"""
    depth = ds["DEPTH"].values
    inflection = inflection_points(depth)
    last_upcast_index = inflection[::-1][0]
    try:
        upcast = ds.isel({"DATETIME": np.arange(last_upcast_index, len(depth), 1)})
    except:
        upcast = ds.iloc[np.arange(last_upcast_index, len(depth), 1)]
    return upcast


def pres(depth, lat):
    """
    Calculates pressure in dbars from depth in meters.
    Parameters
    ----------
    depth : array_like
            depth [meters]
    lat : array_like
          latitude in decimal degrees north [-90..+90]
    Returns
    -------
    p : array_like
           pressure [db]
    Examples
    --------
    >>> import seawater as sw
    >>> depth, lat = 7321.45, 30
    >>> sw.pres(depth,lat)
    7500.0065130118019
    References
    ----------
    .. [1] Saunders, Peter M., 1981: Practical Conversion of Pressure to Depth.
       J. Phys. Oceanogr., 11, 573-574.
       doi: 10.1175/1520-0485(1981)011<0573:PCOPTD>2.0.CO;2
    """
    depth, lat = list(map(np.asanyarray, (depth, lat)))
    deg2rad = np.pi / 180.0
    X = np.sin(np.abs(lat * deg2rad))
    C1 = 5.92e-3 + X**2 * 5.25e-3
    pressure = ((1 - C1) - (((1 - C1) ** 2) - (8.84e-6 * depth)) ** 0.5) / 4.42e-6
    return pressure * 10000
