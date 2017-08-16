### Authors: Tyler Buntain, Jay Dahlstrom, and Christian Matthews
### Date: November 11, 2016
### Geography 562
###
### Description: This script compares the location of Mapillary photos containing
### a certain object class to the nearest object in a known dataset.  For example
### Mapillary photos containing fire hydrants can be compared against a city managed
### dataset of fire hydrants.  If the known dataset is line feature class the segments
### are converted to points at a user defined distance to allow for a comparison
### between the Mapillary points and the known features.
###
### This script was designed to work with ArcGIS 10.4/10.5 and Python 2.7.10,
### the script may or may not work with other versions ArcGIS and will need to be
### refactored to work with newer versions of Python (if/when arcpy is updated to
### work with newer Python versions).

###
### import modules
###

import arcpy
import os
import sys
import shutil

###
### Parameters
###

# Dataset containing known locations of the object class
FcKnown = arcpy.GetParameterAsText(0)
# Type of Known feature class, either line if True or point if false
LineFeatureClass = arcpy.GetParameterAsText(1)
# Distance at which points will be created along each line segment
PointDistance = arcpy.GetParameterAsText(2)
# Shapefile of Mapillary photo locations of the object class
FcMapillary = arcpy.GetParameterAsText(3)


###
### Set work environment
###

arcpy.env.workspace = r'C:\Users\Jay Dahlstrom\OneDrive\Geog 569\Project\GeoJSON\working'
workspace = arcpy.env.workspace
arcpy.env.overwriteOutput = True

###
### Script Follows
###

def main(FcKnown, FcMapillary, LineFeatureClass, Distance):
    arcpy.AddMessage('Creating temporary working directory')
    TempPath = sys.path[0] + r"\tempDistance"
    CreateTempDirectory(TempPath)
    arcpy.AddMessage('Preparing the shapefiles for analysis')
    FcKnownAnalysis = PrepFeatureClasses(FcKnown, FcMapillary, LineFeatureClass, TempPath, Distance)
    ListKnown = []
    ListMapillary = []
    arcpy.AddMessage('Searching through the feature classes for X and Y values')
    SearchCursor(FcKnownAnalysis, ["POINT_X","POINT_Y"], ListKnown)
    SearchCursor(FcMapillary, ["POINT_X","POINT_Y", 'Key'], ListMapillary)
    arcpy.AddMessage('Calculating the shortest distance between each Mapillary point and known points')
    CalculateShortestDistance(ListMapillary, ListKnown)
    arcpy.AddMessage('Inserting the shortest distance values into the Mapillary feature class')
    InsertDistanceValues(ListMapillary)
    arcpy.AddMessage('Script finished successfully')

def CreateTempDirectory(Path):
    '''
    Function that creates a temporary working directory for the files
    used to calculate the distance between Mapillary and known points.
    Requires only a file path which is generated by the script and deletes
    an existing directory with the same name.
    '''
    if os.path.isdir(Path):
        shutil.rmtree(Path)
    os.makedirs(Path)

def PrepFeatureClasses(FcKnown, FcMapillary, LineFeatureClass, tempPath, Distance):
    '''
    Function that takes two input feature classes, the boolean is line type
    and the path to the temporary working folder.  If the known feature class
    contains lines a new feature class is created with points at a set distance.
    The spatial reference of the known feature class is also set to the same
    spatial reference as the Mapillary feature class.
    '''
    arcpy.AddXY_management(FcMapillary)
    MapillarySpatialRef = arcpy.Describe(FcMapillary).spatialReference
    FcKnownProjected = tempPath + r'\KnownProjected.shp'
    arcpy.Project_management(FcKnown, FcKnownProjected, MapillarySpatialRef)
    arcpy.AddMessage(LineFeatureClass)
    # If the known feature class contains lines create a new point feature class
    if LineFeatureClass == 'true':
        FcKnownPointProjected = tempPath + r'\KnowProjectedPoints.shp'
        arcpy.GeneratePointsAlongLines_management(FcKnownProjected, FcKnownPointProjected, "DISTANCE", Distance)
        arcpy.AddXY_management(FcKnownPointProjected)
        # Return the new point feature class for analysis
        arcpy.AddMessage(FcKnownPointProjected)
        return FcKnownPointProjected
    # If the known feature class contains points then add the X,Y values and return the same feature class
    else:
        arcpy.AddXY_management(FcKnownProjected)
        arcpy.AddMessage(FcKnownProjected)
        return FcKnownProjected

def SearchCursor(FeatureClass, Fields, OutList):
    '''
    Function that takes an input feature class, list of fields
    and an empty list and searches through the feature class returning
    the values for each of the fields by row and appends them as a nested
    list to the input list.
    '''
    with arcpy.da.SearchCursor(FeatureClass, Fields) as Cursor:
        for Row in Cursor:
            TempList = []
            # Add the items to a temp list which is then itself appended to the primary list
            # This is done for the insert cursor
            for Item in Row:
                TempList.append(Item)
            OutList.append(TempList)

def CalculateShortestDistance(MapillaryList, KnownList):
    '''
    Function that takes two input lists containing X,Y values and calculates
    the distance between each Mapillary point and the nearest known point.
    The shortest distance is added to each row of the Mapillary list.
    '''
    for MapillaryPoint in MapillaryList:
        # set an arbitrarily high number for the minimum distance at the start of each row
        MinDistance = 99999999
        for KnownPoint in KnownList:
            # find the distance between the points 
            Xdistance = math.pow((MapillaryPoint[0]-KnownPoint[0]),2)
            Ydistance = math.pow((MapillaryPoint[1]-KnownPoint[1]),2)
            Sum = Ydistance + Xdistance
            Distance = math.sqrt(Sum)
            # compare this distance to the previous minimum and if less than update the minimum distance value
            # if the new value is higher than pass
            if Distance < MinDistance:
                MinDistance = Distance
            else:
                pass
        MapillaryPoint.append(MinDistance)

def InsertDistanceValues(MapillaryList):
    '''
    Function that takes the updated Mapillary list from the calculate shortest distance
    function and inserts the new distance value into a new distance field.  The insert
    cursor compares the key values between the feature class and list to find a match
    then inserts the list distance value into the distance field
    '''
    arcpy.AddField_management(FcMapillary, 'Distance', "DOUBLE")
    with arcpy.da.UpdateCursor(FcMapillary, ["Key", "Distance"]) as Cursor:
        for Row in Cursor:
            for Item in MapillaryList:
                if Row[0] == Item[2]:
                    Row[1] = Item[3]
                    Cursor.updateRow(Row)
                else:
                    pass
    del Cursor

if __name__ == "__main__":
    main(FcKnown, FcMapillary, LineFeatureClass, PointDistance)


