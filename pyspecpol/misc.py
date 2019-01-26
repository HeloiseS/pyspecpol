"""
26 - Jan - 2019 / H.F. Stevance / hfstevance@gmail.com

T'is only the beginning
"""

import sys
import numpy as np
import warnings


if sys.version_info.major < 3:
    range = xrange
    input = raw_input

def _warn_if_list(parameters):
    """ Checks if a (list of) parameter(s) is a list and raises a warning"""
    try:
        for param in parameters:
            if isinstance(param, list): warnings.warn(" You are parsing a list. "
                                                      "Operations on lists may fail -- use arrays.")
    except TypeError:
        if isinstance(parameters, list): warnings.warn(" You are parsing a list. "
                                                       "Operations on lists may fail -- use arrays.")


def calculate_pol_deg(q, u, dq=None, du=None, debiased = True):
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
        return  _pol_deg(q,u)

    elif (dq is not None and du is None) or (du is not None and dq is None):
        # if errors are missing give warning and return raw degree of pol
        warnings.warn('It seems one set of error is missing (either for q or u)\nOnly p will be '
                      + 'returned without being debiased. If this is unexpected check your input.')
        return  _pol_deg(q,u)

    elif dq is not None and du is not None:
        # The intention is good but this will fail if a float and an int are parsed an that's
        # not the point
        # assert type(q) == type(dq) == type(u) == type(du), "Types of parsed data should be the same."

        p, dp =  _pol_deg_and_err(q,u, dq, du)
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
                               # "not the same type"


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
