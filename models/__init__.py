# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models
*********************

**Modules**:
    * :mod:`models.aacgm`: corrected geomagnetic model
    * :mod:`models.tsyganenko`: T96
    * :mod:`models.iri`: International Reference Ionosphere 2012
    * :mod:`models.igrf`: International Geomagnetic Reference Field 2011
    * :mod:`models.msis`: Neutral atmosphere model (NRLMSISE-00)
    * :mod:`models.raydarn`: SuperDARN ray tracing code coupled with IRI

"""


class Model(object):
    """Baseclass for most fortran models

    **Args**:
        * `date` (`datetime <http://tinyurl.com/bl352yx>`_): date and time
        * `lat` (float or iterable): latitude(s)
        * `lon` (float or iterable): longitude(s)
        * `alt` (float or iterable): altitude(s)
        * `limit` (int): length limit on input vectors
    """
    def __init__(self, date, lat, lon, alt, limit=None):
        # First check for iterables:
        self.lat = self.__iterable(lat, limit=limit)
        self.lon = self.__iterable(lon, limit=limit)
        self.alt = self.__iterable(alt, limit=limit)
        # Save the date/time
        self.date = date

    def __iterable(self, iterable, limit=None):
        """ Check if `iterable` is iterable, if not, make it so.
        **Args**
            * `iterable`: the variable to be checked for iterability
            * `limit` (int): optional size limit on iterable (resample oversized ones) 
        **Returns**
            * `iterable`: the converted and possibly resampled iterable
        """
        import numpy as np
        try:
            out = np.array( [l for l in iterable] )
        except TypeError:
            out = np.array( [iterable] )
        if limit is not None and len(out) > limit:
            print('Resampling input [{}...{}]'.format(
                iterable[0], iterable[-1]))
            out = np.linspace(iterable[0], iterable[-1], limit)
        return out


try:
    import tsyganenko
except Exception, e:
    print __file__+' -> models.tsyganenko: ', e

try:
    import igrf
except Exception, e:
    print __file__+' -> models.igrf: ', e

try:
    import aacgm
except Exception, e:
    print __file__+' -> models.aacgm: ', e

try:
    import iri
except Exception, e:
    print __file__+' -> models.iri: ', e

try:
    import msis
except Exception, e:
    print __file__+' -> models.msis: ', e

try:
    import hwm
except Exception, e:
    print __file__+' -> models.hwm: ', e

try:
    import raydarn
except Exception, e:
    print __file__+' -> models.raydarn: ', e

try:
    import conductivity
except Exception, e:
    print __file__+' -> models.conductivity: ', e