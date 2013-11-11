# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.igrf.igrf
*********************
This module wraps IGRF fortran subroutines

**Classes**:
    * :class:`models.igrf.igrf.Igrf`

Written by Sebastien
"""
from models import Model as __Model

class Igrf(__Model):
    """ This class runs and stores the IGRF model and its results

    **Args**:
        * `date` (`datetime <http://tinyurl.com/bl352yx>`_): date and time
        * `lat` (float or iterable): latitude(s)
        * `lon` (float or iterable): longitude(s)
        * `alt` (float or iterable): altitude(s)
        * `field_type` (str): 'MF' for main field (default), 'SV' for secular variation, 'both' for both

    **Example**:
    ::

        import datetime as dt
        date = dt.utcnow()
        atm = Igrf(date, 50, -80, range(100, 500, 10))

    .. note:: 

    """
    def __init__(self, date, lat, lon, alt, 
        field_type='MF'):
        super(Igrf, self).__init__(date, lat, lon, alt)

        # Calculate everything
        self.mass = 48

        # Field calculation type
        self.field_type = field_type

        # Run fortran code
        self.run()

    def run(self):
        """ Run fortran subroutine(s)
        """
        import igrfFort
        import utils
        import numpy as np

        # Some input conversions
        # Geodetic coordinates
        itype = 1
        # decimal year
        yyd = utils.dateToDecYear(self.date)
        # latitude start, stop, step
        if len(self.lat) > 1:
            stp = (max(self.lat) - min(self.lat))/(len(self.lat) - 1)
        else: 
            stp = 1
        xlti, xltf, xltd = self.lat[0], self.lat[-1], stp
        # longitude start, stop, step
        if len(self.lon) > 1:
            stp = (max(self.lon) - min(self.lon))/(len(self.lon) - 1)
        else: 
            stp = 1
        xlni, xlnf, xlnd = self.lon[0], self.lon[-1], stp
        # 0- Main field
        # 1- Secular variation
        # 2- Both
        if self.field_type == 'MF':
            ifl = 0
        elif self.field_type == 'SV':
            ifl = 1
        else:
            ifl = 2

        # output arrays
        dim = (len(self.lat), 
            len(self.lon), 
            len(self.alt))
        self.dip = np.zeros(dim)
        self.dec = np.zeros(dim)
        self.B = {'total': np.zeros(dim),
                  'north': np.zeros(dim),
                  'east': np.zeros(dim),
                  'hori': np.zeros(dim),
                  'vert': np.zeros(dim),}

        # Call fortran subroutine
        for k,alt in enumerate(self.alt):
            lat, lon, d, s, h, x, y, z, f = \
                igrfFort.igrf11(itype, yyd, alt, ifl, 
                    xlti, xltf, xltd, 
                    xlni, xlnf, xlnd)
            self.dip[:,:,k] = s.reshape(dim[0:2])
            self.dec[:,:,k] = d.reshape(dim[0:2])
            self.B['total'][:,:,k] = f.reshape(dim[0:2])
            self.B['north'][:,:,k] = f.reshape(dim[0:2])
            self.B['east'][:,:,k] = f.reshape(dim[0:2])
            self.B['hori'][:,:,k] = f.reshape(dim[0:2])
            self.B['vert'][:,:,k] = f.reshape(dim[0:2])

