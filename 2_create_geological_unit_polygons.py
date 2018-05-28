# -*- coding: utf-8 -*-
"""
Script to turn contacts and boundary geology into unit polygons
Based on SURV519 2017 Tutorial 4 instructions

Made By Luke Easterbrook
9/2017
"""

#import modules
import arcpy
from arcpy import env #import for environment setting
import traceback #for error handling
import os #import os for easier path operations (e.g. concatenation)
import numpy 

#allow overwriting (enable for testing purposes)
arcpy.env.overwriteOutput = False

#code for error handling in ArcGIS scripts.  From SURV319 2017 Tutorial 4 instructions
try:
    
##get various input from the user. For the optional inputs the default names/paths are based on
##the user having run the script 1_create_template_geological_features_v2 to generate the template geology
    workingGDBPath= arcpy.GetParameterAsText(0) #Required get the path to the working geodatabase
    digitisingFDPath = arcpy.GetParameterAsText(1) #Optional get the name of the digitising feature dataset
    contactsFCPath = arcpy.GetParameterAsText(2)#Optional get the digitised contacts from the user
    boundaryFCPath = arcpy.GetParameterAsText(3) #Optional get the digitised boundary from the user
    validUnitTableName = arcpy.GetParameterAsText(4)#Optional, get name of the table that has the valid units in it
    unitCodeFieldName = arcpy.GetParameterAsText(5) #Optional, get the Unit Code Value that was used
    fieldMapScale = arcpy.GetParameter(6)#Required input - field map absolute scale
    digitisingAccuracy = float(arcpy.GetParameter(7)) #Optional- This overrides value from map scale.(the default is empty)

##other parameters used in this script, FC = Feature Class 
    unitsFCName = "Units"

    
##set the environment to the working geodatabase
    env.workspace = workingGDBPath


##Snap edit the contacts layer to tidy up any digitising issues. This ensures that Creating the unit polygons works correctly.
    arcpy.Snap_edit(contactsFCPath, [[contactsFCPath, "END", digitisingAccuracy], [boundaryFCPath, "EDGE", digitisingAccuracy],[contactsFCPath, "EDGE", digitisingAccuracy]])

    
##Create the unit polygons
    
    #turn the contacts and boundary into unit polygons
    inFeatures = [contactsFCPath,boundaryFCPath]
    arcpy.FeatureToPolygon_management(inFeatures, os.path.join(digitisingFDPath,unitsFCName),"", "NO_ATTRIBUTES", "")

    
##Add the unit code sub_type to the unit polygon feature class

    #Add the Unit code Field
    arcpy.AddField_management(os.path.join(digitisingFDPath,unitsFCName),unitCodeFieldName,"LONG")

    #Create empty sub type for the Unit Code field
    arcpy.SetSubtypeField_management(os.path.join(digitisingFDPath,unitsFCName),unitCodeFieldName)

    #create a new numpy array from the Unit polygon attributes we just created. This array is a 1d array of tuples
    fields = ['OID@', unitCodeFieldName]
    UnitCodeSubTypeArray = arcpy.da.TableToNumPyArray(validUnitTableName,fields)
    
    #loop through the unit code sub-type array and add each value to the sub-types for the unit code field
    #the array is a 1d array of tuples, so we need to use "array[][]" to access individual values
    for i in range(UnitCodeSubTypeArray.shape[0]):
        arcpy.AddSubtype_management(os.path.join(digitisingFDPath,unitsFCName),UnitCodeSubTypeArray[i][0],UnitCodeSubTypeArray[i][1])

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
