#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Spyder Editor
tESTANDO O COMIT DO GITHUB
Este é um arquivo que será deletado em breve
"""

import sys
import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

"""
graph1 function plots a XYZ scatter plot over time
"""
def graph1(posError, text):
    X = [] 
    Y = []
    Z = []
    time = []        
    for i in posError:
        time.append(i[0]*10000 + i[1]*100 + i[2])
        X.append(i[3])
        Y.append(i[4])
        Z.append(i[5])
    plt.figure()
    plt.scatter(time,X,c='blue',label='X error')
    plt.scatter(time,Y,c='red',label='Y error')
    plt.scatter(time,Z,c='green',label='Z error')
    plt.xlabel('time hhmmss')
    plt.ylabel('Error (m)')
    plt.title(text)
    plt.legend()
    plt.grid(True)
    plt.figure(0)
    plt.show

"""
deg2xyz function converts Latitude, Longitude and Height to XYZ
"""
def deg2xyz(Lat,Lon,h):
    a = 6378137
    e = 0.081819191
    result = []
    N = ( a / ((1-(e**2)*(math.sin(math.radians(Lat)))**2)**(1/2.0)))
    X = (N+h)*math.cos(math.radians(Lat))*math.cos(math.radians(Lon))
    Y = (N+h)*math.cos(math.radians(Lat))*math.sin(math.radians(Lon))
    Z = (N*(1-e**2)+h)*math.sin(math.radians(Lat))
    result.append(X)
    result.append(Y)
    result.append(Z)
    return result


"""
.POS format
     Position:    Description:
     0            Date of survey as YYYY/MM/DD
     1            Epoch as HH:MM:SS.SSSS (seconds are float)
     2            x-ecef(m)
     3            y-ecef(m)
     4            z-ecef(m)
     5            Q
     6            ns = # of satellites
     7            sdx(m)
     8            sdy(m)   
     9            sdz(m)
     10           sdxy(m)
     11           sdyz(m)
     12           sdzx(m)
     13           age(s)
     14           ratio
"""


"""
rinexError function reads XYZ of a known location and compares it to a .POS file format
"""
def rinexError(fileName):
    posError = []
    Xonrj = 4283638.3579
    Yonrj = -4026028.8217
    Zonrj = -2466096.8361
    with open(fileName, 'r') as posFile:
        for line in posFile:
            if line[0] == '%':
                continue
            else:
                dataArray = line.split()
                if len(dataArray) == 0: # Pula linhas vazias
                    continue
                hTime = int(dataArray[1][0:2])
                mTime = int(dataArray[1][3:5])
                sTime = int(dataArray[1][6:8])
                Xpos = float(dataArray[2])
                Ypos = float(dataArray[3])
                Zpos = float(dataArray[4])
                Xerror = Xonrj - Xpos
                Yerror = Yonrj - Ypos
                Zerror = Zonrj - Zpos
                epoch = (hTime, mTime, sTime, Xerror, Yerror, Zerror)
                posError.append( epoch )            
        posFile.close()
    graph1(posError, "RINEX file X and Y error")
    
"""
nmeaError function reads Latitude, Longitude and Altitude or Height of geoid
          of a known location and compares it to a NMEA file format
"""
def nmeaError(nmeafileName):
    nmeaData = []
    LatMarco = 22 + 49/60.0 + 08.76793/3600
    LonMarco = 43 + 18/60.0 + 23.95193/3600
    h = -1.461
    XYZMarco = deg2xyz(LatMarco,LonMarco,h)
    
    with open(nmeafileName, 'r') as nmeaFile:
        for line in nmeaFile:
            line = line.translate(None, '$')
            dataArray = line.split(',')
            if len(dataArray) == 0: # Pula linhas vazias
                continue
            sentenceId = dataArray[0]
            if sentenceId == "GPGGA":
                fixQuality = dataArray[6]
                #if fixQuality[0] != 'N' and fixQuality[1] != 'N':
                if fixQuality[0] != '0':
                    hTime = int(dataArray[1][0:2])
                    mTime = int(dataArray[1][2:4])
                    sTime = int(dataArray[1][4:6])
                    dLat = int(dataArray[2][0:2])
                    mLat = float(dataArray[2][2:])
                    dLon = int(dataArray[4][0:3])
                    mLon = float(dataArray[4][3:])
                    h = float(dataArray[9]) 
                    ddLat = dLat + mLat/60
                    ddLon = dLon + mLon/60
                    XYZnmea = deg2xyz(ddLat,ddLon,h)
                    
                    Xerror = XYZMarco[0] - XYZnmea[0]
                    Yerror = XYZMarco[1] - XYZnmea[1]
                    Zerror = XYZMarco[2] - XYZnmea[2]                
                    
                    epoch = (hTime, mTime, sTime, Xerror, Yerror, Zerror)
                    nmeaData.append( epoch )
        nmeaFile.close()
        graph1(nmeaData, "NMEA file X and Y error")


#nmeafileName = '02_20170824135855.txt'
#nmeafileName = '01_20170824122806.txt'
#nmeafileName = '00_20170824133538_Tools.txt'

#fileName = 'filteredRinex20_G_Debugg_XYZ.pos'
#fileName = 'onrj2361_XYZ.pos'

rinexError('filteredRinex20_G_Debugg_XYZ.pos')
rinexError('onrj2361_XYZ.pos')
nmeaError('01_20170824122806.txt')
nmeaError('02_20170824135855.txt')
nmeaError('00_20170824133538_Tools.txt')


"""
time = []
X =[]
Y=[]
for i in posError:
    time.append(i[0]*10000 + i[1]*100 + i[2])
    X.append(i[3])
    Y.append(i[4])

plt.scatter(time,X,c='blue',label='X error')
plt.scatter(time,Y,c='red',label='Y error')
plt.xlabel('time hhmmss')
plt.ylabel('Error (m)')
plt.title('RINEX file X and Y error')
plt.legend()
plt.grid(True)
plt.figure(0)
plt.show

del time[:]
del X[:]
del Y[:]
M = 6345019.905403
N = 6381350.429605


for i in nmeaData:
    time.append(i[0]*10000 + i[1]*100 + i[2])
    X.append(math.radians(i[3])*M)
    Y.append(math.radians(i[4])*N)
plt.figure()
plt.scatter(time,X,c='blue',label='Lat error')
plt.xlabel('time hhmmss')
plt.ylabel('Error (m)')
plt.title('NMEA file X error')
plt.legend()
plt.grid(True)
plt.show

plt.figure()
plt.scatter(time,Y,c='red',label='Lon error')
plt.xlabel('time hhmmss')
plt.ylabel('Error (m)')
plt.title('NMEA file Y error')
plt.legend()
plt.grid(True)
plt.show
"""

print 'Program has Finished!'