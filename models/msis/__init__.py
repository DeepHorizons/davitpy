# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.msis
*********************
Runs the NRLMSIS00 model

**Modules**:
  * :mod:`msis`: wrapper object

**Functions**:
  * :func:`models.msis.msisFort.gtd7`
    * **Args**:
      * **IYD** - year and day as YYDDD (day of year from 1 to 365 (or 366)) (Year ignored in current model)
      * **SEC** - UT (SEC)
      * **ALT** - altitude (KM)
      * **GLAT** - geodetic latitude (DEG)
      * **GLONG** - geodetic longitude (DEG)
      * **STL** - local aparent solar time (HRS; see Note below)
      * **F107A** - 81 day average of F10.7 flux (centered on day DDD)
      * **F107** - daily F10.7 flux for previous day
      * **AP** - magnetic index (daily) OR when SW(9)=-1., array containing:
          * (1) daily AP
          * (2) 3 HR AP index FOR current time
          * (3) 3 HR AP index FOR 3 hrs before current time
          * (4) 3 HR AP index FOR 6 hrs before current time
          * (5) 3 HR AP index FOR 9 hrs before current time
          * (6) average of height 3 HR AP indices from 12 TO 33 HRS prior to current time
          * (7) average of height 3 HR AP indices from 36 TO 57 HRS prior to current time
      * **MASS** - mass number (only density for selected gass is calculated.  MASS 0 is temperature.  
        MASS 48 for ALL. MASS 17 is Anomalous O ONLY.)
    * **Returns**:
      * **D(1)** - HE number density(CM-3)
      * **D(2)** - O number density(CM-3)
      * **D(3)** - N2 number density(CM-3)
      * **D(4)** - O2 number density(CM-3)
      * **D(5)** - AR number density(CM-3)                       
      * **D(6)** - total mass density(GM/CM3)
      * **D(7)** - H number density(CM-3)
      * **D(8)** - N number density(CM-3)
      * **D(9)** - Anomalous oxygen number density(CM-3)
      * **T(1)** - exospheric temperature
      * **T(2)** - temperature at ALT
  
"""

try: 
    import msisFort
except Exception as e:
    print __file__+' -> models.msis: ', e 
try: 
    from msis import *
except Exception as e:
    print __file__+' -> models.msis: ', e
