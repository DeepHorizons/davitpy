# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.iri
*********************
International Reference Ionosphere

**Modules**:
  * :mod:`models.iri.iri`: IRI wrapper
  * :mod:`models.iri.iriFort`: fortran subroutines 

"""

try:
      import iriFort
except Exception, e:
      print __file__+' -> models.iri.iriFort: ', e
try:
      from iri import *
except Exception, e:
      print __file__+' -> models.iri.iri: ', e
