# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.msis
*********************
Runs the NRLMSIS00 model

**Modules**:
  * :mod:`models.msis.msis`: MSIS wrapper
  * :mod:`models.msis.msisFort`: Fortran subroutines
  
"""

try: 
    import msisFort
except Exception as e:
    print __file__+' -> models.msis.msisFort: ', e 
try: 
    from msis import *
except Exception as e:
    print __file__+' -> models.msis.msis: ', e
