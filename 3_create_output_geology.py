# -*- coding: utf-8 -*-
"""
Script to turn contacts and boundary geology into unit polygons
Based on SURV519 2017 Tutorial 4 instructions

Made By Luke Easterbrook
9/2017
"""

##import modules
import arcpy
from arcpy import env #import for environment setting
import traceback #for error handling
import os #import os for easier path operations (e.g. concatenation)
import numpy

##code to automatically increment trailing numbers on a string. 
##Modified from https://stackoverflow.com/questions/7085512/check-what-number-a-string-ends-with-in-python
##Luke added functionality to make it increment the number, rather than just fetch it
import re
def increment_trailing_number(s):
    m = re.search(r'\d+$', s)#regular expression to find the numbers on the end
    newString = ""
    if m:
        n = int(m.group())
        newString = s[:-1*len(str(n))] + str(n+1)
    else:
        newString = s + str(1)
    return newString

#allow overwriting (enable for testing purposes)
arcpy.env.overwriteOutput = False

#code for error handling in ArcGIS scripts.  From SURV319 2017 Tutorial 4 instructions
try:
    
##get various input from the user. For the optional inputs the default names/paths are based on
##the user having run the script 1_create_template_geological_features_v2 to generate the template geology
    workingGDBPath= arcpy.GetParameterAsText(0) #Required get the path to the working geodatabase
    inputUnitsFCPath = arcpy.GetParameterAsText(1) #required get the input units(added)
    digitisingFDPath = arcpy.GetParameterAsText(2) #Optional get the name of the digitising feature dataset
    contactsFCPath = arcpy.GetParameterAsText(3)#Optional get the digitised contacts from the user
    boundaryFCPath = arcpy.GetParameterAsText(4) #Optional get the digitised boundary from the user
    validUnitTableName = arcpy.GetParameterAsText(5)#Optional, get name of the table that has the valid units in it
    unitCodeFieldName = arcpy.GetParameterAsText(6) #Optional, get the Unit Code Value that was used
    fieldMapScale = arcpy.GetParameter(7)#Required input - field map absolute scale
    digitisingAccuracy = float(arcpy.GetParameter(8)) #Optional- This overrides value from map scale.(the default is empty)

##other parameters used in this script, FC = Feature Class 
    unitsTempFCName = "Units_temp"
    unitsUpdatedFCPath = increment_trailing_number(inputUnitsFCPath)
    
##set the environment to the working geodatabase
    env.workspace = workingGDBPath

##Snap the contacts vertices to their own ends, the edges of the boundary layer, and then the contacts edges
    arcpy.Snap_edit(contactsFCPath, [[contactsFCPath, "END", digitisingAccuracy], [boundaryFCPath, "EDGE", digitisingAccuracy],[contactsFCPath, "EDGE", digitisingAccuracy]])    

##Create the unit polygons
    
    #turn the contacts and boundary into unit polygons
    inFeatures = [contactsFCPath,boundaryFCPath]
    arcpy.FeatureToPolygon_management(inFeatures, os.path.join(digitisingFDPath,unitsTempFCName),"", "NO_ATTRIBUTES", "")

##Get the attributes for Unit polygons V2 from the original Unitsl Feature Class using a Spatial Join

    arcpy.SpatialJoin_analysis(os.path.join(digitisingFDPath,unitsTempFCName),inputUnitsFCPath, unitsUpdatedFCPath,"", "", "", "HAVE_THEIR_CENTER_IN","","")
    
##Add the unit code sub_type to the output polygon feature class

    #Create empty sub type for the Unit Code field
    arcpy.SetSubtypeField_management(unitsUpdatedFCPath,unitCodeFieldName)
    
    #create a new numpy array from the Unit polygon attributes we just created. This array is a 1d array of tuples
    fields = ['OID@', unitCodeFieldName]
    UnitCodeSubTypeArray = arcpy.da.TableToNumPyArray(validUnitTableName,fields)
    
    #loop through the unit code sub-type array and add each value to the sub-types for the unit code field
    #the array is a 1d array of tuples, so we need to use "array[][]" to access individual values
    for i in range(UnitCodeSubTypeArray.shape[0]):
        arcpy.AddSubtype_management(unitsUpdatedFCPath,UnitCodeSubTypeArray[i][0],UnitCodeSubTypeArray[i][1])

##Delete the temp units layer
    arcpy.Delete_management(os.path.join(digitisingFDPath,unitsTempFCName))

##Script Finished

#code to provide error messages. From SURV319 2017 Tutorial 4 instructions
except arcpy.ExecuteError: 
    # Get the tool error messages 
    # 
    msgs = arcpy.GetMessages(2) 
    
    # Return tool error messages for use with a script tool 
    #
    arcpy.AddError(msgs) 

    # Print tool error messages for use in Python/PythonWin 
    # 
    print(msgs)

except:
    # Get the traceback object
    #
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    #
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

    # Return python error messages for use in script tool or Python Window
    #
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    #
    print(pymsg)
    print(msgs)
