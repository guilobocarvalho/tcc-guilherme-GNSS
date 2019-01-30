# -*- coding: utf-8 -*-

import math
import matplotlib.pyplot as plt
import xlsxwriter
from datetime import datetime, timedelta
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

Xriod = 4280294.8786
Yriod = -4034431.2247 
Zriod = -2458141.3800

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
SUPPORT FUNCTIONS:
getRinexTime
"""

def getRinexTime(line):
    hour = int(line[10:12])
    minute = int(line[13:15])
    second = int(round(float(line[16:21])))
    return datetime(1, 1, 1, hour, minute, second)

def getSatellites(line):
    result = []
    for i in range(0, len(line)/3): # Loops in bundles of 3 due to GXX RXX satellite number format
        c = line[i*3] # G for GPS and R for GLONASS
        d = line[i*3+1] # Tenths
        u = line[i*3+2] # Units
        result.append(c+d+u)
    return result

def getObservation(line):
    result = []
    pseudorange = float(line[0:14])
    doppler = float(line[54:62])
    result.append(pseudorange)
#    result.append(doppler)
#    result.append(measurements)
#    print measurements
    return pseudorange,doppler

def compareSatellite(epochsat,epochnum):
    for i in range(0,len(epochsat[epochnum][1])):
        print i
"""
FILE READING FUNCTIONS:
    
readNMEA
readRINEX
readPOS
"""

def readNMEA(fileName):
    result = []
    searchFix = True
    searchSat = False
    numberSat = 0
    satellites = []
    checkGPSsat = []
    hTime = 0
    mTime = 0
    sTime = 0
    nlines = 0
    with open(fileName, 'r') as nmeaFile:
        for line in nmeaFile:
            line = line.translate(None, '$')
            dataArray = line.split(',')
            if len(dataArray) == 0: # Skip blank lines
                continue
            sentenceId = dataArray[0]
            if searchFix and sentenceId == "GPGGA": # Searching for GNSS fixes
                fixQuality = dataArray[6]
                if fixQuality[0] == '1': # Check if solution exists
                    numberSat = int(dataArray[7]) # Number of satellites in fix
                    hTime = int(dataArray[1][0:2]) # Hour of fix
                    mTime = int(dataArray[1][2:4]) # Minute of fix
                    sTime = int(dataArray[1][4:6]) # Second of fix
                    searchSat = True # Start looking for fix satellites
                    searchFix = False
                    nlines = 0
                    satellites = []
            if searchSat and sentenceId == "GPGSA": # Searching for number of GPS satellites in fix
                fixType = int(dataArray[2]) # Checks if fix exists
                if fixType in [2, 3]:
                    checkGPSsat += [int(x) for x in dataArray[3:15] if x is not ''] # Add observed satellite numbers
                    satGPS = len(checkGPSsat)
                    
            if searchSat and sentenceId == "GNGSA": # Searching for GPS and GLONASS satellites in fix
                fixType = int(dataArray[2]) # Checks if fix exists
                if fixType in [2, 3]:
                    satellites += [int(x) for x in dataArray[3:15] if x is not ''] # Add observed satellite numbers
                    satGL = len(satellites) - satGPS
                    nlines += 1 # Looks at second line of observed satellites
                    
            if searchSat and sentenceId == "BDGSA": # Searching for Beidou satellites in fix
                fixType = int(dataArray[2]) # Checks if fix exists
                if fixType in [2, 3]:
                    satellites += [int(x) for x in dataArray[3:15] if x is not ''] # Add observed satellite numbers
                    satBD = len(satellites) - satGPS - satGL
                    nlines += 1 # Looks at second line of observed satellites
                    
            if searchSat and sentenceId == "GAGSA": # Searching for Beidou satellites in fix
                fixType = int(dataArray[2]) # Checks if fix exists
                if fixType in [2, 3]:
                    satellites += [int(x) for x in dataArray[3:15] if x is not ''] # Add observed satellite numbers
                    satGA = len(satellites) - satGPS - satGL - satBD
                    nlines += 1 # Looks at second line of observed satellites
                    if nlines == 5:
                        epoch = (hTime, mTime, sTime, numberSat, satellites,satGPS,satGL,satBD,satGA)
                        result.append( epoch )
                        if numberSat != len(satellites):
                            print "Incoherent satellite count at the line ", \
                            len(result), "\n" 
                        searchSat = False
                        searchFix = True # Starts looking for next fix
        nmeaFile.close()
    return result
fileName = 'SmoothingDebug.19o'
#def readRINEX(fileName):
result = []
epochsat = []
out = []
onHeader = True
currTime = None
searchTime = True
ignoreLines = 0
extendLines = 0
numSat = 0
epoch = 0
tuc = 0
sat = []
obs = []
observationlist = []
epochnum = 0
l1length = 0.19
with open(fileName, 'r') as rinexFile:
    for line in rinexFile:
        if onHeader: # Keeps Header and gets leap seconds
            out.append(line)
            if "LEAP SECONDS" in line:
                tuc = int(line[0:6]) # Gets Leap seconds
            if "END OF HEADER" in line:
                onHeader = False
        else: # Start reading epochs
            if searchTime:
                if ignoreLines == 0:
                    out.append(line)
#                        currTime = getRinexTime(line)
                    numSat = int(line[29:32]) # Number of satellites in epoch
                    extendLines =  (numSat - 1) / 12 # Check if epoch has more than 1 line of observed satellites
                    sat = getSatellites(line[32:]) # List satellites for this epoch
                    searchTime = False # Start reading each satellite observation
                    count = 0
                    obs[:] = []
                    epochsat[:] = []
                else:
                    ignoreLines -= 1 # Counts down lines that need to be skipped
                    continue
                if searchTime == False and extendLines ==0:
                    epoch = (epochnum,sat)
                    epochsat.append(epoch)
                    print epochsat
            else: # Start reading each satellite observation
                if extendLines > 0: # Read extra observed satellite line
                    result.append(line)
                    extendLines -= 1
                    sat = sat + getSatellites(line[32:]) # concatenates second satellite line to first
#                    epoch = (epochnum,sat)
#                    epochsat.append(epoch)
#                    compareSatellite(epochsat,epochnum)
#                else:
#                    epoch = (epochnum,sat)
#                    epochsat.append(epoch)
#                    compareSatellite(epochsat,epochnum)
                if extendLines == 0:
                    pseudorange = float(line[0:14])
                    doppler = float(line[54:62])
                    measurement = (pseudorange,doppler)
                    obs.append(measurement)
                    count += 1
                    numSat -= 1
                    if numSat == 0: # END OF EPOCH: Finished reading all satellites
                        print 'end of epoch ',epochnum
                        observationlist.append(obs)
                        searchTime = True # Read new epoch
                        epochnum +=1
                    
    rinexFile.close()
#    with open(outfile, 'w') as outputFile:
#	    for line in result:
#	        outputFile.write(line)
#    return result


#rinex = readRINEX('SmoothingDebug.19o')

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
                    sat = int(dataArray[7])
                    ddLat = dLat + mLat/60
                    ddLon = dLon + mLon/60
                    if dataArray[3] == "S":
                        ddLat = -ddLat
                    if dataArray[5] == "W":
                        ddLon = -ddLon
                    epoch = (hTime, mTime, sTime, ddLat, ddLon, h,sat)
                    result.append( epoch )
        nmeaFile.close()
        return result
    
def errorNMEA(nmeafileName):
    result = []
    nmea = nmea2deg(nmeafileName)
    sat = readNMEA(nmeafileName)
    for coord in nmea:
        error = radianError(LatMarco,LonMarco,coord[3],coord[4])
        herror = coord[5] - hMarco
        epoch = (coord[0], coord[1], coord[2], error[0], error[1], herror,coord[6])
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

def errorPOSriod(fileName):
    result = []
    DDriod = xyz2deg(Xriod,Yriod,Zriod)
    XYZpos = pos2xyz(fileName)
    for coord in XYZpos:
        DDpos = xyz2deg(coord[3],coord[4],coord[5])
        LatLonError = radianError(DDriod[0],DDriod[1],DDpos[0],DDpos[1])
        herror = DDpos[2] - DDriod[2]
        
        epoch = (coord[0], coord[1], coord[2], LatLonError[0], LatLonError[1], herror)
        result.append( epoch )
    return result

def errorPOSsmartphone(fileName):
    result = []
    XYZpos = pos2xyz(fileName)
    for coord in XYZpos:
        DDpos = xyz2deg(coord[3],coord[4],coord[5])
        LatLonError = radianError(LatMarco,LonMarco,DDpos[0],DDpos[1])
        herror = DDpos[2] - hMarco
        
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
Statistical calculations
Calculates Averages, Root mean errors and standard deviation.
"""
def averageNMEA(fileName):
    nmeaCoords = nmea2deg(fileName)
    sumLat = 0
    sumLon = 0
    sumH = 0
    for coord in nmeaCoords:
        sumLat += coord[3]
        sumLon += coord[4]
        sumH += coord[5]
    averageLat = sumLat/len(nmeaCoords)
    averageLon = sumLon/len(nmeaCoords)
    averageH = sumH/len(nmeaCoords)
#    print averageLat
#    print averageLon
#    print averageH
    avgError = radianError(LatMarco,LonMarco,averageLat,averageLon)
    avgHerror = averageH - hMarco
    result = (avgError[0],avgError[1],avgHerror)
    print result
    return result
    
    

def averagePOS(fileName):
    XYZpos = pos2xyz(fileName)
    sumLat = 0
    sumLon = 0
    sumH = 0
    for coord in XYZpos:
        DDpos = xyz2deg(coord[3],coord[4],coord[5])
        sumLat += DDpos[0]
        sumLon += DDpos[1]
        sumH += DDpos[2]
    averageLat = sumLat/len(XYZpos)
    averageLon = sumLon/len(XYZpos)
    averageH = sumH/len(XYZpos)
#    print averageLat
#    print averageLon
#    print averageH
    avgError = radianError(LatMarco,LonMarco,averageLat,averageLon)
    avgHerror = averageH - hMarco
    result = (avgError[0],avgError[1],avgHerror)
    print result
    return result
    
def rmsNMEA(fileName):
    RMSvector = errorNMEA(fileName)
    squareSumLat = 0
    squareSumLon = 0
    squareSumH = 0
    for coord in RMSvector:
        squareSumLat += (coord[3])**2
        squareSumLon += (coord[4])**2
        squareSumH += (coord[5])**2
    RMSLat = math.sqrt((squareSumLat)/(len(RMSvector)-1))
    RMSLon = math.sqrt((squareSumLon)/(len(RMSvector)-1))
    RMSH = math.sqrt((squareSumH)/(len(RMSvector)-1))
#    print RMSLat
#    print RMSLon
#    print RMSH
    result = (RMSLat,RMSLon,RMSH)
    print result
    return result

def rmsPOS(fileName):
    RMSvector = errorPOSsmartphone(fileName)
    squareSumLat = 0
    squareSumLon = 0
    squareSumH = 0
    for coord in RMSvector:
        squareSumLat += (coord[3])**2
        squareSumLon += (coord[4])**2
        squareSumH += (coord[5])**2
    RMSLat = math.sqrt((squareSumLat)/(len(RMSvector)-1))
    RMSLon = math.sqrt((squareSumLon)/(len(RMSvector)-1))
    RMSH = math.sqrt((squareSumH)/(len(RMSvector)-1))
#    print RMSLat
#    print RMSLon
#    print RMSH
    result = (RMSLat,RMSLon,RMSH)
    print result
    return result

def sdNMEA(fileName):
    avg = averageNMEA(fileName)
    nmeaError = errorNMEA(fileName)
    squareSumLat = 0
    squareSumLon = 0
    squareSumH = 0    
    for coord in nmeaError:
        squareSumLat += (coord[3]-avg[0])**2
        squareSumLon += (coord[4]-avg[1])**2
        squareSumH += (coord[5]-avg[2])**2
    sdLat = math.sqrt(squareSumLat/len(nmeaError))
    sdLon = math.sqrt(squareSumLon/len(nmeaError))
    sdH = math.sqrt(squareSumH/len(nmeaError))
#    print sdLat
#    print sdLon
#    print sdH
    result = (sdLat,sdLon,sdH)
    print result
    return result

def sdPOS(fileName):
    avg = averagePOS(fileName)
    nmeaError = errorPOSsmartphone(fileName)
    squareSumLat = 0
    squareSumLon = 0
    squareSumH = 0    
    for coord in nmeaError:
        squareSumLat += (coord[3]-avg[0])**2
        squareSumLon += (coord[4]-avg[1])**2
        squareSumH += (coord[5]-avg[2])**2
    sdLat = math.sqrt(squareSumLat/len(nmeaError))
    sdLon = math.sqrt(squareSumLon/len(nmeaError))
    sdH = math.sqrt(squareSumH/len(nmeaError))
#    print sdLat
#    print sdLon
#    print sdH
    result = (sdLat,sdLon,sdH)
    print result
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
    worksheet.write(row, col+7, 'Total de Satelites')
    worksheet.write(row, col+8, 'GPS')
    worksheet.write(row, col+9, 'GLONASS')
    worksheet.write(row, col+10, 'BEIDOU')
    worksheet.write(row, col+11, 'GALILEO')
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


"""
print 'Standard Deviation NMEA'
sdNMEA('20190115_092503.txt')
print

print'Standard Deviation POS OFF'
sdPOS('20190115_LevantamentoCompleto_Iono OFF e Tropo OFF.pos')
print

print 'Standard Deviation POS Broad and Saas'
sdPOS('20190115_LevantamentoCompleto.pos')
print

print 'RMS NMEA'
rmsNMEA('20190115_092503.txt')
print

print 'RMS POS OFF'
rmsPOS('20190115_LevantamentoCompleto_Iono OFF e Tropo OFF.pos')
print

print 'RMS POS Broad and Saas'
rmsPOS('20190115_LevantamentoCompleto.pos')
print

print 'Average Error NMEA'
averageNMEA('20190115_092503.txt')
print

print 'Average Error POS OFF'
averagePOS('20190115_LevantamentoCompleto_Iono OFF e Tropo OFF.pos')
print

print 'Average Error POS Broad and Saas'
averagePOS('20190115_LevantamentoCompleto.pos')
print
"""

#averagePOS('20190115_LevantamentoCompleto_Iono OFF e Tropo OFF.pos')
#createExcel('20190117_064503.txt',errorNMEA('20190117_064503.txt'))
#createExcel('20190115_LevantamentoCompleto_Iono OFF e Tropo OFF.pos',errorPOSsmartphone('20190115_LevantamentoCompleto_Iono OFF e Tropo OFF.pos'))
#createExcel('ErrorNMEA',adjustmentErrorNMEA('filteredRinex20_G_Debugg_XYZ.pos','02_20170824135855.txt'))
#createExcelerrorNMEA('02_20170824135855.txt')
#print deg2xyz(-22.895700560001078, -43.22433159713865, 35.63634614087641)