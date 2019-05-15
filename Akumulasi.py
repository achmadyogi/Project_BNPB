## CALCULATE TOTAL ACCUMULATION EACH 3 HOURS
#  Second Step

print("================================================================")
print("                       TOTAL ACCUMULATION                       ")
print("================================================================")

print("Progress: Preparing libraries...\n")
# Define libraries
import time
import os, glob, shutil
import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("spatial")

#{
# ---INPUT DATA---
# FlowDir.tif
# runoff.tif
# }
print("Progress: Reading directory folder...\n")
env.workspace = "D:\\PROJECTS\\Python\\data"

iteration = 127

start = time.time()
# ---PROCESS: FLOW ACCUMULATION---
print("Progress: Calculating flow accumulation...")

for i in range(1,iteration+1):
    start_ = time.time()
    if i == 1:
        # Flow Accumulation
        arcpy.gp.FlowAccumulation_sa("FlowDir.tif","FlowAcc1.tif","FlowAccrunoff.tif","FLOAT")
    elif i%2 == 0:
        # Flow Accumulation
        arcpy.gp.FlowAccumulation_sa("FlowDir.tif","FlowAcc2.tif","FlowAcc1.tif","FLOAT")
    else:
        # Flow Accumulation
        arcpy.gp.FlowAccumulation_sa("FlowDir.tif","FlowAcc1.tif","FlowAcc2.tif","FLOAT")
    end_ = time.time()
    print("Time consumed: "+ str(end_-start_) + " s.\n")

end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")