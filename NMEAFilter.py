#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on 2017 - 07 - 04

Updated 2018 - 10 - 03

@author: Irving Badolato
"""

import sys
from datetime import datetime, timedelta


"""
#getRinexTime function creates python datetime object from a Rinex line
"""
# 
def getRinexTime(line):
    hour = int(line[10:12])
    minute = int(line[13:15])
    second = int(line[16:18])
    return datetime(1, 1, 1, hour, minute, second)

"""
#getNmeaTime function creates python datetime object from nmea line where:

0 = hour
1 = minutes
2 = seconds
tuc = leapseconds to tuc
"""
def getNmeaTime(nmea, tuc):
    time = datetime(1, 1, 1, nmea[0], nmea[1], nmea[2])
    return time - timedelta(hours=0) + timedelta(seconds=18);

"""
#getSatellites function adjusts RINEX satellite number to match NMEA satellite number format
"""
def getSatellites(line):
    result = []
    for i in range(0, len(line)/3): # Loops in bundles of 3 due to GXX RXX satellite number format
        c = line[i*3] # G for GPS and R for GLONASS
        d = line[i*3+1] # Tenths
        u = line[i*3+2] # Units
        if not (c in ['g','G', 'r', 'R']):
            break
        elif c in ['g','G']:
            result.append( int(d)*10 + int(u) )
        else:
            result.append( int(d)*10 + int(u) + 64) #64 is added to match NMEA numbering for GLONASS
    return result

"""
#getRinexEpoch function compares RINEX observed satellites to NMEA's, removing the ones that do not match
"""
def getRinexEpoch(line, rsats, nsats):
    result = line # inserts first 29 spaces related to the epoch
    sats = []
    for rsat in rsats: # Checking each RINEX satellite
        for nsat in nsats: # checks each NMEA satellite
            if rsat == nsat:
                sats.append(rsat) # Includes RINEX satellite in the list
    for nsat in nsats:
        if not (nsat in sats): # Checks if all NMEA satellites were also observed in RINEX list
            print "Alert: Satellite ", nsat," in NMEA not found in RINEX.", line
    result = result + '%3d' % len(sats) # Adds total number of satellites that match
    for i, sat in enumerate(sats):
        if (i > 0) and (i % 12 == 0): # Checks to see if line has 12 satellites
            result = result + '\n' + (' ' * 32) # Adds new line with 32 blank spaces
        if sat > 64:
            Rsat = sat - 64 # Restores RINEX numbering for GLONASS satellite
            result = result + 'R%02d' % Rsat # Concatenates GLONASS satellite
        else:
            result = result + 'G%02d' % sat # Concatenates GPS satellite
    result = result + '\n'
    return result

"""
readNMEA é função para leitura de fonte de dados NMEA e listagem dos satélites
           usados em cada época, cuja solução foi considerada fixada.
         
No formato NMEA são inseridas diversas linhas (sentenças) com formatos
distintos, dos quais nos interessam os formatos a saber:
    
Formato da sentença $GPGSA
     Posição:     Domínio:
     0        $GPGSA => Satellite status
     1        A or M (for Automatic or Manual) selection of 2D or 3D fix 
     2        3D fix - values include: 1 = no fix
                                       2 = 2D fix
                                       3 = 3D fix
     3 - 14   PRNs of satellites used for fix (space for 12) 
     15       PDOP (dilution of precision) 
     16       Horizontal dilution of precision (HDOP) 
     17       Vertical dilution of precision (VDOP)
     18       The checksum data, always begins with *

Formato da sentença $GPGGA
     Posição:     Domínio:
     0            $GPGGA => Global Positioning System Fix Data
     1            Fix taken at UTC   (123519 => 12:35:19)
     2            Latitude  ( 4807.038 => 48 deg 07.038')
     3            (N or S)
     4            Longitude (01131.000 => 11 deg 31.000')
     5            (E or W)
     6            Fix quality: 0 = invalid
                               1 = GPS fix (SPS)
                               2 = DGPS fix
                               3 = PPS fix
			                  4 = Real Time Kinematic
			                  5 = Float RTK
                               6 = estimated (dead reckoning) (2.3 feature)
			                  7 = Manual input mode
			                  8 = Simulation mode
     7            Number of satellites being tracked
     8            Horizontal dilution of position
     9            Altitude, Meters, above mean sea level
     10           Metric unit
     11           Height of geoid (mean sea level) above WGS84 ellipsoid
     12           Metric unit
     13           Time in seconds since last DGPS update
     14           DGPS station ID number
     15           The checksum data, always begins with *
"""
def readNMEASimple(fileName):
    result = []
    searchFix = True
    searchSat = False
    numberSat = 0
    satellites = []
    hTime = 0
    mTime = 0
    sTime = 0
    with open(fileName, 'r') as nmeaFile:
        for line in nmeaFile:
            line = line.translate(None, '$')
            dataArray = line.split(',')
            if len(dataArray) == 0: # Pula linhas vazias
                continue
            sentenceId = dataArray[0]
            if searchFix and sentenceId == "GPGGA":
                fixQuality = int(dataArray[6])
                if fixQuality == 1:
                    numberSat = int(dataArray[7])
                    hTime = int(dataArray[1][0:2])
                    mTime = int(dataArray[1][2:4])
                    sTime = int(dataArray[1][4:6])
                    searchSat = True
                    searchFix = False
            if searchSat and sentenceId == "GPGSA":
                fixType = int(dataArray[2])
                if fixType in [2, 3]:
                    satellites = [int(x) for x in dataArray[3:15] if x is not '']
                    if numberSat != len(satellites):
                        print "Incoherent satellite count at the line ", \
                        len(result), "\n" 
                    epoch = (hTime, mTime, sTime, numberSat, satellites)
                    result.append( epoch )
                    searchSat = False
                    searchFix = True
        nmeaFile.close()
    return result



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


"""
readRINEX is a function that reads RINEX data and lists the observed satellites for each epoch.
"""
def filterRINEX(fileName, nmea):
    result = []
    onHeader = True
    currNmea = None
    nmeaTime = None
    currTime = None
    searchTime = True
    ignoreLines = 0
    extendLines = 0
    numSat = 0
    epoch = 0
    tuc = 0
    sat = []
    out = []
    with open(fileName, 'r') as rinexFile:
        for line in rinexFile:
            if onHeader: # Keeps Header and gets leap seconds
                result.append(line)
                if "LEAP SECONDS" in line:
                    tuc = int(line[0:6]) # Gets Leap seconds
                if "END OF HEADER" in line:
                    onHeader = False
                    currNmea = nmea.pop(0) # List a file and read first line
            else: # Start reading epochs
                if searchTime:
                    if ignoreLines == 0:
                        currTime = getRinexTime(line)
                        nmeaTime = getNmeaTime(currNmea, tuc)
                        numSat = int(line[29:32]) # Number of satellites in epoch
                        extendLines =  (numSat - 1) / 12 # Check if epoch has more than 1 line of observed satellites
                        if (currTime < nmeaTime): # Checks if RINEX epoch matches NMEA epoch
                            ignoreLines = numSat + extendLines # Skip satellite observation lines
                        elif (currTime >= nmeaTime): # Checks if RINEX epoch matches NMEA epoch
                            while(currTime > nmeaTime): # Gets new NMEA line If RINEX epoch is ahead of NMEA epoch
                                if len(nmea) == 0:
                                    break
                                currNmea = nmea.pop(0) # Get new NMEA line
                                nmeaTime = getNmeaTime(currNmea, tuc)
                            if (currTime == nmeaTime): #Epochs match
                                epoch = line[0:29] # Reads epoch date
                                sat = getSatellites(line[32:]) # List satellites for this epoch
                                searchTime = False # Start reading each satellite observation
                            else:
                                break
                    else:
                        ignoreLines -= 1 # Counts down lines that need to be skipped
                        continue
                else: # Start reading each satellite observation
                    if extendLines > 0: # Read extra observed satellite line
                        extendLines -= 1
                        sat = sat + getSatellites(line[32:]) # concatenates second satellite line to first
                    else:                        
                        if len(out) == 0:
                            out.append(getRinexEpoch(epoch, sat, currNmea[4])) # Compares RINEX observed satellites to NMEA's
                        if sat[-numSat] in currNmea[4]: # Test Sat to append in out
                            out.append(line[:32])
                        numSat -= 1
                        if numSat == 0: # Finished reading all satellites
                            searchTime = True
                            while (len(out) > 0):
                                result.append(out.pop(0)) # pop out to result, resetting out
                            if len(nmea) == 0:
                                break
                            currNmea = nmea.pop(0) # Get new NMEA line
        rinexFile.close()
    return result


import sys
old_stdout = sys.stdout
log_file = open("log.txt","w")
sys.stdout = log_file

isDebug = True
if isDebug:
	#NMEA = readNMEA('NMEA_Tools.txt')
	NMEA  = readNMEA('20190115_092503.txt')
	#for item in NMEA:
	    #if (item[2]+18) % 15 == 0:
	    #   print item
#	RINEX = filterRINEX('onrj2361.17o', NMEA)
#	with open('filteredRinex20_G_Debugg11111.txt', 'w') as outputFile:
#	    for line in RINEX:
#	        outputFile.write(line)
#	outputFile.close()


if len(sys.argv) == 4:
	NMEA = readNMEA(sys.argv[1])
	RINEX = filterRINEX(sys.argv[2], NMEA)
	with open(sys.argv[3], 'w') as outputFile:
		for line in RINEX:
			outputFile.write(line)
		outputFile.close()
elif not isDebug:
	print "Usage: \n"
	print "\tpython NMEAFilter <NMEA_filename> <RINEX_filename> <output_filename>\n"

print "Program has finished!"
sys.stdout = old_stdout
log_file.close()
