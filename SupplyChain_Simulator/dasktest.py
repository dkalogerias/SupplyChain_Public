# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 11:02:08 2018

@author: Woramanot
"""
import numpy as np
from dask import delayed, compute
from dask.distributed import Client
import dask.bag as db
#c = Client()
#c()
setsz = list([0,1])
def dasktest(x,y):
    y.append(x)
    return(y)
#print(str(dasktest(50)))
#dasktest = delayed(dasktest)
#print(str(dasktest(50).compute()))
IDList = [100,200,300]
DaskInput = db.from_sequence(IDList)
DaskOutout = DaskInput.map(lambda x: dasktest(x,setsz))
#out = DaskOutout.compute()

