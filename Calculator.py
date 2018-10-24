#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Spyder Editor

Este é um arquivo de script temporário.
"""

import sys
import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

"""
graph1 function plots a XYZ scatter plot over time

PASSAR TEMPO PARA SEGUNDOS DA SEMANA

Agrupar os erros de cada componente de cada soluçao e comparar com o original
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
    plt.scatter(time,X,c='blue',label='Phi error')
    plt.scatter(time,Y,c='red',label='Lambda error')
    plt.scatter(time,Z,c='green',label='H error')
    plt.xlabel('time hhmmss')
    plt.ylabel('Error (m)')
    plt.axis([time[0],time[len(time)-1],-15,6])
    plt.title(text)
    plt.legend()
    plt.grid(True)
    plt.figure(0)
    plt.show

"""
deg2xyz function converts Latitude, Longitude and Height to XYZ

TESTAR COM OS PROPRIOS VALORES DO RELATORIO

PRECISAO SIMPLES OU DUPLA?? tem que ser DuUPLA
"""
def deg2xyz(ddLat,ddLon,h):
    a = 6378137.0
    e = 0.08181919104282
    radLat = math.radians(ddLat)
    radLon = math.radians(ddLon)
    N = ( a / ((1-(e**2)*(math.sin(radLat))**2)**(0.5)))
    X = (N+h)*math.cos(radLat)*math.cos(radLon)
    Y = (N+h)*math.cos(radLat)*math.sin(radLon)
    Z = (N*(1-e**2)+h)*math.sin(radLat)
    XYZ = (X,Y,Z)
    return XYZ

def xyz2deg(X,Y,Z):
#    X = 4283638.3579
#    Y = -4026028.8217
#    Z = -2466096.8361
    a = 6378137.0
    e2 = (0.08181919104282)**2
    b = a*((1-e2)**0.5)
    elinha2 = e2/(1-e2)
    tanU = (Z/((X**2+Y**2)**0.5))*(a/b)
    senU = tanU/((1+tanU**2)**0.5)
    cosU = 1/((1+tanU**2)**0.5)
    radLat = math.atan((Z+(elinha2*b*(senU**3)))/((X**2+Y**2)**0.5-e2*a*cosU**3))
    radLon = math.atan(Y/X)
    N = ( a / ((1-(e2)*(math.sin(radLat))**2)**(0.5)))
    h = (((X**2+Y**2)**0.5)/math.cos(radLat))-N
    ddLat = math.degrees(radLat)
    ddLon = math.degrees(radLon)
    LatLonH = (ddLat,ddLon,h)
    return LatLonH

def radianError(phi1,lamb1,phi2,lamb2):
    a = 6378137.0
    e2 = (0.08181919104282)**2
    phiAvg = math.radians((phi2-phi1)/2)
    phi1 = math.radians(phi1)
    lamb1 = math.radians(lamb1)
    phi2 = math.radians(phi2)
    lamb2 = math.radians(lamb2)
#    radLat = math.radians(0)
#    phi2 = math.radians(1)
#    phi1 = math.radians(0)
#    lamb2 = math.radians(360)
#    lamb1 = math.radians(0)
    A = 1 + 3.0/4*e2 + 45.0/64*e2**2 + 175.0/256*e2**3 + 11025.0/16384*e2**4 + 43659.0/65536*e2**5
    B = 3.0/4*e2 + 15.0/16*e2**2 + 525.0/512*e2**3 + 2205.0/2048*e2**4 + 72765.0/65536*e2**5
    C = 15.0/64*e2**2 + 105.0/256*e2**3 + 2205.0/4096*e2**4 + 10395.0/16384*e2**5
    D = 35.0/512*e2**3 + 315.0/2048*e2**4 + 31185.0/131072*e2**5
    E = 315.0/16384*e2**4 + 3465.0/65536*e2**5
    F = 693.0/131072*e2**5
    phiA = A*(phi2-phi1)
    phiB = B/2 * (math.sin(2*phi2) - math.sin(2*phi1))
    phiC = C/4 * (math.sin(4*phi2) - math.sin(4*phi1))
    phiD = D/6 * (math.sin(6*phi2) - math.sin (6*phi1))
    phiE = E/8 * (math.sin(8*phi2) - math.sin(8*phi1))
    phiF = F/10 * (math.sin(10*phi2) - math.sin(10*phi1))
    
    M = (a*(1-e2)) / (1-e2*math.sin(phiAvg)**2)**(1.5)
    N = ( a / ((1-(e2)*(math.sin(phiAvg))**2)**(0.5)))
    
    S = a*(1-e2)*(phiA - phiB + phiC - phiD + phiE - phiF) #Comrpimento de arco de Meridiano
    L = N*math.cos(phiAvg)*(lamb2-lamb1)#Comprimento de arco de Paralelo
    
    Ssimples = M * (phi2-phi1)
    C = math.pi*a*2

    result = (S,L)

    return result



"""
print "Latitude calculada: " , ddCalcLat
print "Longitude calculada: " , ddCalcLon
print "Altitude elipsoidal calculada: " , hCalc
print "\n"
dmsRefLat = -(22 + 53/60.0 + 44.52202/3600)
dmsRefLon = -(43 + 13/60.0 + 27.59375/3600)
hRef = 35.636
print "Latitude referencia: " , dmsRefLat
print "Longitude referencia: " ,dmsRefLon
print "Altitude elipsoidal referencia: " , hRef
print "\n"

print "Erro Latitude: " , ddCalcLat - dmsRefLat
print "Erro Longitude: " , ddCalcLon - dmsRefLon
print "Erro Altitude Elispsoidal: " , hCalc - hRef
print "\n"

XYZcalc = deg2xyz(dmsRefLat,dmsRefLon,hRef)
print "X calculado: " , XYZcalc[0]
print "Y calculado: " , XYZcalc[1]
print "Z calculado: " , XYZcalc[2]

print "X referencia: " , X
print "Y referencia: " , Y
print "Z referencia: " , Z

print "Erro X: " , XYZcalc[0] - X
print "Erro Y: " , XYZcalc[1] - Y
print "Erro Z: " , XYZcalc[2] - Z

"""



"""
nmea2xyz function reads a nmea file and returns the epochs with XYZ coordinates

O PROBLEMA É O SINAL DE LATITUDE, LONGITUDE

SINAIS de preferencia apos as somas

VERIFICAR FLOAT

teSTAR O CALCULO
"""
def nmea2xyz(nmeafileName):
    result = []
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
                    h = float(dataArray[9]) + float(dataArray[11]) 
                    ddLat = dLat + mLat/60
                    ddLon = dLon + mLon/60
                    if dataArray[3] == "S":
                        ddLat = -ddLat
                    if dataArray[5] == "W":
                        ddLon = -ddLon
                    XYZnmea = deg2xyz(ddLat,ddLon,h)
                    epoch = (hTime, mTime, sTime, XYZnmea[0], XYZnmea[1], XYZnmea[2])
                    result.append( epoch )
        nmeaFile.close()
        return result
    
def nmea2deg(nmeafileName):
    result = []
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
                    h = float(dataArray[9]) + float(dataArray[11]) 
                    ddLat = dLat + mLat/60
                    ddLon = dLon + mLon/60
                    if dataArray[3] == "S":
                        ddLat = -ddLat
                    if dataArray[5] == "W":
                        ddLon = -ddLon
                    epoch = (hTime, mTime, sTime, ddLat, ddLon, h)
                    result.append( epoch )
        nmeaFile.close()
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

posAdjust function reads XYZ of a known location and compares it to a .POS file format

ERRO eh o calulado - referencia

calculado - erro = base

CNFERIR DADOS DO RELATORIO COM O RINEX
"""
def posAdjust(fileName):
    result = []
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
                Xerror = Xpos - Xonrj
                Yerror = Ypos - Yonrj
                Zerror = Zpos - Zonrj
                epoch = (hTime, mTime, sTime, Xerror, Yerror, Zerror)
                result.append( epoch )            
        posFile.close()
    return result

def posError(fileName):
    result = []
    Xonrj = 4283638.3579
    Yonrj = -4026028.8217
    Zonrj = -2466096.8361
    DDonrj = xyz2deg(Xonrj,Yonrj,Zonrj)
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
                DDpos = xyz2deg(Xpos,Ypos,Zpos)
                LatLonError = radianError(DDonrj[0],DDonrj[1],DDpos[0],DDpos[1])
                herror = DDpos[2] - DDonrj[2]
                epoch = (hTime, mTime, sTime, LatLonError[0], LatLonError[1], herror)
                result.append( epoch )            
        posFile.close()
    return result

#PROCURAR ESTACAO GPS
#VERIFICARRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
def nmeaAdjustionError(posFile,nmeafileName):
    result = []
    LatMarco = -(22 + 49/60.0 + 08.76793/3600)
    LonMarco = -(43 + 18/60.0 + 23.95193/3600)
    h = -1.461
    ref = posAdjust(posFile)
    nmea = nmea2xyz(nmeafileName)
    for coord in nmea:
        for error in ref:
            if error[0] == coord[0] and error[1] == coord[1] and error[2] == coord[2]:
                hTime = coord[0]
                mTime = coord[1]
                sTime = coord[2]
                Xadjusted = coord[3] - error[3]
                Yadjusted = coord[4] - error[4]
                Zadjusted = coord[5] - error[5]
                LatLon = xyz2deg(Xadjusted,Yadjusted,Zadjusted)
                error = radianError(LatMarco,LonMarco,LatLon[0],LatLon[1])
                herror = LatLon[2] - h
                adjusted = (hTime, mTime, sTime, error[0], error[1], herror)
                result.append( adjusted )            
    return result

    

def nmeaError(nmeafileName):
    result = []
    LatMarco = -(22 + 49/60.0 + 08.76793/3600)
    LonMarco = -(43 + 18/60.0 + 23.95193/3600)
    h = -1.461
    nmea = nmea2deg(nmeafileName)
    for coord in nmea:
        error = radianError(LatMarco,LonMarco,coord[3],coord[4])
        herror = coord[5] - h
        epoch = (coord[0], coord[1], coord[2], error[0], error[1], herror)
        result.append( epoch )
    return result


#r2 = posError('onrj2361_XYZ.pos')
#graph1(r2, "Erro do RINEX do dia")

r1 = posError('filteredRinex20_G_Debugg_XYZ.pos')
graph1(r1, "Erro do Rinex filtrado")

n1 = nmeaError('02_20170824135855.txt')
graph1(n1, "GPS NMEA 20 minutos")

x = nmeaAdjustionError('filteredRinex20_G_Debugg_XYZ.pos','02_20170824135855.txt')
graph1(x, "GPS NMEA 20 minutos Ajustado")

n2 = nmeaError('01_20170824122806.txt')
graph1(n2, "GPS NMEA 10 minutos")

n3 = nmeaError('00_20170824133538_Tools.txt')
graph1(n3, "NMEA Tools 10 minutos")


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