# -------------------------------------------------------------------------------
# AnalyzeMapillaryPHotos.py
# Created on: 2017-07-30
# Authors: Jay Dahlstrom, Christian Matthews, Tommy Nguyen
# Contact: jaydahlstrom92@gmail.com, cmatthews@tutamail.com, tnguyen@tutamail.com
# Description: This tool (1) creates a raster heat map of input photos and
#              (2) a grid for a city and ranks the grids by capture priority.
# -------------------------------------------------------------------------------

# Import modules and settings
import arcpy
import time
start = time.time()

arcpy.env.workspace = arcpy.GetParameterAsText(0)
arcpy.env.overwriteOutput = True

# Get variables:
SFBoundary = arcpy.GetParameterAsText(1)
MPhotos = arcpy.GetParameterAsText(2)
KData = arcpy.GetParameterAsText(3)
BufferDist = arcpy.GetParameterAsText(4)
GridRanking = "GridRanking"
HeatMap = "HeatMap"
Grid = "in_memory\Grid"
KDataLayer = "in_memory\KDataLayer"
MPhotosLayer = "in_memory\MPhotosLayer"
KDataBuffer = "in_memory\KDataBuffer"
KDataBufferID = "KDataBufferID"
KDataBufferIDLayer = "in_memory\KDataBufferID_Layer"
KDataBufferID_Stat = "in_memory\KDataBufferID_Stat"

# Create heat map
if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
        arcpy.gp.KernelDensity_sa(MPhotos, "NONE", HeatMap, "100", "400", "SQUARE_METERS", "DENSITIES", "PLANAR")
        arcpy.CheckInExtension("Spatial")
else:
        raise LicenseError

# Clean-up input data
KDatacopy = "in_memory\KData1"
arcpy.CopyFeatures_management(KData, KDatacopy)
KData = KDatacopy

MPhotoscopy = "in_memory\MPhotos1"
arcpy.CopyFeatures_management(MPhotos, MPhotoscopy)
MPhotos = MPhotoscopy

for f in arcpy.ListFields(KData):
  if (f.type == 'OID' or f.type == 'Geometry'):
    print()
  else:
    arcpy.DeleteField_management(KData, f.name)
for f in arcpy.ListFields(MPhotos):
  if (f.type == 'OID' or f.type == 'Geometry'):
    print()
  else:
    arcpy.DeleteField_management(MPhotos, f.name)

# Create grid
arcpy.GridIndexFeatures_cartography(Grid, SFBoundary, "INTERSECTFEATURE", "NO_USEPAGEUNIT", "", "0.5 Miles", "0.5 Miles")

# Buffer known data
arcpy.Buffer_analysis(KData, KDataBuffer, str(BufferDist) + " Meters", "FULL", "ROUND", "NONE", "", "PLANAR")

# Select mapillary photos within buffer
arcpy.MakeFeatureLayer_management(MPhotos, MPhotosLayer) 
arcpy.SelectLayerByLocation_management(MPhotosLayer, "INTERSECT", KDataBuffer, "", "NEW_SELECTION", "NOT_INVERT")

# Get count of mapillary photos within buffer for each grid square
arcpy.SpatialJoin_analysis(Grid, MPhotosLayer, GridRanking)

# Clip buffer to grid
arcpy.Identity_analysis(KDataBuffer, GridRanking, KDataBufferID, "ALL", "", "NO_RELATIONSHIPS")

# Delete clipped buffers outside grid
arcpy.MakeFeatureLayer_management(KDataBufferID, KDataBufferIDLayer)
arcpy.SelectLayerByAttribute_management(KDataBufferIDLayer, "NEW_SELECTION", "FID_GridRanking = -1")
arcpy.DeleteFeatures_management(KDataBufferIDLayer)

# Sum buffer by grid number
arcpy.Statistics_analysis(KDataBufferIDLayer, KDataBufferID_Stat, "Shape_Area SUM", "PageNumber")

# Get area values for grids
arcpy.JoinField_management(GridRanking, "PageNumber", KDataBufferID_Stat, "PageNumber", "SUM_Shape_Area")

# Add fields to grid feature class
arcpy.AddField_management(GridRanking, "MCE_Photo_Count", "DOUBLE")
arcpy.AddField_management(GridRanking, "MCE_Shape_Area", "DOUBLE")
arcpy.AddField_management(GridRanking, "Priority", "DOUBLE")

# Calculate max values for area and photos
MaxArea = []  
rows = arcpy.SearchCursor(GridRanking)  
for row in rows:  
    MaxArea.append(row.getValue("SUM_Shape_Area"))  
del rows            
MaxArea.sort()    
MaxArea = MaxArea[-1]

MaxPhotos = []  
rows = arcpy.SearchCursor(GridRanking)  
for row in rows:  
    MaxPhotos.append(row.getValue("Join_Count"))  
del rows            
MaxPhotos.sort()    
MaxPhotos = MaxPhotos[-1]

# MCE calculation/priority ranking
arcpy.CalculateField_management(GridRanking, "MCE_Photo_Count", "1-([Join_Count]/ " + str(MaxPhotos)+")", "VB", "")
arcpy.CalculateField_management(GridRanking, "MCE_Shape_Area", "[SUM_Shape_Area]/ " + str(MaxArea), "VB", "")
arcpy.CalculateField_management(GridRanking, "Priority", "(0.5* [MCE_Photo_Count])+(0.5* [MCE_Shape_Area])", "VB", "")

# Cleanup
arcpy.Delete_management(KDataBufferID)
end = time.time()
print("Completed in "+ str(round(end - start,0))+" seconds")
