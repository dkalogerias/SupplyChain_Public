# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 00:13:00 2018

@author: Woramanot
"""
a1 = []
a2 = []
a3 = []
a4 = []
a5 = []
with open('PilotView/UnMet_Data.pf') as f:
    for line in f:
        data = line.split()
        a1.append(int(data[0]))
        a2.append(int(data[1]))
        a3.append(int(data[2]))
        a4.append(int(data[3]))
        a5.append(int(data[4]))
        
UnMetFile = open('PilotView/UnMet_Data.pf','w') # Create and open file (for PilotView)
for i in range(0,len(a1)):
    UnMetFile.write(' '.join([str(a1[i]), \
                              str(a2[i]), \
                              str(a3[i]), str(a4[i]), \
                              str(int(a5[i])/10), '\n']))