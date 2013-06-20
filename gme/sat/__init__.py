# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: gme.sat
*********************
This subpackage contains various fucntions to read and write sattelite data

This includes the following modules:
    * **poes**
    * **rbsp**
"""
try: import poes
except Exception, e:
    print __file__+' -> gme.sat.poes: ', e
try: from poes import *
except Exception, e:
    print __file__+' -> gme.sat.poes: ', e

try: import rbspFp
except Exception, e:
    print __file__+' -> gme.sat.rbspFp: ', e
try: from rbspFp import *
except Exception, e:
    print __file__+' -> gme.sat.rbspFp: ', e

try: import rbspEfield
except Exception, e:
    print __file__+' -> gme.sat.rbspEfield: ', e
try: from rbspEfield import *
except Exception, e:
    print __file__+' -> gme.sat.rbspEfield: ', e