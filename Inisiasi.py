## CALCULATE FLOW DIRECTION AND FLOW TIME
## ADDITIONAL COMMENT
#  First Step

print("================================================================")
print("             CALCULATE FLOW DIRECTION AND FLOW TIME             ")
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
# ---INPUT DEM DATA AND REGIONAL ADMINISTRATION BOUNDARY---
# Data in this stage must satisfy the following requirements
# 1. DEM should have fixed resolution according to request ("DEM.tif")
# 2. Regional administration boundary should be provided using shapefile extension ("Regional.shp")
# 3. Regional administration boundary and DEM must use the same map projection or reference system
# }
print("Progress: Reading directory folder...\n")
env.workspace = "D:\\PROJECTS\\Python\\data"

all_start = time.time()

# Define raster size
RasterSize = 50

start = time.time()
#{
# ---PROCESS: CLIP RASTER---
# Extracting DEM with respect to the shape of administarion boundary
# }
print("Progress: Clipping raster to administration boundary...")
newDEM = arcpy.Clip_management ("DEM.tif", "11906591.4606255 -803846.750436296 12017785.6828144 -654609.794358843", "newDEM.tif", "regional.shp", "-1", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: RASTER CALCULATOR---
# Filling any pixel with null value to be zero: in case of data failures
# }
print("Progress: Repairing raster...")
repairDEM = Con(IsNull("newDEM.tif"),0,"newDEM.tif")
repairDEM.save("repairDEM.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: CLIP RASTER---
# Extracting DEM with respect to the shape of administarion boundary
# }
print("Progress: Reclipping data to administration boundary...")
maskDEM = arcpy.Clip_management ("repairDEM.tif", "11906591.4606255 -803846.750436296 12017785.6828144 -654609.794358843", "maskDEM.tif", "regional.shp", "-1", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: FILL---
# Repairing raster become smooth
# }
print("Progress: Filling raster...")
fillDEM = Fill("maskDEM.tif")
fillDEM.save("fillDEM.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: CLIP RASTER---
# Extracting DEM with respect to the shape of administarion boundary
# }
print("Progress: Reclipping data to administration boundary...")
maskDEM = arcpy.Clip_management ("fillDEM.tif", "11906591.4606255 -803846.750436296 12017785.6828144 -654609.794358843", "maskDEM.tif", "regional.shp", "-1", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: FLOW DIRECTION---
# Determining in which direction water will flow
# }
print("Progress: Calculating flow direction...")
FlowDir = FlowDirection("fillDEM.tif")
FlowDir.save("FlowDir.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: FLOW ACCUMULATION---
# Calculation accumulation from flow direction
# }
print("Progress: Calculating flow accumulation...")
FlowAcc = FlowAccumulation("FlowDir.tif")
FlowAcc.save("FlowAcc.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: DRAW BASIN---
print("Progress: Drawing basins...")
BasinRas = Basin ("FlowDir.tif")
BasinRas.save("Basin.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: CLIP BASIN---
print("Progress: Clipping basin to administration boundary...")
newBasin = arcpy.Clip_management ("Basin.tif", "11906591.4606255 -803846.750436296 12017785.6828144 -654609.794358843", "newBasin.tif", "regional.shp", "-1", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: EXPORT BASIN TO SHAPEFILE---
print("Progress: Exporting basin to shapefile...")
VectorBasin = arcpy.RasterToPolygon_conversion ("newBasin.tif", "VecBasin.shp", "SIMPLIFY", "Value")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: STREAM ORDER---
print("Progress: Calculating stream order...")
Stream_order = StreamOrder ("FlowDir.tif", "FlowDir.tif", "STRAHLER")
Stream_order.save("StreamOrder.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: SELECT BIGGER STREAM ORDER---
# Only stream order of more than 6
# }
print("Process: Selecting bigger stream order (Deleting orde 1-6)...")
ConStreamOrder = arcpy.gp.SetNull_sa("StreamOrder.tif", "StreamOrder.tif", "ConStrOrder.tif", "\"Value\" <=6")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: STREAM TO FEATURE---
# Create line vector for every stream order
# }
print("Progress: Converting raster to vector...")
Stream_to_feature = StreamToFeature ("ConStrOrder.tif", "FlowDir.tif", "StrToFeature.tif", "SIMPLIFY")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: DELETE EXISTING BUFFER---
print("Progress: Managing buffer polygon data...")
for i in range (7,16):
    if arcpy.Exists("feature"+str(i)+".shp"):
        arcpy.Delete_management("feature"+str(i)+".shp")
    if arcpy.Exists("buff"+str(i)+".shp"):
        arcpy.Delete_management("buff"+str(i)+".shp")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
# ---PROCESS: BUFFERING---
print("Progress: Input buffer radius...")
for i in range (7,16):
    arcpy.Select_analysis("StrToFeature.shp", "feature"+str(i)+".shp", "\"GRID_CODE\" = "+str(i))
    count = arcpy.GetCount_management ("feature"+str(i)+".shp")
    amount = count[0]
    if amount == '0':
        arcpy.Delete_management("feature"+str(i)+".shp")
    else:
        print("Orde-"+str(i)+" exists.")

# Define variables
combination = ""
ARCID = "ARCID \"ARCID\" true true false 10 Long 0 10 ,First,#"
GRID_CODE = "GRID_CODE \"GRID_CODE\" true true false 10 Long 0 10 ,First,#"
FROM_NODE = "FROM_NODE \"FROM_NODE\" true true false 10 Long 0 10 ,First,#"
TO_NODE = "TO_NODE \"TO_NODE\" true true false 10 Long 0 10 ,First,#"
K_VALUE = "K_VALUE \"K_VALUE\" true true false 19 Double 0 0 ,First,#"

# Define river widths
widths = [20,40,60,70,70,70,70,70,70,70,70,70,70,70,70]
K_value = [2.1,1.2,0.48,0.48,0.48,0.48,0.48,0.48,0.48]

for i in range (7,16):
    # buffering
    if arcpy.Exists("feature"+str(i)+".shp"):
        # for intersect
        combination = combination + "buff" + str(i) + ".shp;"
        ARCID = ARCID + ",buff"+str(i)+".shp,ARCID,-1,-1"
        GRID_CODE = GRID_CODE + ",buff"+str(i)+".shp,GRID_CODE,-1,-1"
        FROM_NODE = FROM_NODE + ",buff"+str(i)+".shp,FROM_NODE,-1,-1"
        TO_NODE = TO_NODE + ",buff"+str(i)+".shp,TO_NODE,-1,-1"
        K_VALUE = K_VALUE + ",buff"+str(i)+".shp,K_VALUE,-1,-1"
        print("\nProgress: Buffering Stream Order "+str(i)+"...\n")
        # Start buffering
        arcpy.Buffer_analysis ("feature"+str(i)+".shp", "buff"+str(i)+".shp", str(widths[i-7])+" Meters", "FULL", "ROUND", "LIST", "FID;ARCID;GRID_CODE;FROM_NODE;TO_NODE", "PLANAR")
        # Adding new field: K_value
        arcpy.AddField_management("buff"+str(i)+".shp", "K_VALUE", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        # Calculate field
        arcpy.CalculateField_management("buff"+str(i)+".shp", "K_VALUE", str(K_value[i-7]), "PYTHON", "")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

start = time.time()
#{
# ---PROCESS: MERGE---
# Combining all buffers
# }
field = ARCID + ";" + GRID_CODE + ";" + FROM_NODE + ";" + TO_NODE + ";" + K_VALUE + ";"
print("Process: Merging stream orders...")
Merge = arcpy.Merge_management(combination, "Merge.shp", field)
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# --PROCESS: RASTERING--
start = time.time()
print("Process: Rastering Merge.shp ...")
arcpy.PolygonToRaster_conversion("Merge.shp", "K_VALUE", "K_value.tif", "CELL_CENTER", "NONE", str(RasterSize))
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# --PROCESS: CREATE RANDOM POINT--
start = time.time()
print("Process: Create random point from merge.shp ...")
arcpy.CreateRandomPoints_management(env.workspace, "RandomPoint.shp", "Merge.shp", "0 0 250 250", "100", "0 Meters", "POINT", "0")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# --PROCESS: EXTRACT VALUE TO POINTS--
start = time.time()
print("Process: Extract value to points...")
arcpy.gp.ExtractValuesToPoints_sa("RandomPoint.shp", "K_value.tif", "K_val_points.shp", "NONE", "VALUE_ONLY")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# --PROCESS: CLEAR BLUNDER FROM POINTS--
start = time.time()
print("Process: Clear blunder from points...")
arcpy.Select_analysis("K_val_points.shp", "RandomPoint.shp", "\"RASTERVALU\" > 0")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# --PROCESS: KRIGING--
start = time.time()
print("Process: Kriging...")
arcpy.Kriging_3d("RandomPoint.shp", "RASTERVALU", "PointKriging.tif", "Spherical 410.646411", str(RasterSize), "VARIABLE 12", "")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# ---PROCESS: CLIPPING KRIGING---
start = time.time()
print("Process: Clipping kriging result...")
arcpy.Clip_management ("PointKriging.tif", "11906591.4606255 -803846.750436296 12017785.6828144 -654609.794358843", "ClipKvalue.tif", "regional.shp", "-1", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# --PROCESS: SLOPE--
start = time.time()
print("Process: Slope...")
arcpy.gp.Slope_sa("maskDEM.tif", "Slope.tif", "PERCENT_RISE", "1")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# ---PROCESS: CALCULATING V(x,y)---
start = time.time()
print("Process: Calculating S(x,y)...")
V = (0.3048*Raster("ClipKvalue.tif"))*(Raster("Slope.tif")^0.5)
V.save("V.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")

# --PROCESS: CALCULATIONG T(x,y)
start = time.time()
print("Process: Calculating T(x,y)...")
T = (RasterSize/Raster("V.tif"))
T.save("T.tif")
end = time.time()
print("Time consumed: "+ str(end-start) + " s.\n")


print("\nThe final product has been created: TrueVolume.shp")
print("\nALL PROCESS FINISHED")
print("================================================================")
all_end = time.time()
print("Total time consumed: " + str(all_end - all_start) + " s.\n")
