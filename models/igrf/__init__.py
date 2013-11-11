# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.igrf
*********************
International GeoMagnetic Reference Field

**Modules**:
  * :mod:`models.igrf.igrf`: IGRF wrapper
  * :mod:`models.igrf.igrfFort`: fortran subroutines

"""

try:
    import igrfFort
except Exception, e:
    print __file__+' -> models.igrf.igrfFort: ', e
try:
    from igrf import *
except Exception, e:
    print __file__+' -> models.igrf.igrf: ', e
