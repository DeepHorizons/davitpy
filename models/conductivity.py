# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.conductivity
*********************
This module calculates ionospheric conductivities based on IRI, MSIS and IGRF profiles

**Classes**:
    * :class:`models.conductivity.Sigma`

Written by Sebastien
"""
import models as __models


class Sigma(__models.Model):
    """ This class runs and stores the Conductivity model and its results

    **Args**:
        * `date` (`datetime <http://tinyurl.com/bl352yx>`_): date and time
        * `lat` (float or iterable): latitude(s)
        * `lon` (float or iterable): longitude(s)
        * `alt` (float or iterable): altitude(s)

    **Example**:
    ::

        import datetime as dt
        date = dt.utcnow()
        self.atm = Sigma(date, 50, -80, range(100, 500, 10))

    .. note:: these collision frequencies and conductivities are approximation taken from Kelley [2000], Section 2.2

    """
    def __init__(self, date, lat, lon, alt):
        super(Sigma, self).__init__(date, lat, lon, alt)
        import models
        import numpy as np

        ## Call to IGRF
        self.mag = models.igrf.Igrf(self.date, 
            self.lat, self.lon, self.alt)

        ## Call to IRI
        self.ionos = models.iri.Iri(self.date, 
            self.lat, self.lon, self.alt)

        ## Call to MSIS
        self.atm = models.msis.Msis(self.date, 
            self.lat, self.lon, self.alt)

        # Some constants
        amu = 1.66e-27
        qe = 1.60e-19
        me = 9.11e-31
        Ahe = 4.
        Ao = 16.
        An2 = 28.
        Ao2 = 32.
        Aar = 40.
        An = 14.
        Ah = 1.

        ## Now some more calculations
        # Ion density
        # ni = self.ionos.ni['O+'] + self.ionos.ni['O2+'] + self.ionos.ni['NO+']
        ni = self.ionos.ne
        # Neutral density
        nn = self.atm.rho['He'] + self.atm.rho['O'] + \
            self.atm.rho['N2'] + self.atm.rho['O2'] + self.atm.rho['Ar']
        # ion mass (harmonic mean over NO+, O+, O2+)
        # mi = ni/(self.ionos.ni['O+']/Ao/amu + self.ionos.ni['O2+']/Ao2/amu + \
        #         self.ionos.ni['NO+']/(An + Ao)/amu)
        mi = (Ao*amu + Ao2*amu)/2.
        # neutral mean molecular mass in amu
        A = (Ahe*self.atm.rho['He'] + Ao*self.atm.rho['O'] + \
            An2*self.atm.rho['N2'] + Ao2*self.atm.rho['O2'] + \
            Aar*self.atm.rho['Ar'])/nn
        # gyroradii
        self.wce = qe*self.mag.B['total']*1e-9/me
        self.wci = qe*self.mag.B['total']*1e-9/mi
        # collision frequencies
        self.nu_en = 5.4e-16 * nn * self.ionos.Te**(1./2.) \
                + ( 59. + 4.18*np.log(self.ionos.Te**3/(self.ionos.ne*1e-6)) ) \
                *1e-6 * self.ionos.ne * self.ionos.Te**(-3./2.)
        self.nu_in = 2.6e-15 * (nn + ni) * A**(-1./2.)

        # Direct conductivity
        self.sig0 = self.ionos.ne*qe**2 * ( 1./(me * self.nu_en) + 1./(mi * self.nu_in) )

        # Pedersen conductivity
        self.sigP = self.ionos.ne*qe**2 * ( self.nu_en/me * 1./(self.nu_en**2 + self.wce**2) \
                + self.nu_in/mi * 1./(self.nu_in**2 + self.wci**2) )

        # Hall conductivity
        self.sigH = self.ionos.ne*qe**2 * ( self.wce/me * (1./(self.nu_en**2 + self.wce**2) ) \
                - self.wci/mi * ( 1./(self.nu_in**2 + self.wci**2) ) )

    def plot_collfreq(self, ilat=0, ilon=0,
        fig=None, ax=None, 
        legend='upper left'):
        """ Plot collision frequencies

        **Args**:
            * `ilat` (int): latitude index
            * `ilon` (int): longitude index
            * `fig`: matplotlib figure object
            * `ax`: matplotlib axes object
            * `legend`: legend placement (None for no legend)
        """
        import matplotlib as mp

        if fig is None and ax is None:
            fig = mp.figure.Figure()
            ax = fig.add_subplot(111)
        elif ax is None:
            ax = fig.add_subplot(111)

        ax.plot(self.nu_en[ilat,ilon,:], self.alt, 
            label=r'$\nu_{en}$',)
        ax.plot(self.nu_in[ilat,ilon,:], self.alt, 
            label=r'$\nu_{in}$',)

        ax.set_xlabel(r'$\nu$ [s$^{-1}$]')
        ax.set_ylabel(r'altitude [km]')
        ax.set_xscale('log')
        if legend is not None:
            ax.legend(loc=legend)
        ax.grid()

        return fig, ax

    def plot_cond(self, ilat=0, ilon=0,
        fig=None, ax=None, 
        legend='upper left'):
        """ Plot conductivities

        **Args**:
            * `ilat` (int): latitude index
            * `ilon` (int): longitude index
            * `fig`: matplotlib figure object
            * `ax`: matplotlib axes object
            * `legend`: legend placement (None for no legend)
        """
        import matplotlib as mp
        import numpy as np

        if fig is None and ax is None:
            fig = mp.figure.Figure()
            ax = fig.add_subplot(111)
        elif ax is None:
            ax = fig.add_subplot(111)

        ax.plot(self.sig0[ilat,ilon,:], self.alt, 
            label=r'$\sigma_0$')
        ax.plot(self.sigP[ilat,ilon,:], self.alt, 
            label=r'$\sigma_P$')
        ax.plot(self.sigH[ilat,ilon,:], self.alt, 
            label=r'$\sigma_H$')
        ax.set_xlabel(r'$\sigma$ [S/m]')
        ax.set_ylabel(r'altitude [km]')
        ax.set_xscale('log')
        if legend is not None:
            ax.legend(loc=legend)
        ax.grid()

        return fig, ax






