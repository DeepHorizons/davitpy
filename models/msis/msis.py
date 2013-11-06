# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.msis.msis
*********************
This module wraps IRI fortran subroutines

**Classes**:
    * :class:`models.msis.msis.Msis`

**Functions**:
    * :func:`models.msis.msis.getF107Ap`

Written by Sebastien
"""

class Msis(object):
    """ This class runs and stores the MSIS model and its results

    **Args**:
        * `date` (`datetime <http://tinyurl.com/bl352yx>`_): date and time
        * `lat` (float or iterable): latitude(s)
        * `lon` (float or iterable): longitude(s)
        * `alt` (float or iterable): altitude(s)

    **Example**:
    ::

        import datetime as dt
        date = dt.utcnow()
        atm = Msis(date, 50, -80, range(100, 500, 10))

    .. note:: rho['total'] is the total mass density in kg/m^3 while rho['X'] are number densities in m^-3

    .. note:: O, H and N are set to 0 below 72.5 km

    """
    def __init__(self, date, lat, lon, alt):
        # Inputs
        self.date = date
        self.lat = self.__iterable(lat)
        self.lon = self.__iterable(lon)
        self.alt = self.__iterable(alt)

        # Calculate everything
        self.mass = 48

        # Solar conditions:
        self.sol = getF107Ap(self.date)

        # Run fortran code
        self.run()

    def run(self):
        """ Run fortran subroutine(s)
        """
        import msisFort
        import numpy as np

        # Force to SI units:
        msisFort.meters(True)

        # Some input conversions
        iyd = (self.date.year - self.date.year/100*100)*100 \
                + self.date.timetuple().tm_yday
        sec = self.date.hour*24. + self.date.minute*60.

        # output arrays
        dim = (len(self.lat), 
            len(self.lon), 
            len(self.alt))
        self.T = np.zeros(dim)
        self.rho = {'total': np.zeros(dim),
                    'N2': np.zeros(dim),
                    'O2': np.zeros(dim),
                    'O': np.zeros(dim),
                    'N': np.zeros(dim),
                    'Ar': np.zeros(dim),
                    'H': np.zeros(dim),
                    'He': np.zeros(dim),}

        # Call fortran subroutine
        for i,lat in enumerate(self.lat):
            for j,lon in enumerate(self.lon):
                stl = sec/3600. + lon/15.
                for k,alt in enumerate(self.alt):
                    d,t = msisFort.gtd7(iyd, sec, alt, lat, lon, stl, 
                        self.sol['f107a'], self.sol['f107'], 
                        self.sol['ap'], self.mass)
                    self.T[i,j,k] = t[1]
                    self.rho['total'][i,j,k] = d[5]
                    self.rho['N2'][i,j,k] = d[2]
                    self.rho['O2'][i,j,k] = d[3]
                    self.rho['N'][i,j,k] = d[7]
                    self.rho['O'][i,j,k] = d[1]
                    self.rho['H'][i,j,k] = d[6]
                    self.rho['He'][i,j,k] = d[0]
                    self.rho['Ar'][i,j,k] = d[4]
        

    def __iterable(self, iterable):
        """ Check if `iterable` is iterable, if not, make it so.
        """
        import numpy as np
        try:
            return np.array( [l for l in iterable] )
        except TypeError:
            return np.array( [iterable] )



def getF107Ap(mydatetime=None):
    """Obtain F107 and AP required for MSIS input from tabulated values in IRI data.

    **Args**:
    * `mydatetime`: python datetime object (defaults to last tabulated value)

    **Returns**:
    * `dictOut`: a dictionnary containing:
      * datetime: the date and time as a python datetime object
      * f107: daily f10.7 flux for previous day
      * f107a: 81 day average of f10.7 flux (centered on date)
      * ap: magnetic index containing:
        * (1) daily AP
        * (2) 3 HR AP index for current time
        * (3) 3 HR AP index for 3 hours before current time
        * (4) 3 HR AP index for 6 hours before current time
        * (5) 3 HR AP index for 9 hours before current time
        * (6) Average of eight 3 hour AP indicies from 12 to 33 hrs prior to current time
        * (7) Average of eight 3 hour AP indicies from 36 to 57 hrs prior to current time

    """
    from models import iri
    from datetime import datetime
    from numpy import mean, floor

    # Get current path to IRI module
    path = iri.__file__.partition('__init__.py')[0]

    # open apf107.dat file
    with open('{}apf107.dat'.format(path), 'r') as fileh:
        data = []
        for line in fileh:
            data.append(line)

    # read into array 
    # (cannot use genfromtext because some columns are not separated by anything)
    tdate = []
    tap = []
    tapd = []
    tf107 = []
    tf107a = []
    tf107y = []
    for ldat in data:
        yy = int(ldat[1:3])
        year = 1900+yy if (yy >= 58) else 2000+yy
        tdate.append( datetime(year, int(ldat[4:6]), int(ldat[7:9])).date() )
        ttap = []
        for iap in xrange(8):
            ttap.append( int(ldat[9+3*iap:9+3*iap+4]) )
        tap.append( ttap )
        tapd.append( int(ldat[33:36]) )
        tf107.append( float(ldat[39:44]) )
        tf107a.append( float(ldat[44:49]) )
        tf107y.append( float(ldat[49:54]) )

    # Get required datetime
    dictOut = {}
    if mydatetime is None:
        dictOut['datetime'] = datetime(tdate[-1].year, tdate[-1].month, tdate[-1].day)
    elif mydatetime.date() <= tdate[-1]:
        dictOut['datetime'] = mydatetime
    else:
        print 'Invalid date {}'.format(mydatetime)
        print 'Date must be in range {} to {}'.format(tdate[0],tdate[-1])
        return

    # Find entry for date
    dtInd = tdate.index(dictOut['datetime'].date())
    # Find hour index
    hrInd = int( floor( dictOut['datetime'].hour/3. ) )

    # f107 output
    dictOut['f107'] = tf107[dtInd-1]
    dictOut['f107a'] = tf107a[dtInd]

    # AP output
    ttap = [ tap[dtInd][hrInd-i] for i in range(hrInd+1) ]
    for id in xrange(3):
        for ih in xrange(8):
            ttap.append(tap[dtInd-id-1][-ih-1])
    dictOut['ap'] = [ tapd[dtInd], 
                    ttap[0], 
                    ttap[1], 
                    ttap[2], 
                    ttap[3], 
                    mean(ttap[4:13]), 
                    mean(ttap[13:26])
                  ]

    return dictOut