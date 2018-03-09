# -*- coding: utf-8 -*-
# Standard Libraries  
import numpy as np
import time as time
import datetime as dt
import matplotlib.pyplot as mp
import copy as cp
# Custom Libraries
from dataPrep import *
from SupplierClasses import Supplier, LocalShipment
# Load delayed from dask
from dask import compute, delayed
from Functions import *
import dask.bag as db
###############################################################################
print('\n===============================================')
print()
# Specify the Supplier Horizon (later, make this user input)
H = 13
# Specify the total chain time (also user input, later)
T = 100
print('Supplier Horizon Length (Days): ', H)
print('Total Supply Chain Operation (Days): ', T)
print()
# Import Supply Chain data from file Chain.txt (provided)
# Also, perform data preparation
SupplierDict, maxLagTotal = dataPrep(H)

#######################################
#Create IDList of length 485
IDList = []
with open('ValueRecorder.pf') as f:
    for line in f:
        data = line.split()
        IDList.append(int(data[0]))
#######################################
#######################################################
def ParallelUpdate(ID):
    #print('Day', t, '/ Updating Suppler ID:', int(ID))
    # Get label of parent to current Supplier
    TheParent = SupplierDict[ID].ParentLabel
    # Get the plans from all children to current Supplier
    tempSpec = dict()
    # ALSO: Compute TOTAL input inventory for current Supplier (with no children)
    tempTotalInv = 0
    if SupplierDict[ID].NumberOfChildren != 0:
        for child in SupplierDict[ID].ChildrenLabels:
            tempSpec[child] = SupplierDict[child].DownStream_Info_PRE
            tempTotalInv += SupplierDict[ID].InputInventory[child]
            # ALSO: Write InputInventoryFile for current Supplier (for PilotView)
        InputInventoryFile.write(' '.join([str(int(SupplierDict[ID].Label)), \
                                           str(int(SupplierDict[ID].Label)), \
                                           str(24 * 60 * t), str(24 * 60), \
                                           str(int(SupplierDict[ID].OutputInventory)), '\n']))
                                           #str(int(tempTotalInv)), '\n']))
     
            # ALSO: Write ValueInputInventoryFile for current Supplier (for PilotView)
        ValueInputInventoryFile.write(' '.join([str(int(SupplierDict[ID].Label)), \
                                                str(int(SupplierDict[ID].Label)), \
                                                str(24 * 60 * t), str(24 * 60), \
                                                str(int(SupplierDict[ID].OutputInventory)*int(np.minimum(500,SupplierDict[ID].Value))), '\n']))
                                                #str(int(tempTotalInv)*int(SupplierDict[ID].Value)), '\n']))
       
    # Produce parts for today and update Supplier
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
    SupplierDict[ID].ProduceParts(SupplierDict[TheParent] if TheParent != -1 else -1,
                DataFromChildren = tempSpec,
                DataFromParent = SupplierDict[TheParent].UpStream_Info_PRE[ID] if TheParent != -1 else RootPlan[t : t + H])
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
    
#############################################################################################





# Initialize header files for PilotView
# Top level parameter file
SCParFile = open('PilotView/SupplyChainParameters.pf','w')
SCParFile.write(''.join(['Void\n',
                         'Locations.pf\n',
                         dt.datetime.now().strftime('%B %d %Y %I:%M %p'), '\n',
                         str(T * 24), '\n',
                         str(24 * 60), '\n',
                         'PartFlow PartFlow_Header.pf PartFlow_Data.pf', '\n',
                         'InputInventory InputInventory_Header.pf InputInventory_Data.pf', '\n',
                         'UnMet UnMet_Header.pf UnMet_Data.pf', '\n',
                         'ValueUnMet ValueUnMet_Header.pf ValueUnMet_Data.pf', '\n',
                         'ValueFlow ValueFlow_Header.pf ValueFlow_Data.pf', '\n',
                         'ValueInputInventory ValueInputInventory_Header.pf ValueInputInventory_Data.pf', '\n',
                         'Hiccup Hiccup_Header.pf Hiccup_Data.pf', '\n',
                         ]))
SCParFile.close()
# PartFlow header file
PartFlowHeaderFile = open('PilotView/PartFlow_Header.pf','w')
PartFlowHeaderFile.write('From To TIME Duration FLOW')
PartFlowHeaderFile.close()
# InputInventory header file
PartFlowHeaderFile = open('PilotView/InputInventory_Header.pf','w')
PartFlowHeaderFile.write('From To TIME Duration FLOW')
PartFlowHeaderFile.close()
# UnMet demand header file
PartFlowHeaderFile = open('PilotView/UnMet_Header.pf','w')
PartFlowHeaderFile.write('From To TIME Duration FLOW')
PartFlowHeaderFile.close()
# ValueFlow demand header file
PartFlowHeaderFile = open('PilotView/ValueFlow_Header.pf','w')
PartFlowHeaderFile.write('From To TIME Duration FLOW')
PartFlowHeaderFile.close()
# ValueFlow demand header file
PartFlowHeaderFile = open('PilotView/ValueInputInventory_Header.pf','w')
PartFlowHeaderFile.write('From To TIME Duration FLOW')
PartFlowHeaderFile.close()
# ValueUnmet demand header file
PartFlowHeaderFile = open('PilotView/ValueUnMet_Header.pf','w')
PartFlowHeaderFile.write('From To TIME Duration FLOW')
PartFlowHeaderFile.close()
# Hiccup header file
PartFlowHeaderFile = open('PilotView/Hiccup_Header.pf','w')
PartFlowHeaderFile.write('From To TIME Duration FLOW')
PartFlowHeaderFile.close()
###############################################################################
#                      Ready to execute the main Loop                         #
###############################################################################
# Create an empty list for parts
PartList = list()
# Initialize extended plan
RootPlan = np.zeros((T + H))
# Fixed Root Plan
# This should be given
RootPlan[0: T] = np.ones((T))
# Auxiliary end of plan; All zeros
RootPlan[T: ] = 0
# Start Simulation
print('\nSimulation Started...')
# At each time step
start = time.time() # Also start measuring total time
PartFlowFile = open('PilotView/PartFlow_Data.pf','w') # Create and open file (for PilotView)
InputInventoryFile = open('PilotView/InputInventory_Data.pf','w+') # Create and open file (for PilotView)
UnMetFile = open('PilotView/UnMet_Data.pf','w') # Create and open file (for PilotView)
ValueUnMetFile = open('PilotView/ValueUnMet_Data.pf','w') # Create and open file (for PilotView)
ValueInputInventoryFile = open('PilotView/ValueInputInventory_Data.pf','w+') # Create and open file (for PilotView)
ValueFlowFile = open('PilotView/ValueFlow_Data.pf','w') # Create and open file (for PilotView)
HiccupFile = open('PilotView/Hiccup_Data.pf','w') # Create and open file (for PilotView)
for t in range(T):
    startDay = time.time() # Also start measuring Supplier update time PER day
    print('============================================')
    print('Day', t)
    # Introduce temporary hiccup
    if t == 32:
        ID = 9781
        PastOutput = 3.5*170*int(np.minimum(1000,SupplierDict[ID].Value))
        PastDemand_Child = dict(zip(SupplierDict[ID].ChildrenLabels, \
                                     np.zeros((SupplierDict[ID].NumberOfChildren)))) 
        for child in SupplierDict[ID].ChildrenLabels:
                PastDemand_Child[child] = SupplierDict[child].ProductionPlan[1]
        PastDemand_Parent = int(SupplierDict[ID].ProductionPlan[1]*int(np.minimum(1000,SupplierDict[ID].Value)))
    if t >= 33 and t < 66:
        #ID = 10972
        #ID = 9334
        ID = 9781
        #ID = 12298
        store_KPro1 = cp.deepcopy(SupplierDict[ID].KPro)
        # set cost of production to unrealistic height
        SupplierDict[ID].KPro = 100000000
        
        HiccupFile.write(' '.join([str(int(SupplierDict[ID].Label)), \
                                                str(int(SupplierDict[ID].Label)), \
                                                str(24 * 60 * t), str(24 * 60), \
                                                str(PastOutput \
                                                    - int(SupplierDict[ID].OutputInventory)*int(np.minimum(1000,SupplierDict[ID].Value))), '\n']))
       
        for child in SupplierDict[ID].ChildrenLabels:
            HiccupFile.write(' '.join([str(int(child)), \
                                                  str(int(SupplierDict[ID].Label)), \
                                                  str(24 * 60 * t), str(24 * 60), \
                                                  str(int(PastDemand_Child[child]*min(SupplierDict[child].Value,1000)\
                                                          - SupplierDict[child].ProductionPlan[0]*min(SupplierDict[child].Value,1000)\
                                                      )), '\n']))
        HiccupFile.write(' '.join([str(int(SupplierDict[ID].ParentLabel)), \
                                               str(int(SupplierDict[ID].Label)), \
                                               str(24 * 60 * t), str(24 * 60), \
                                               # Scale by 3.3 times to be comparable to ValuePartFlow
                                               str(PastDemand_Parent -\
                                                   int(SupplierDict[ID].ProductionPlan[0]*int(np.minimum(1000,SupplierDict[ID].Value)))\
                                                   ), '\n']))
        #ID = 11971
        #store_ProdCap2 = cp.deepcopy(SupplierDict[ID].KPro)
        #SupplierDict[ID].KPro = 100000000
        
    if t == 66:
        #ID = 9334
        ID = 9781
        #ID = 12298
        SupplierDict[ID].KPro = store_KPro1
        #ID = 11971
        #SupplierDict[ID].KPro = store_ProdCap2
    # Update shipment list for EACH supplier
    for ID, value in SupplierDict.items():
        if SupplierDict[ID].NumberOfChildren != 0:
            # Iterate in a COPY of the current ShipmentList  
            for shipment in SupplierDict[ID].ShipmentList_PRE[:]:
                # Update shipment in ShipmentList of current Supplier
                shipment.LocalShipmentUpdate(SupplierDict[ID])
        SupplierDict[ID].ShipmentList_POST = cp.deepcopy(SupplierDict[ID].ShipmentList_PRE)
    # Produce Parts (and "PRIVATELY" update attributes) for EACH Supplier
    
    ##################################################################################
    # Dask Parallelization 
    ##################################################################################
    #DaskInput = db.from_sequence(IDList)
    #DaskOutput = DaskInput.map(ParallelUpdate)
    #DaskOutput.compute()
    for ID in IDList:
       ParallelUpdate(ID)
    ####################################################################################################
    # End Dask Parallelization
    ####################################################################################################
        # Produce Parts (and "PRIVATELY" update attributes) for EACH Supplier
    #for ID, value in SupplierDict.items(): # This should be able to be performed in parallel
    #    #print('Day', t, '/ Updating Suppler ID:', int(ID))
    #    # Get label of parent to current Supplier
    #    TheParent = SupplierDict[ID].ParentLabel
    #    # Get the plans from all children to current Supplier
    #    tempSpec = dict()
    #    # ALSO: Compute TOTAL input inventory for current Supplier (with no children)
    #    tempTotalInv = 0
    #    if SupplierDict[ID].NumberOfChildren != 0:
    #        for child in SupplierDict[ID].ChildrenLabels:
    #            tempSpec[child] = SupplierDict[child].DownStream_Info_PRE
    #            tempTotalInv += SupplierDict[ID].InputInventory[child]
    #        # ALSO: Write InputInventoryFile for current Supplier (for PilotView)
    #        InputInventoryFile.write(' '.join([str(int(SupplierDict[ID].Label)), \
    #                                     str(int(SupplierDict[ID].Label)), \
    #                                     str(24 * 60 * t), str(24 * 60), \
    #                                     str(int(tempTotalInv)), '\n']))
    #    # Produce parts for today and update Supplier
    #    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
    #    SupplierDict[ID].ProduceParts(SupplierDict[TheParent] if TheParent != -1 else -1,
    #        DataFromChildren = tempSpec,
    #        DataFromParent = SupplierDict[TheParent].UpStream_Info_PRE[ID] if TheParent != -1 else RootPlan[t : t + H])
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
    # Update PRE variables with POST variables
    for ID, value in SupplierDict.items():
        SupplierDict[ID].ShipmentList_PRE = cp.deepcopy(SupplierDict[ID].ShipmentList_POST)
        SupplierDict[ID].DownStream_Info_PRE = cp.deepcopy(SupplierDict[ID].DownStream_Info_POST)
        SupplierDict[ID].UpStream_Info_PRE = cp.deepcopy(SupplierDict[ID].UpStream_Info_POST)
        # Write PartFlowFile for current Supplier (for PilotView)
        if SupplierDict[ID].NumberOfChildren != 0:
            # Initialize dictionary for keeping the flow of each child
            childrenFlows = dict(zip(SupplierDict[ID].ChildrenLabels, \
                                     np.zeros((SupplierDict[ID].NumberOfChildren)))) 
            # Iterate in a COPY of the current ShipmentList
            # For each shipment in ShipmentList, record its flow 
            for shipment in SupplierDict[ID].ShipmentList_PRE:
                childrenFlows[shipment.From] += shipment.Size # Update Flow
            # Write PartFlowFile (for PilotView)
            for child in SupplierDict[ID].ChildrenLabels:
                if childrenFlows[child] >= 1:
                    PartFlowFile.write(' '.join([str(int(child)), \
                                                 str(int(SupplierDict[ID].Label)), \
                                                 str(24 * 60 * t), str(24 * 60), \
                                                 str(int(childrenFlows[child])), '\n']))
                    # Write ValuePartFlowFile (for PilotView)
                    ValueFlowFile.write(' '.join([str(int(child)), \
                                                  str(int(SupplierDict[ID].Label)), \
                                                  str(24 * 60 * t), str(24 * 60), \
                                                  str(int(childrenFlows[child]*min(SupplierDict[child].Value,1000))), '\n']))
                                                  #str(int(childrenFlows[child]*min(SupplierDict[child].Value,max(SupplierDict[child].Value/10,10)))), '\n']))
                                                  
        # Write UnMetFile for current Supplier (for PilotView)
        if SupplierDict[ID].ParentLabel != -1:
            if SupplierDict[SupplierDict[ID].ParentLabel].CurrentUnMet != 0:
                UnMetFile.write(' '.join([str(int(SupplierDict[ID].ParentLabel)), \
                                          str(int(SupplierDict[ID].Label)), \
                                          str(24 * 60 * t), str(24 * 60), \
                                          # Scale by 330 times so it is comparable to PartFlow
                                          str(int(SupplierDict[SupplierDict[ID].ParentLabel].CurrentUnMet*33)), '\n']))
                # Write ValueUnMetFile for current Supplier (for PilotView)
                ValueUnMetFile.write(' '.join([str(int(SupplierDict[ID].ParentLabel)), \
                                               str(int(SupplierDict[ID].Label)), \
                                               str(24 * 60 * t), str(24 * 60), \
                                               # Scale by 3.3 times to be comparable to ValuePartFlow
                                               str(int(SupplierDict[SupplierDict[ID].ParentLabel].CurrentUnMet*int(np.minimum(1000,SupplierDict[ID].Value))*15)), '\n']))
        if SupplierDict[ID].ParentLabel == -1:
            UnMetFile.write(' '.join([str(int(SupplierDict[ID].Label)), \
                                      str(int(SupplierDict[ID].Label)), \
                                      str(24 * 60 * t), str(24 * 60), \
                                      # multiply by 2500 due to this data using same scale as Inventory in PilotView
                                      str(int(SupplierDict[ID].CurrentUnMet)*2500), '\n']))
            ValueUnMetFile.write(' '.join([str(int(SupplierDict[ID].Label)), \
                                           str(int(SupplierDict[ID].Label)), \
                                           str(24 * 60 * t), str(24 * 60), \
                                           # divide by 15 due to this data using same scale as Inventory in PilotView
                                           str(int(SupplierDict[ID].CurrentUnMet*int(np.minimum(1000,SupplierDict[ID].Value))*15)), '\n']))              
    endDay = time.time() # End measuring Supplier update time PER day
    print('Time Elapsed (Suppliers Updating):', round(endDay - startDay, 2), 'sec.')
    #if t>= 111: wait = input('PRESS ENTER TO CONTINUE.\n')
# endfor
# Note that best scale for non-value is 0.03 0.3
PartFlowFile.close()
InputInventoryFile.close()
UnMetFile.close()
ValueFlowFile.close()
ValueInputInventoryFile.close()
ValueUnMetFile.close()
HiccupFile.close()
end = time.time() # End measuring total time
print('\n... Done.')
print('===============================================')
print('Time Elapsed (total):', round(end - start, 2), 'sec.')
###############################################################################