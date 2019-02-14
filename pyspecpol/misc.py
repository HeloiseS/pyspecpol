"""
13 - Feb - 2019 / H.F. Stevance / hfstevance@gmail.com

T'is only the beginning
"""

import sys
import numpy as np
import warnings
import pandas as pd
from .utils.errors import _warn_if_list

if sys.version_info.major < 3:
    range = xrange
    input = raw_input


### PolData Object ###

class PolData(object):
    # TODO: Give it a __add__, __sub__, __truediv__, etc...
    # TODO: plotting methods??
    # TODO: ISP related methods??

    def __init__(self, filename=None):
        if filename is not None:
            self.load_file(filename)

        if filename is None:
            self.wl, self.time = False, False
            self.p, self.dp, self.q, self.dq, self.u, self.du, self.pa, self.dpa = False, False, \
                                                                                   False, False, \
                                                                                   False, False, \
                                                                                   False, False

    def load_file(self, filename, force=False, **kwargs):

    # TODO: check the file exists and create test for the case in which it doesn't
    # TODO: Check I can read a dataframe type file that has indexes
    # TODO: Check whether I can read file that has no column headers

        """
        Loads data from a data file. Default separator is comma.

        Notes
        ------
        1) Accepts same **kwargs as pandas.read_csv()

        2) The column names are what the function uses to fill things in the right place.

        Accepted column names:
           wl = Wavelength
           time = time
           p = Degree or polarisation
           dp = Error on p
           q =  Stokes q
           dq =  Error on Stokes q
           u =  Stokes u
           du = Error on Stokes u
           pa = Polarisation Angle
           dpa = Error on P.A.

        Parameters
        ----------
        filename : str
            path to the file to load data from
        force : bool, optional
            Whether to force laoding the data even if it might overwrite already defined attributes.
            Default is False.
        kwargs : optional
            Keyword arguments to parse to pandas.read_csv(). E.g. sep='\t'

        Returns
        -------

        """

        print("Accepted column names: \n "
              "wl = Wavelength / time = time / p = Degree or polarisation / dp = Error on p / "
              "q =  Stokes q / dq =  Error on Stokes q / u =  Stokes u / du = Error on Stokes u /"
              "pa = Polarisation Angle / dpa = Error on P.A.\n"
              "The column names are case sensitive.")


        # Here I am checking whether some attributes have already been filled.
        try:
            # If all attributes are False then they should sum to 0
            if sum(self.__dict__.values()) != 0 and not force:
                return "Some attributes already contain values and loading data from a file may " \
                       "overwrite them. If you're sure you want to do this set force=True."

        # If some attributes filled with arrays the sum is undefined, but we still don't
        # want to overwrite, so there is an exception for ValueErrors and a check for `force`
        except ValueError:
            if not force:
                return "Some attributes already contain values and loading data from a file may " \
                       "overwrite them. If you're sure you want to do this set force=True."
            if force:
                pass

        # If the code has gotten this far we actually start loading the file.

        # Reading csv with pandas
        temp_df = pd.read_csv(filename, **kwargs)

        # Not all files wil contain data for all attributes, so need exceptions.

        # WAVELENGTH
        try:
            self.wl = temp_df.wl.values
        except AttributeError:
            print("Column 'wl' not found. Ignore this if you don't have a wavelength dimension, "
                  "otherwise check your file has the right column format.")

        # TIME
        try:
            self.time = temp_df.time.values
        except AttributeError:
            print("Column 'time' not found. Ignore this if you don't have a time dimension, "
                  "otherwise check your file has the right column format. ")

        # DEGREE OF POLARISATION
        try:
            self.p = temp_df.p.values
        except AttributeError:
            print("Column 'p' not found. Ignore this if you don't have a p value, "
                  "otherwise check your file has the right column format. ")
        try:
            self.dp = temp_df.dp.values
        except AttributeError:
            print("Column 'dp' not found. Ignore this if you don't have a dp value, "
                  "otherwise check your file has the right column format. ")

        # STOKES Q
        try:
            self.q = temp_df.q.values
        except AttributeError:
            print("Column 'q' not found. Ignore this if you don't have a Stokes q value, "
                  "otherwise check your file has the right column format. ")
        try:
            self.dq = temp_df.dq.values
        except AttributeError:
            print("Column 'dq' not found. Ignore this if you don't have an error on Stokes q value,"
                  " otherwise check your file has the right column format. ")

        # STOKES U
        try:
            self.u = temp_df.u.values
        except AttributeError:
            print("Column 'u' not found. Ignore this if you don't have a Stokes u value, "
                  "otherwise check your file has the right column format. ")
        try:
            self.du = temp_df.du.values
        except AttributeError:
            print("Column 'du' not found. Ignore this if you don't have an error on Stokes u, "
                  "otherwise check your file has the right column format. ")

        # POLARISATION ANGLE
        try:
            self.pa = temp_df.pa.values
        except AttributeError:
            print("Column 'pa' not found. Ignore this if you don't have a polarisation angle value,"
                  " otherwise check your file has the right column format. ")
        try:
            self.dpa = temp_df.dpa.values
        except AttributeError:
            print("Column 'dpa' not found. Ignore this if you don't have an error on "
                  "the polarisation angle, otherwise check your file has the right column format. ")

        return "Data successfully loaded form "+filename


### CALCULATING THE DEGREE OF POLARISATION P ###
def calc_p(q, u, dq=None, du=None, debiased=True):
    """
    Calculates the degree of polarisation

    Notes
    -----
    1) You mus parse 1D numpy.ndarrays, not lists.
    # TODO: Should I let the code crash or should I more elegantly stop the function if a list is parsed?
    2) The types of the stokes parameters and their errors should be homogeneous.


    Parameters
    ----------
    q : numpy.ndarray, float or int
        Stokes parameters q
    u : numpy.ndarray, float or int
        Stokes parameters u
    dq : numpy.ndarray, float or int, optional
        Error(s) on Stokes q
    du : numpy.ndarray, float or int, optional
        Error(s) on Stokes u

    debiased : Bool, optional
        Default is True. Debiases the degree of polarisation for the bias
        using a heavy side function

    Returns
    -------
    Degree of polarisation -- if no errors given
    Tuple(Degree of polarisation, Error(s) on the degree of polarisation) -- if errors given

    Scalars or arrays are returned depending on the input type.

    """

    # Checks whether these parameters are lists and warns that calculations may fail
    _warn_if_list([q, u, dq, du])

    if dq is None and du is None:
        # if no errors are given just calculate a raw degree of polarisation
        return _pol_deg(q,u)

    elif (dq is not None and du is None) or (du is not None and dq is None):
        # if errors are missing give warning and return raw degree of pol
        warnings.warn('It seems one set of error is missing (either for q or u)\nOnly p will be '
                      + 'returned without being debiased. If this is unexpected check your input.')
        return _pol_deg(q,u)

    elif dq is not None and du is not None:
        # The intention is good but this will fail if a float and an int are parsed an that's
        # not the point
        # assert type(q) == type(dq) == type(u) == type(du), "Types of parsed data should be the same."

        p, dp = _pol_deg_and_err(q,u, dq, du)
        if debiased:
            p_debiased = debias_polarisation(p, dp)
            return p_debiased, dp

        if not debiased:
            return p, dp


def debias_polarisation(p, dp):
    """
    Function for debiasing polarisation

    Parameters
    ----------
    p : int, float or numpy.ndarray
        Degree of polarisation
    dp : int, float or numpy.ndarray
        Errors on the degree of polarisation

    Returns
    -------
    Debiased degree of polarisation (int, float or numpy.ndarray)

    """

    # The intention is good but this will fail if a float and an int are parsed and that's a pblm
    # assert type(p) == type(dp), "Polarisation and polarisation error parameters are " \
    #                              "not the same type"

    # Asking for forgiveness not permission. In most cases I expect this opperation will
    # be performed on lists or arrays of values. If single values are given a TypeError will
    # be risen and caught by the except.

    try:
        # List comprehension to replace the list or array of polarisation degree values
        # by the debiased polarisation degree.

        # Pseudo code of the list comprehension:
        # --> For a given value p, if it is greater than its associated error, then:
        # debiased_ p = p - (p_error**2 / p)
        # (See: Polarimetry of the Type IA Supernova SN 1996X -- Wang et al. (1997) -- Eq. 3)

        p = [p[i] - (dp[i]**2)/p[i] if p[i] - dp[i] > 0 else p[i] for i in range(len(p))]

    except TypeError:
        # Same logic as discribed above but for a single value.
        if p - dp > 0: p -= (dp**2)/p

    return p


def _pol_deg(q, u):
    """ Adds Stokes parameters in quadrature --  No errors """
    return np.sqrt(q * q + u * u)


def _pol_deg_and_err(q, u, dq, du):
    """ Adds Stokes parameters in quadrature and propagates errors"""
    p = _pol_deg(q,u)
    dp = (1 / p) * np.sqrt((q * dq) ** 2 + (u * du) ** 2)
    return p, dp





if __name__ == "__main__":
    print("Hello World!")
