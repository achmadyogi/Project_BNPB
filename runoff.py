## CALCULATE RUNOFF
#  Second Step

print("================================================================")
print("                        CALCULATE RUNOFF                        ")
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
# The following data are required:
# 1. Curve Number (CN) in the region (CN.tif) using Mercator Projection
# 2. Results from previous process:
#    - Flow direction raster (FlowDir.tif)
#    - Regional boundary administration using Mercator Projection (MercRegional.shp)
# }
print("Progress: Reading directory folder...\n")
env.workspace = "D:\\PROJECTS\\Python\\data"

all_start = time.time()

# Define raster size
RasterSize = 50

start = time.time()
#--PROCESS: PROJECT RASTER
print("Progress: Project raster rain...")
arcpy.ProjectRaster_management("Rain.tif", "MercRain.tif", "PROJCS['WGS_1984_World_Mercator',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],UNIT['Meter',1.0]]", "NEAREST", str(RasterSize) + " " + str(RasterSize), "", "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: CLIPPING RAINFALL---
print("Process: Clipping rainfall...")
arcpy.gp.ExtractByMask_sa("MercRain.tif", "regional.shp", "ClipRain.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: RESAMPLE RAINFALL---
print("Process: Resampling rainfall raster (+- " + str(RasterSize) + "meter)...")
arcpy.Resample_management("ClipRain.tif", "ResRain.tif", str(RasterSize) + " " + str(RasterSize), "NEAREST")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: CALCULATING S(x,y)---
print("Process: Calculating S(x,y)...")
S = (1000/Raster("CN.tif"))-10
S.save("S.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: REPAIRING S RASTER
print("Progress: Repairing raster S...")
repairS = Con(IsNull("S.tif"),0,"S.tif")
repairS.save("repairS.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# --PROCESS: RECLIPPING RASTER S
print("Progress: Reclipping raster S...")
arcpy.Clip_management ("repairS.tif", "11906591.4606255 -803846.750436296 12017785.6828144 -654609.794358843", "FixS.tif", "regional.shp", "-1", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: CALCULATING Q(x,y)---
print("Process: Calculating Q(x,y)...")
runoff = (Raster("ResRain.tif")-0.2*Raster("FixS.tif"))*(Raster("ResRain.tif")-0.2*Raster("FixS.tif"))/(Raster("ResRain.tif")-0.8*Raster("FixS.tif"))
runoff.save("Q.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: FLOW ACCUMULATION---
print("Progress: Calculating flow accumulation...")
arcpy.gp.FlowAccumulation_sa("FlowDir.tif","FlowAccrunoff.tif","Q.tif","FLOAT")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: CALCULATING RUNOFF VOLUME---
print("Process: Calculating Runoff Volume...")
runoffvol = (Raster("FlowAccrunoff.tif")*RasterSize*RasterSize)
runoffvol.save("RunoffVolume.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

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

print("The final product has been created: RunoffVolume.tif")
print("ALL PROCESSES FINISHED")
print("================================================================")

all_end = time.time()

print("Time consumed: "+ str(all_start - all_end) + " s.\n")