### Authors: Jay Dahlstrom, Christian Matthews and Tommy Nguyen
### Date: August 5, 2017
### Geography 569
###
### Description: Takes a GeoJSON file from Mapillary and exports the desired object
### class to a new user defined shapefile for use in a desktop GIS (ArcMap/QGIS).
### The script requires an output folder location for the new shapefile, the name
### of the shapefile, an output field name for the object class data, the output
### spatial reference and the GeoJSON file and object class key to function. Tool
### is run through ArcMap as a custom toolbox tool.
###
### This script was designed to work with ArcGIS 10.4/10.5 and Python 2.7.10,
### the script may or may not work with other versions ArcGIS and will need to be
### refactored to work with newer versions of Python (if/when arcpy is updated to
### work with newer Python versions).

###
### import modules
###

import arcpy
import json

###
### Parameters
###

# The folder/database where the Feature Class will be stored
FcFolder = arcpy.GetParameterAsText(0)
# Name of the new feature class
FcName = arcpy.GetParameterAsText(1)
# Name of the new object field, Double field that stores percent of image for the object class
FcField = arcpy.GetParameterAsText(2)
# Coordinate Systems for the output feature class
FcSR = arcpy.GetParameterAsText(3)
# Path to the GeoJSON dataset
JsonPath = arcpy.GetParameterAsText(4)
# Name of the object class dictionary key
ObjectJsonName = arcpy.GetParameterAsText(5)

###
### Set work environment
###

arcpy.AddMessage('Importing modules and setting environment')

arcpy.env.workspace = FcFolder
workspace = arcpy.env.workspace
arcpy.env.overwriteOutput = True

###
### Script Follows
###

def main(OutFCLocation, FCName, ObjectFieldName, CoordinateSystem, RawDataFilePath, ObjectKey):
    arcpy.AddMessage('Creating the new shapefile')
    FeatureClassPath = CreateFeatureClass(OutFCLocation, FCName, ObjectFieldName)
    arcpy.AddMessage('Extracting GeoJSON data')
    DataList = ExtractData(RawDataFilePath, ObjectKey)
    arcpy.AddMessage('Inserting GeoJSON data into the shapefile')
    InsertFields = ['Key', ObjectFieldName, 'SHAPE@XY']
    InsertData(FeatureClassPath, InsertFields, DataList)
    arcpy.AddMessage('Projecting the shapefile in the desired coordinate system')
    arcpy.Project_management(FeatureClassPath, OutFCLocation + r'\\' + FCName + r'_Projected.shp', CoordinateSystem)
    arcpy.AddMessage('Script finished successfully')
  
def CreateFeatureClass(OutLocation, Name, ObjectFieldName):
    '''
    Function that takes an output folder, feature class name and output
    field name and creates a new shapefile to load the Mapillary data into
    from the GeoJSON data.  The function adds a field for the unique key
    associated with each photo and sets the spatial reference to Web
    Mercator (the Mapillary projection).
    '''
    arcpy.CreateFeatureclass_management(OutLocation, Name, "POINT")
    # Need to set if/else statement for .shp extension
    FeatureClassPath = OutLocation + r'\\' + Name + r'.shp'
    arcpy.AddField_management(FeatureClassPath, 'Key', "TEXT")
    arcpy.AddField_management(FeatureClassPath, ObjectFieldName, "DOUBLE")
    SR = arcpy.SpatialReference(4326)
    arcpy.DefineProjection_management(FeatureClassPath, SR)
    return FeatureClassPath
    
def ExtractData(FilePath, ObjectKey):
    '''
    Function that extracts the data from the GeoJSON file and returns a nested
    list that will be used to populate the feature class from the new shapefile.
    The path to the GeoJSON file and the key for the object being imported are
    required as inputs.
    '''
    DataTransferList = []
    with open(FilePath) as RawData:
        DataDictionary = json.load(RawData)

    for Row in DataDictionary['features']:
        DataTransferList.append([Row['properties']['key'], Row['properties'][ObjectKey], Row['geometry']['coordinates']])
    return DataTransferList

def InsertData(FeatureClassPath, Fields, DataList):
    '''
    Function that inserts the output of a nested list into the new shapefile.
    Requires the path of the shapefile and the nested list to function properly.
    '''
    Cursor = arcpy.da.InsertCursor(FeatureClassPath, Fields)
    for Row in DataList:
        Cursor.insertRow(Row)
    del Cursor

if __name__ == "__main__":
    main(FcFolder, FcName, FcField, FcSR, JsonPath, ObjectJsonName)

