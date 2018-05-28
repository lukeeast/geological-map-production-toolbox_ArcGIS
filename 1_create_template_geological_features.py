# -*- coding: utf-8 -*-
"""
Script to generate template geological features
for digitising a hand drawn Geological map
Based on SURV319_2017 Tutorial 4 instructions

Made By Luke Easterbrook
9/2017
"""

#import modules
import arcpy
from arcpy import env #import for environment setting
import traceback #for error handling
import os #import os for easier path operations (e.g. concatenation)

#allow overwriting (enable for testing purposes)
arcpy.env.overwriteOutput = False

#code for error handling in ArcGIS scripts.  From SURV519 2017 Tutorial 4 instructions
try:


##get various input from the user
    workingGDBPath= arcpy.GetParameterAsText(0) #Get the path to the working 
    coordinateSystem = arcpy.GetParameterAsText(1)#required input - get the coordinate system to apply to template features


##other parameters used in this script, FD = Feature Dataset, FC = Feature Class 
    digitisingFDName = "Geology_digitising"
    outputFDName = "Geology_output"
    contactsFCName = "Contacts"
    boundaryFCName = "Map_boundary"
    accuracyFieldName = "Accuracy"
    validUnitTableName = "Valid_units"
    unitCodeFieldName = "Unit_code"
    unitNameFieldName = "Unit_Name"


##set the environment to the working geodatabase 
    env.workspace = workingGDBPath


## Make all the feature datasets and feature classes we will use

    #Create the feature dataset where the empty geological features will be stored
    arcpy.CreateFeatureDataset_management(workingGDBPath, digitisingFDName, coordinateSystem)

    #Create the feature class for contacts
    arcpy.CreateFeatureclass_management(digitisingFDName, contactsFCName, "POLYLINE")

    #Create the feature class for map boundary
    arcpy.CreateFeatureclass_management(digitisingFDName, boundaryFCName, "POLYGON")


##Preparing the Valid Units table

    #create the table of Valid Units
    arcpy.CreateTable_management(workingGDBPath, validUnitTableName)

    #add the Unit Code field to the Valid Units Table
    arcpy.AddField_management(validUnitTableName,unitCodeFieldName,"TEXT","")

    #add the Unit Name field to the Valid Units Table
    arcpy.AddField_management(validUnitTableName,unitNameFieldName,"TEXT","")


##Create accuracy field in the contacts feature class and add sub type containing valid accuracy types
    
    #add the accuracy field
    arcpy.AddField_management(os.path.join(digitisingFDName,contactsFCName),accuracyFieldName,"LONG","")

    #Create empty sub type to go in the Accuracy Field
    arcpy.SetSubtypeField_management(os.path.join(digitisingFDName,contactsFCName),accuracyFieldName)

    #define a sub-type(ST) array for accuracy fields as tuples
    accuracySTArray = [(1,"Accurate"),(2,"Approximate"),(3,"Inferred")]
    
    #loop through the unit code sub-type array and add each value to the sub-types for the unit code field
    #the array is a 1d array of tuples, so we need to use "array[][]" to access individual values
    for i in range(len(accuracySTArray)):
        arcpy.AddSubtype_management(os.path.join(digitisingFDName,contactsFCName),accuracySTArray[i][0],accuracySTArray[i][1])

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
