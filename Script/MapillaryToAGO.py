### Authors: Jay Dahlstrom, Christian Matthews and Tommy Nguyen
### Date: July 20, 2017
### Geography 569
###
### Description: This script is designed to convert an ESRI MXD file into a 
### hosted feature service in an ArcGIS Online Organizational Account.  With
### this service it will be possible to create public and/or private web applications.
### Mapillary and local city governments will be better able to distribute
### information to their users/constituents.
###
### This script was designed to work with ArcGIS 10.4/10.5 and Python 2.7.10,
### the script may or may not work with other versions ArcGIS and will need to be
### refactored to work with newer versions of Python (if/when arcpy is updated to
### work with newer Python versions).

###
### Import Modules
###

import arcpy
import os
import sys
import xml.dom.minidom as DOM
import shutil

###
### Input Parameters
###

# Convert to get Parameter as text
loggedIntoAGO = arcpy.GetParameterAsText(0)
path2MXD = arcpy.GetParameterAsText(1)
serviceName = arcpy.GetParameterAsText(2)
serviceSummary = arcpy.GetParameterAsText(3)
serviceTags = arcpy.GetParameterAsText(4)

###
### Script Follows
###

arcpy.AddMessage('Creating temporary working folder')
# Create temp folder in local directory, if necessary delete old temp folder first
tempPath = sys.path[0] + r"\tempArcGISOnline"
if os.path.isdir(tempPath):
    shutil.rmtree(tempPath)
os.makedirs(tempPath)

arcpy.AddMessage('Setting output file parameters')
# Set file paths to service files
arcpy.env.overwriteOutput = True
SDdraft = os.path.join(tempPath, "tempdraft.sddraft")
newSDdraft = os.path.join(tempPath, "updatedDraft.sddraft")
SD = os.path.join(tempPath, serviceName + ".sd")

arcpy.AddMessage('Creating initial service definition file')
#Create service definition draft
mxd = arcpy.mapping.MapDocument(path2MXD)
arcpy.mapping.CreateMapSDDraft(mxd, SDdraft, serviceName, "MY_HOSTED_SERVICES", "", True, "", serviceSummary, serviceTags)


###
### From here to the end was mostly developed by ESRI
### For more info review example 7 here: http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-mapping/createmapsddraft.htm 
###

arcpy.AddMessage('Updating service definition to enable feature access')
# Read the contents of the original SDDraft into an xml parser
doc = DOM.parse(SDdraft)

# The following 5 code pieces modify the SDDraft from a new MapService
# with caching capabilities to a FeatureService with Query,Create,
# Update,Delete,Uploads,Editing capabilities. The first two code
# pieces handle overwriting an existing service. The last three pieces
# change Map to Feature Service, disable caching and set appropriate
# capabilities. You can customize the capabilities by removing items.
# Note you cannot disable Query from a Feature Service.
tagsType = doc.getElementsByTagName('Type')
for tagType in tagsType:
    if tagType.parentNode.tagName == 'SVCManifest':
        if tagType.hasChildNodes():
            tagType.firstChild.data = "esriServiceDefinitionType_Replacement"

tagsState = doc.getElementsByTagName('State')
for tagState in tagsState:
    if tagState.parentNode.tagName == 'SVCManifest':
        if tagState.hasChildNodes():
            tagState.firstChild.data = "esriSDState_Published"

# Change service type from map service to feature service
typeNames = doc.getElementsByTagName('TypeName')
for typeName in typeNames:
    if typeName.firstChild.data == "MapServer":
        typeName.firstChild.data = "FeatureServer"

# Turn off caching
configProps = doc.getElementsByTagName('ConfigurationProperties')[0]
propArray = configProps.firstChild
propSets = propArray.childNodes
for propSet in propSets:
    keyValues = propSet.childNodes
    for keyValue in keyValues:
        if keyValue.tagName == 'Key':
            if keyValue.firstChild.data == "isCached":
                keyValue.nextSibling.firstChild.data = "false"

# Turn on feature access capabilities
configProps = doc.getElementsByTagName('Info')[0]
propArray = configProps.firstChild
propSets = propArray.childNodes
for propSet in propSets:
    keyValues = propSet.childNodes
    for keyValue in keyValues:
        if keyValue.tagName == 'Key':
            if keyValue.firstChild.data == "WebCapabilities":
                keyValue.nextSibling.firstChild.data = "Query,Create,Update,Delete,Uploads,Editing"

# Write the new draft to disk
f = open(newSDdraft, 'w')
doc.writexml( f )
f.close()

# Analyze the service
analysis = arcpy.mapping.AnalyzeForSD(newSDdraft)

arcpy.AddMessage('Uploading service definition to ArcGIS Online')
if analysis['errors'] == {}:
    # Stage the service
    arcpy.StageService_server(newSDdraft, SD)

    # Upload the service. The OVERRIDE_DEFINITION parameter allows you to override the
    # sharing properties set in the service definition with new values. In this case,
    # the feature service will be shared to everyone on ArcGIS.com by specifying the
    # SHARE_ONLINE and PUBLIC parameters. Optionally you can share to specific groups
    # using the last parameter, in_groups.
    arcpy.UploadServiceDefinition_server(SD, "My Hosted Services", serviceName,
                                         "", "", "", "", "OVERRIDE_DEFINITION", "SHARE_ONLINE",
                                         "PRIVATE", "NO_SHARE_ORGANIZATION", "")

    print "Uploaded and overwrote service"

else:
    # If the sddraft analysis contained errors, display them and quit.
    print analysis['errors']
