# -*- coding: utf-8 -*-

import math
import matplotlib.pyplot as plt
import xlsxwriter
import datetime
import inspect
from numbers import Number

a = 6378137.0
e2 = (0.08181919104282)**2

LatMarco = -(22 + 49/60.0 + 08.76793/3600)
LonMarco = -(43 + 18/60.0 + 23.95193/3600)
hMarco = -1.461

Xonrj = 4283638.3579
Yonrj = -4026028.8217
Zonrj = -2466096.8361

""""
MATH FUNCTIONS:

deg2xyz
xyz2deg
radianError
"""
def deg2xyz(ddLat,ddLon,h): #VALIDADO
    radLat = math.radians(ddLat)
    radLon = math.radians(ddLon)
    N = ( a / ((1-(e2)*(math.sin(radLat))**2)**(0.5)))
    X = (N+h)*math.cos(radLat)*math.cos(radLon)
    Y = (N+h)*math.cos(radLat)*math.sin(radLon)
    Z = (N*(1-e2)+h)*math.sin(radLat)
    XYZ = (X,Y,Z)
    return XYZ

def xyz2deg(X,Y,Z): #VALIDADO
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

def radianError(phi1,lamb1,phi2,lamb2): #VALIDADO
    phiAvg = math.radians((phi2-phi1)/2)
    phi1 = math.radians(phi1)
    lamb1 = math.radians(lamb1)
    phi2 = math.radians(phi2)
    lamb2 = math.radians(lamb2)
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
      
    Ssimples = M * (phi2-phi1)
    
    S = a*(1-e2)*(phiA - phiB + phiC - phiD + phiE - phiF) #Comrpimento de arco de Meridiano
    L = N*math.cos(phiAvg)*(lamb2-lamb1)#Comprimento de arco de Paralelo

    result = (S,L)

    return result

"""
NMEA FILE PROCESSING

This step reads the nmea file and calculates the error from the smartphone solution.
"""

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
    
def errorNMEA(nmeafileName):
    result = []
    nmea = nmea2deg(nmeafileName)
    for coord in nmea:
        error = radianError(LatMarco,LonMarco,coord[3],coord[4])
        herror = coord[5] - hMarco
        epoch = (coord[0], coord[1], coord[2], error[0], error[1], herror)
        result.append( epoch )
    return result

"""
.POS FILE PROCESSING

This step reads a .POS file in XYZ format and calculates the error from the survey
"""

def pos2xyz(fileName):
    result = []
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
                epoch = (hTime, mTime, sTime, Xpos, Ypos, Zpos)
                result.append( epoch )            
        posFile.close()
    return result

def errorPOS(fileName):
    result = []
    DDonrj = xyz2deg(Xonrj,Yonrj,Zonrj)
    XYZpos = pos2xyz(fileName)
    for coord in XYZpos:
        DDpos = xyz2deg(coord[3],coord[4],coord[5])
        LatLonError = radianError(DDonrj[0],DDonrj[1],DDpos[0],DDpos[1])
        herror = DDpos[2] - DDonrj[2]
        
        epoch = (coord[0], coord[1], coord[2], LatLonError[0], LatLonError[1], herror)
        result.append( epoch )
    return result

"""
ERROR ADJUSTMENT

This final step adjusts the NMEA coordinates to the POS file
"""
def nmea2xyz(nmeafileName):
    result = []
    nmeaDD = nmea2deg(nmeafileName)
    for coord in nmeaDD:
        XYZnmea = deg2xyz(coord[3],coord[4],coord[5])
        epoch = (coord[0], coord[1], coord[2], XYZnmea[0], XYZnmea[1], XYZnmea[2])
        result.append( epoch )
    return result
        
def adjustmentNMEA(posFile,nmeafileName):
    result = []
    ref = pos2xyz(posFile)
    nmea = nmea2xyz(nmeafileName)
    for coord in nmea:
        for pos in ref:
            if pos[0] == coord[0] and pos[1] == coord[1] and pos[2] == coord[2]:
                hTime = coord[0]
                mTime = coord[1]
                sTime = coord[2]                
                Xerror = pos[3] - Xonrj
                Yerror = pos[4] - Yonrj
                Zerror = pos[5] - Zonrj
                
                Xadjusted = coord[3] - Xerror
                Yadjusted = coord[4] - Yerror
                Zadjusted = coord[5] - Zerror
                LatLon = xyz2deg(Xadjusted,Yadjusted,Zadjusted)
                adjusted = (hTime, mTime, sTime, LatLon[0],LatLon[1],LatLon[2])
                result.append( adjusted )            
    return result

def adjustmentErrorNMEA(posFile,nmeafileName):
    result = []
    nmea = adjustmentNMEA(posFile,nmeafileName)
    for coord in nmea:
        error = radianError(LatMarco,LonMarco,coord[3],coord[4])
        herror = coord[5] - hMarco
        epoch = (coord[0], coord[1], coord[2], error[0], error[1], herror)
        result.append( epoch )
    return result

"""
PLOTTING RESULTS

Either graphs or output to excel spreadsheets
"""
def createExcel(fileName,data):    
    cutfileName = fileName.split('.')
    excelfileName = cutfileName[0] + '.xlsx'
    workbook = xlsxwriter.Workbook(excelfileName)
    worksheet = workbook.add_worksheet()
    
    row = 0
    col = 0
    worksheet.write(row, col, 'HH')
    worksheet.write(row, col+1, 'MM')
    worksheet.write(row, col+2, 'SS')
    worksheet.write(row, col+3, 'Erro Latitude (m)')
    worksheet.write(row, col+4, 'Erro Longitude (m)')
    worksheet.write(row, col+5, 'Erro Altitude (m)')
    worksheet.write(row, col+6, 'HHMMSS')
    row += 1
    for epoch in data:
        col = 0
        for item in epoch:
            worksheet.write(row, col, item)
            col += 1
        time = (epoch[0]*10000 + epoch[1]*100 + epoch[2])
        worksheet.write(row, col, time)
        row += 1
        
    workbook.close()

createExcel('02_20170824135855.txt',errorNMEA('02_20170824135855.txt'))
createExcel('filteredRinex20_G_Debugg_XYZ.pos',errorPOS('filteredRinex20_G_Debugg_XYZ.pos'))
createExcel('ErrorNMEA',adjustmentErrorNMEA('filteredRinex20_G_Debugg_XYZ.pos','02_20170824135855.txt'))
#createExcelerrorNMEA('02_20170824135855.txt')
#print deg2xyz(-22.895700560001078, -43.22433159713865, 35.63634614087641)