import pyspecpol.misc as polmisc
import numpy as np


class TestPolData(object):
    def test_blank_init(self):
        # checking basic instanciation of a PolData object
        poldata = polmisc.PolData()
        assert isinstance(poldata, polmisc.PolData)

    def test_init_from_file(self):
        # Checking that I can load the data file correctly
        poldata = polmisc.PolData('poldata.csv')

        assert isinstance(poldata, polmisc.PolData)

        assert poldata.wl[0] == 4000 and poldata.p[0]== 1.0 and poldata.dp[0]  == 0.0 and\
        poldata.q[0] == 1.0 and poldata.dq[0] == 0.0 and poldata.u[0] == 1.0 and poldata.du[0] == 0.0\
        and poldata.pa[0] == 45 and poldata.dpa[0] == 0.0, 'The file has not been read correctly'

    def test_init_from_file_force(self):
        # Checking that the `force` parameter does its job

        # First I instantiate the object and fill in some values
        poldata = polmisc.PolData()
        poldata.wl, poldata.p = np.array([3000,3500]), np.array([3,3.5])

        # Then I try to load the file without `force = True` and check values are unchanged
        poldata.load_file('poldata.csv')
        assert poldata.wl[0] == 3000 and poldata.p[0] == 3, "Values shouldn't have changed!"

        # Then I add in `force=True` and check everything has updated.
        poldata.load_file('poldata.csv', force=True)
        assert poldata.wl[0] == 4000 and poldata.p[0] == 1.0, "Values should be the same as in file"





class TestDegreeOfPolarisation(object):
    def test_pol_deg(self):
           # Checks single Values
           assert polmisc._pol_deg(2, 0) == 2, "Can't combine single values."

           # Checks values given in array
           p_arr = polmisc._pol_deg(np.array([2,2,2]), np.array([1,1,1]))
           # if all 3 values of the arrays are right, I'll get 3 True values, which I sum (giving 3)
           assert np.sum(np.isclose(p_arr, np.array([ 2.23606798,  2.23606798,  2.23606798]))) == 3, \
                  "Can't combine arrays "

    def test_pol_deg_error(self):
           # Checks single values
           p, dp = polmisc._pol_deg_and_err(1,1,0.5,0.5)
           assert np.isclose(p, 1.41421356) , "Adding single values, p wrong."
           assert np.isclose(dp, 0.5) , "Adding single values, delta_p wrong."

           # Checks values in array
           p, dp = polmisc._pol_deg_and_err(q = np.array([1.,2.,1.]),
                                            u = np.array([1.,2.,1.]),
                                            dq = np.array([0.5, 0.5, 0.5]),
                                            du = np.array([0.25, 0.25, 0.25]))
           assert np.sum(np.isclose(p, np.array([ 1.41421356,  2.82842712,  1.41421356]))) == 3, \
                         "Combining arrays, polarisation degree is wrong."
           assert np.sum(np.isclose(dp, np.array([ 0.39528471,  0.39528471,  0.39528471]))) == 3, \
                  "Combining arrays, error on degree of polarisation is wrong."

    def test_debias_polarisation(self):
           # Checks single values
           debiased_p = polmisc.debias_polarisation(2,1)
           assert debiased_p == 1.5, "Debiasing single value. Wrong."

           # Check list of values
           debiased_p_list = polmisc.debias_polarisation([2.,2.,2.], [1.,2.,1.])
           assert debiased_p_list == [1.5, 2., 1.5], "Debiasing list of values. Wrong."

           # Checks numpy.ndarray
           debiased_p_list = polmisc.debias_polarisation(np.array([2.,2.,2.]),
                                                         np.array([1.,2.,1.]))
           assert debiased_p_list == [1.5, 2., 1.5], "Debiasing numpy.ndarray of values. Wrong."

    def test_calculate_pol_deg(self):
        #### Inputs: Scalars

        # Without errors
        p = polmisc.calc_p(2, 3)
        assert np.isclose(p, 3.605551275463), "Calculating p from scalars. No errors. Wrong."

        # With errors, debiased
        p, dp = polmisc.calc_p(2, 3, 0.5, 0.7)
        assert np.isclose(p, 3.4901309654032779 ), "Calculating p from scalars with errors and debiased." \
                                                  "Wrong. "
        assert np.isclose(dp,0.64509987300715388), "Calculating dp from scalars with errors and " \
                                                   "debiased. Wrong. "
        # With errors, NOT debiased
        p, dp = polmisc.calc_p(2, 3, 0.5, 0.7, debiased=False)
        assert np.isclose(p, 3.6055512754639891), "Calculating p from scalars with errors and " \
                                                  "NOT debiased. Wrong."
        assert np.isclose(dp,0.64509987300715388), "Calculating dp from scalars with errors and " \
                                                   "NOT debiased. Wrong. "

        #### Inputs: Arrays

        # Without errors
        p = polmisc.calc_p(q = np.array([1, 2, 3]),
                           u = np.array([1,2,3]))

        assert np.sum(np.isclose(p, np.array([1.41421356,  2.82842712,  4.24264069]))) == 3, \
                "Combining arrays and NOT debiasing, p is wrong."

        # With errors, debiased
        p, dp = polmisc.calc_p(q = np.array([1, 2, 3]),
                               u = np.array([1,2,3]),
                               dq = np.array([.8,1.2,.5]),
                               du = np.array([.1,.2,.3])
                               )
        assert np.sum(np.isclose(p, np.array([1.1844038, 2.5667976, 4.20257130]))) == 3, \
                "Combining arrays and debiasing, p is wrong."
        assert np.sum(np.isclose(dp, np.array([ 0.57008771,  0.86023253,  0.41231056]))) == 3, \
                "Combining arrays and debiasing, dp is wrong"

        # With errors, NOT debiased
        p, dp = polmisc.calc_p(q = np.array([1, 2, 3]),
                               u = np.array([1,2,3]),
                               dq = np.array([.8,1.2,.5]),
                               du = np.array([.1,.2,.3]),
                               debiased = False)

        assert np.sum(np.isclose(p, np.array([1.41421356,  2.82842712,  4.24264069]))) == 3, \
                "Combining arrays and NOT debiasing, p is wrong."
        assert np.sum(np.isclose(dp, np.array([ 0.57008771,  0.86023253,  0.41231056]))) == 3, \
                "Combining arrays and NOT debiasing, dp is wrong"
