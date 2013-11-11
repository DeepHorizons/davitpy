# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.iri.iri
*********************
This module wraps IRI fortran subroutines

**Classes**:
    * :class:`models.iri.iri.Iri`: run and store iri

Written by Sebastien
"""
from models import Model as __Model

class Iri(__Model):
    """ This class runs and stores the IRI model and its results

    **Args**:
        * `date` (`datetime <http://tinyurl.com/bl352yx>`_): date and time
        * `lat` (float or iterable): latitude(s)
        * `lon` (float or iterable): longitude(s)
        * `alt` (float or iterable): altitude(s)
        * `coords` (string): coordinatesm, 'geo' or 'mag'

    **Example**:
    ::

        import datetime as dt
        date = dt.utcnow()
        ionos = Iri(date, 50, -80, range(100, 500, 10))

    .. note:: altitude limits: Electron density (60/80 km to 1000 km), Tempperatures (120 km to 2500/3000 km), Ion densities (100 km to 1000 km)

    """
    def __init__(self, date, lat, lon, alt, 
        coords='geo', ut=True, run=True):
        super(Iri, self).__init__(date, lat, lon, alt, 
                                limit=1000)

        # coordinates
        self.coords = coords
        # ut or not ut
        self.ut = ut

        # Initialize default options:
        self.initialize()

        # Run fortran code
        if run:
            self.run()

    def plot_profile(self, ilat=0, ilon=0, 
        fig=None, ax=None, 
        legend='upper left'):
        """ Plot density and temperature profiles

        **Args**:
            * `ilat` (int): latitude index
            * `ilon` (int): longitude index
            * `fig`: matplotlib figure object
            * `ax`: matplotlib axes object (list of 2)
            * `legend`: legend placement (None for no legend)
        """
        import matplotlib as mp

        if fig is None and ax is None:
            fig = mp.figure.Figure()
            ax = [fig.add_subplot(1,2,1),
                  fig.add_subplot(1,2,2),]
        elif ax is None:
            ax = [fig.add_subplot(1,2,1),
                  fig.add_subplot(1,2,2),]


        ax[0].plot(self.ne[ilat,ilon,:], self.alt, 
            label=r'$n_{e}$',)
        for ion in self.ni:
            ax[0].plot(self.ni[ion][ilat,ilon,:], self.alt, 
                label=ion, linestyle='--')
        ax[0].set_xlabel(r'density [m$^{-3}$]')


        ax[1].plot(self.T[ilat,ilon,:], self.alt, 
            label=r'T',)
        ax[1].plot(self.Te[ilat,ilon,:], self.alt, 
            label=r'T$_e$',)
        ax[1].plot(self.Ti[ilat,ilon,:], self.alt, 
            label=r'T$_i$',)
        ax[1].set_xlabel(r'temperature [K]')

        for axx in ax:
            axx.set_ylabel(r'altitude [km]')
            axx.set_xscale('log')
            if legend is not None:
                axx.legend(loc=legend)
            axx.grid()

        return fig, ax

    def run(self):
        """ Run fortran subroutine(s)
        """
        import iriFort
        import numpy as np

        # output arrays
        dim = (len(self.lat), 
            len(self.lon), 
            len(self.alt))
        self.ne = np.zeros(dim)
        self.T = np.zeros(dim)
        self.Ti = np.zeros(dim)
        self.Te = np.zeros(dim)
        self.ni = {'O+': np.zeros(dim),
                   'H+': np.zeros(dim),
                   'He+': np.zeros(dim),
                   'O2+': np.zeros(dim),
                   'NO+': np.zeros(dim),
                   'N+': np.zeros(dim),
                   'cluster': np.zeros(dim),}
        self.params_out = np.zeros((dim[0], dim[1], 100))

        # Call fortran subroutine
        for i, alati in enumerate(self.lat):
            for j, along in enumerate(self.lon):
                outf, oarr = iriFort.iri_sub(self.jf, 
                    1*(self.coords == 'mag'), alati, along,
                    self.date.year, self.date.month*100 + self.date.day, 
                    self.date.hour + self.date.minute + 25*self.ut,
                    self.alt[0], self.alt[-1], 
                    (self.alt[-1] - self.alt[0])/(len(self.alt)-1),
                    self.params)
                self.ne[i,j,:] = outf[0,0:dim[2]]
                self.T[i,j,:] = outf[1,0:dim[2]]
                self.Ti[i,j,:] = outf[2,0:dim[2]]
                self.Te[i,j,:] = outf[3,0:dim[2]]
                self.ni['O+'][i,j,:] = outf[4,0:dim[2]]
                self.ni['H+'][i,j,:] = outf[5,0:dim[2]]
                self.ni['He+'][i,j,:] = outf[6,0:dim[2]]
                self.ni['O2+'][i,j,:] = outf[7,0:dim[2]]
                self.ni['NO+'][i,j,:] = outf[8,0:dim[2]]
                self.ni['cluster'][i,j,:] = outf[9,0:dim[2]]
                self.ni['N+'][i,j,:] = outf[10,0:dim[2]]
                self.params_out[i,j,:] = oarr

    def initialize(self, ne=True, ni=2, vi=False, 
        ni_units='m', temp=True, 
        b0=0, f0f2mod='ursi', f107lim=True, 
        nete=None, nemod=0, f1mod=0, netops=2, 
        tetops=1, spreaF=False, auroral_bound=False,
        foE_storm=False, foF2_storm=False,  
        nmF2=None, hmF2=None, foF2=None, 
        nmF1=None, hmF1=None, foF1=None, 
        nmE=None, hmE=None, foE=None, 
        f107_d=None, f107_81=None, 
        rz12=None, ig12=None):
        """Initializes default IRI settings
        * `ne`: compute electron densities
        * `ni`: compute ion densities: None, 1 - DS-95 & DY-85, 2 - RBV-10 & TTS-03 
        * `ni_units`: ion units in m^-3 ('m') or percent ('%')
        * `vi`: ion drift computed
        * `temp`: compute Te and Ti
        * `b0`: 0 - tabulated, 1 - ABT-2009, 2 - Gulyaeva h0.5
        * `fof2mod`: 'ursi' or 'ccir'
        * `f107lim`: f10.7 limited at 188 or not
        * `nete`: 2 element array to calculate Te [ne(300km), ne(400km)] or [ne(300km), ne(550km)]
        * `nemod`: 0 - Standard, 1 - Lay-function formalism
        * `f1mod`: 0 - Standard, 1 - F1 plus L condition
        * `netops`: 0 - IRIold, 1 - IRIcor, 2 - NeQuick, 3 - Gulyaeva
        * `tetops`: 0 - Aeros, ISIS, 1 - TBT-2011
        * `spreaF`: compute probability of Spread-F
        * `auroral_bound`: auroral boundary model on/off True/False
        * `foE_storm`: foE storm model
        * `foF2_storm`: foF2 storm model
        * `nmF2`, `hmF2`, `foF2`: F2 peak density [m^-3], altitude [km], frequency [MHz] 
        * `nmF1`, `hmF1`, `foF1`: F1 peak density [m^-3], altitude [km], frequency [MHz] 
        * `nmE`, `hmE`, `foE`: E peak density [m^-3], altitude [km], frequency [MHz]
        * `f107_d`, `f107_81`: f10.7 daily and 81 days 
        * `rz12`: sunspot number
        * `ig12`: ionospheric index
        """
        test = lambda var, val: True if var == val else False
        self.params = [-1]*100
        self.jf = [False]*50
        self.jf[0] = test(ne, True)
        self.jf[1] = test(temp, True)
        self.jf[2] = test(ni, 1) or test(ni, 2)
        self.jf[3] = test(b0, 0)
        self.jf[4] = test(f0f2mod, 'ccir')
        self.jf[5] = test(ni, 1)
        self.jf[6] = test(f107lim, True)
        self.jf[7] = test(foF2, None) and test(nmF2, None)
        if not self.jf[7]:
            self.params[0] = foF2 if foF2 is not None else nmF2
        self.jf[8] = test(hmF2, None)
        if not self.jf[8]:
            self.params[1] = hmF2
        self.jf[9] = test(nete, None)
        if not self.jf[9]:
            self.params[14] = nete[0]
            self.params[15] = nete[1]
        self.jf[10] = test(nemod, 0)
        self.jf[11] = True
        self.jf[12] = test(foF1, None) and test(nmF1, None)
        if not self.jf[12]:
            self.params[2] = foF1 if foF1 is not None else nmF1
        self.jf[13] = test(hmF1, None)
        if not self.jf[13]:
            self.params[3] = hmF1
        self.jf[14] = test(foE, None) and test(nmE, None)
        if not self.jf[14]:
            self.params[4] = foE if foE is not None else nmE
        self.jf[15] = test(hmE, None)
        if not self.jf[15]:
            self.params[5] = hmE
        self.jf[16] = test(rz12, None)
        if not self.jf[16]:
            self.params[32] = rz12
        self.jf[17] = True
        self.jf[18] = True
        self.jf[19] = test(f1mod, 0)
        self.jf[20] = test(vi, True)
        self.jf[21] = test(ni_units, '%')
        self.jf[22] = test(tetops, 0)
        self.jf[23] = True
        self.jf[24] = test(f107_d, None)
        if not self.jf[24]:
            self.params[40] = f107_d
        self.jf[25] = test(foF2_storm, True)
        self.jf[26] = test(ig12, None)
        if not self.jf[26]:
            self.params[38] = ig12
        self.jf[27] = test(spreaF, True)
        self.jf[28] = test(netops, 0) or test(netops, 3)
        self.jf[29] = test(netops, 0) or test(netops, 1)
        self.jf[30] = test(b0, 1)
        self.jf[31] = test(f107_81, None)
        if not self.jf[31]:
            self.params[45] = f107_81
        self.jf[32] = test(auroral_bound, True)
        self.jf[33] = True
        self.jf[34] = test(foE_storm, True)