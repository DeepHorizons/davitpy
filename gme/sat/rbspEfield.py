# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
*********************
**Module**: gme.sat.rbspEfield
*********************
This module handles reading of RBSP Efield data

**Class**:
  * :class:`gme.sat.rbspEfield.efieldRec`
**Functions**:
  * :func:`gme.sat.rbspEfield.readEfieldFtp`
  * :func:`gme.sat.rbspEfield.mapEfieldMongo`  BHARAT WRITE THIS TO READ FROM FTP AND STORE IN MONGODB
  * :func:`gme.sat.rbspEfield.readEfield` BHARAT WRITE THIS TO READ FROM MONGODB
"""
import gme 

class efieldRec(gme.base.gmeBase.gmeData):
  """a class to represent a record of RBSP EFW E field.  Extends :class:`gme.base.gmeBase.gmeData`.  Note that RBSP EFW data is available from September 5 2012-present day (or whatever the latest NASA has uploaded is).
  
  **Members**: 
    * **time** (`datetime <http://tinyurl.com/bl352yx>`_): an object identifying which time these data are for
    * **info** (str): information about where the data come from.  *Please be courteous and give credit to data providers when credit is due.*
    * **dataSet** (str): the name of the data set
    * **sat** (char): the satllite letter, a or b
    * **ex** (float): electric field x component
    * **ey** (float): electric field x component
    * **ez** (float): electric field x component
    
  .. note::
    If any of the members have a value of None or nan, this means that they could not be read for that specific time or are not good
   
  **Methods**:
    * Nothing.

  **Example**:
    ::
    
      emptyEfieldObj = gme.sat.efieldRec()
    
  written by AJ, 20130620
  """
  def __init__(self,time=None,elist=None,sat=None):
    self.time = time
    self.ex = elist[0]
    self.ey = elist[1]
    self.ez = elist[2]
    self.dataSet = 'RBSP Efield Spinfit Data'
    self.info = 'These data were downloaded from NASA CDAWEB at ftp://cdaweb.gsfc.nasa.gov/pub/data/rbsp, and the PI on the EFW instrument is J. Wygant from University of Minnesota'
    self.sat = sat


def readEfieldFtp(sTime,eTime=None,sat=['a','b']):
  """This function reads RBSP E Field data from the NASA GSFC server via anonymous FTP connection.
  
  .. warning::
    You should not use this. Use the general function :func:`gme.sat.rbspEfield.readEfield` instead.
  
  **Args**: 
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the earliest time you want data for
    * [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, eTime will be equal 1 day after sTime.  default = None
  **Returns**:
    * **myList** (list or None): if data is found, a list of :class:`gme.sat.rbspEfield.efieldRec` objects matching the input parameters is returned.  If no data is found, None is returned.
  **Example**:
    ::
    
      import datetime as dt
      efieldList = gme.sat.readEfieldFtp(dt.datetime(2013,1,1,1,50),eTime=dt.datetime(2013,1,1,10,0))
    
  written by AJ, 20130620
  """
  
  from ftplib import FTP
  import datetime as dt
  import os
  from spacepy import pycdf
  
  assert(isinstance(sTime,dt.datetime)),'error, sTime must be datetime'
  if(eTime == None): eTime=sTime+dt.timedelta(days=1)
  assert(isinstance(eTime,dt.datetime)),'error, eTime must be datetime'
  assert(eTime >= sTime), 'error, end time before start time'
  if not isinstance(sat,list): 
    assert(sat == 'a' or sat =='b'),"error, sat must be 'a','b', or ['a','b']"
    sat = [sat]

  
  #connect to the server
  try: ftp = FTP('cdaweb.gsfc.nasa.gov')  
  except Exception,e:
    print e
    print 'problem connecting to NASA server'
    return None
    
  #login as anonymous
  try: l=ftp.login()
  except Exception,e:
    print e
    print 'problem logging in to NASA server'
    return None

  #a temporary directory to store a temporary file
  tmpDir = '/tmp/sat/'
  d = os.path.dirname(tmpDir)
  if not os.path.exists(d):
    os.makedirs(d)


  myData = []
  #get the poes data
  myTime = dt.datetime(sTime.year,sTime.month,sTime.day)
  while(myTime < eTime):
    #iterate over the two satellites
    for s in sat:
      #go to the data directory for satellite s
      try: ftp.cwd('/pub/data/rbsp/rbsp%s/l2/efw/e-spinfit-mgse/%s' % (s,str(myTime.year)))
      except Exception,e:
        print e
        print 'error getting to data directory'
        return None

      #list directory contents of target date
      dirlist = []
      try: 
        dirlist = ftp.nlst('*%s*' % myTime.strftime("%Y%m%d"))
      except:
        print "couldn't find requested FTP data for sat A"

      #if we found files
      if len(d) > 0:
        #check more more than 1 version of the file
        maxver,maxind = -1,-1
        for i in range(len(dirlist)):
          d = dirlist[i]
          ind = d.find('_v')
          if ind != -1:
            ver = int(d[ind+2:ind+4])
            if ver > maxver: 
              maxver = ver
              maxind = i
        if maxind == -1: maxind = 0

        #actually download the file
        try: 
          #store the file in /tmp/sat
          filep = open(tmpDir+dirlist[maxind], 'wb')
          ftp.retrbinary('RETR '+dirlist[maxind],filep.write)
          filep.close()
        except Exception,e:
          print e,maxind
          print 'error retrieving file',dirlist[maxind]
          continue

        #read the cdf file using spacepy
        cdf = pycdf.CDF(tmpDir+dirlist[maxind])
        for i in range(len(cdf['vxb_spinfit_mgse'])):
          #parse the cdf data into a list of efieldRec objects
          if sTime <= cdf['epoch'][i] < eTime:
            myData.append(efieldRec(time=cdf['epoch'][i],elist=cdf['e12_spinfit_mgse'][i],sat=s))

    #delete the downloaded file
    os.system('rm %s*%s*' % (tmpDir,myTime.strftime("%Y%m%d")))
    #increment the number of days
    myTime += dt.timedelta(days=1)

  #quit the ftp session
  try: 
    ftp.quit()
  except:
    print 'problem quitting FTP'

  #return the data
  if len(myData) > 0: 
    myData.sort(key=lambda x: x.time)
    return myData
  else: 
    return None

