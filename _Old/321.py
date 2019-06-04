# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 20:00:48 2019

@author: guidw
"""


for i, sat in enumerate(sats):
    if (i > 0) and (i % 12 == 0): # Checks to see if line has 12 satellites
        result = result + '\n' + (' ' * 32) # Adds new line with 32 blank spaces
    if sat > 64:
        Rsat = sat - 64 # Restores RINEX numbering for GLONASS satellite
        result = result + 'R%02d' % Rsat # Concatenates GLONASS satellite
    else:
        result = result + 'G%02d' % sat # Concatenates GPS satellite