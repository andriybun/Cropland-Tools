# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 11:36:34 2010

@author: Andriy Bun

@name:   Useful utils
"""

import os
import shutil
import arcgisscripting
from iterableStruct import iterableStruct

class config():
    
    num_rasters = 4
    
    paths = iterableStruct()

    def __init__(self, gui, inputPaths, coords, doClip = 1):
        self.gui = gui
        self.gp = arcgisscripting.create()
        self.gp.CheckOutExtension("Spatial")
        self.gp.OverWriteOutput = 1
        self.__InitPaths__(inputPaths)
        gui.PrintText("Homedir: " + str(self.paths.HOMEDIR))
        self.num_rasters = len(self.paths.inputs.LayerList)
        gui.PrintTextTime("Verifying")
        self.VerifyRasters(self.paths.inputs, gui)
        gui.PrintTextTime("Clipping inputs")
        if doClip == 1:
            self.ClipRasters(coords)
        try:
            shutil.rmtree("%s\\Local Settings\\Temp\\" % (os.getenv('USERPROFILE')))
        except:
            pass

    def __InitPaths__(self, inputPaths = None):
        # Main directories
        if inputPaths is None:
            self.paths.HOMEDIR = os.getcwd() + "\\"
        else:
            #self.paths.HOMEDIR = os.getcwd() + "\\"
            self.paths.HOMEDIR = os.path.dirname(inputPaths.result) + "\\"
        self.paths.INPUTDIR = self.paths.HOMEDIR + "input\\"
        self.paths.RESULTDIR = self.paths.HOMEDIR + "results_" + os.getenv('COMPUTERNAME') + "\\"
        self.paths.TMPDIR = self.paths.HOMEDIR + "tmp_" + os.getenv('COMPUTERNAME') + "\\"
        
        self.DeleteDir(self.paths.TMPDIR)
        if not os.path.isdir(self.paths.TMPDIR):
            os.mkdir(self.paths.TMPDIR)
        
        if inputPaths is None:
            # Input rasters:
            self.paths.inputs = iterableStruct()
            
            inputLayerPrefix = self.paths.INPUTDIR + "layer"
            self.paths.inputs.units            = self.paths.INPUTDIR + "countries"
            self.paths.inputs.cellAreas        = self.paths.INPUTDIR + "cell_areas"
            
            self.paths.inputs.LayerList = []
            
            for i in range(1, self.num_rasters + 1):
                self.paths.inputs.LayerList.append(inputLayerPrefix + str(i))
    
            # Result:
            if not os.path.isdir(self.paths.RESULTDIR):
                os.mkdir(self.paths.RESULTDIR)

            self.paths.result = self.paths.RESULTDIR + "mark_high" + extension
            self.paths.description = self.paths.RESULTDIR + "mark_high.txt"
            self.paths.resultAvg = self.paths.RESULTDIR + "mark_high_avg" + extension
            self.paths.resultMin = self.paths.RESULTDIR + "mark_high_min" + extension
            self.paths.resultMax = self.paths.RESULTDIR + "mark_high_max" + extension
        else:
            # Input rasters:
            self.paths.inputs = iterableStruct()
            
            self.paths.inputs.units     = inputPaths.countries
            self.paths.inputs.cellAreas = inputPaths.cellAreas
            self.paths.inputs.LayerList = inputPaths.croplandLayerList
            
            # Result:
            extension = ".img"
            #extension = ""
            resultExtension = ".img"
            self.paths.result = inputPaths.result
            result_name_tuple = os.path.splitext(self.paths.result)
            self.paths.description = result_name_tuple[0] + ".txt"
            if result_name_tuple[1] != resultExtension:
                self.gui.Warning("Warning: '" + os.path.basename(self.paths.result) + \
                "' is not a valid img rater name! Changed to '" + \
                os.path.basename(result_name_tuple[0]) + resultExtension)
                self.paths.result = result_name_tuple[0] + resultExtension
                result_name_tuple = os.path.splitext(self.paths.result)

            self.paths.resultAvg = result_name_tuple[0] + "_avg" + result_name_tuple[1]
            self.paths.resultMin = result_name_tuple[0] + "_min" + result_name_tuple[1]
            self.paths.resultMax = result_name_tuple[0] + "_max" + result_name_tuple[1]
        
        # Temporary rasters:
        self.paths.tmp = iterableStruct()

        tmpPrefix = self.paths.TMPDIR + "tmp_%d" + extension
        
        self.paths.tmp.LayerList = []
        
        for i in range(1, len(self.paths.inputs.LayerList) + 1):
            self.paths.tmp.LayerList.append(tmpPrefix % i)

        self.paths.tmp.temp1      = self.paths.TMPDIR + "temp1" + extension
        self.paths.tmp.temp2      = self.paths.TMPDIR + "temp2" + extension
        self.paths.tmp.temp3      = self.paths.TMPDIR + "temp3" + extension
        self.paths.tmp.temp4      = self.paths.TMPDIR + "temp4" + extension
        self.paths.tmp.temp5      = self.paths.TMPDIR + "temp5" + extension
        self.paths.tmp.temp6      = self.paths.TMPDIR + "temp6" + extension
        self.paths.tmp.sumRast    = self.paths.TMPDIR + "sumRast" + extension
        self.paths.tmp.sumRastOne = self.paths.TMPDIR + "sumRastOne" + extension
        self.paths.tmp.sumRastTwo = self.paths.TMPDIR + "sumRastTwo" + extension

    # clip an area from input raster    
    def ClipRasters(self, coords):
        if coords is None or coords == '#':
            RasterName = self.paths.inputs.units
            rName = os.path.splitext(os.path.basename(RasterName))
            clippedName = self.paths.TMPDIR + rName[0][0:9] + rName[1]
            self.gp.copy_management(RasterName, clippedName)
            self.paths.inputs.units = clippedName
            RasterName = self.paths.inputs.cellAreas
            rName = os.path.splitext(os.path.basename(RasterName))
            clippedName = self.paths.TMPDIR + rName[0][0:9] + rName[1]
            self.gp.copy_management(RasterName, clippedName)
            self.paths.inputs.cellAreas = clippedName
        else:
            RasterName = self.paths.inputs.units
            rName = os.path.splitext(os.path.basename(RasterName))
            clippedName = self.paths.TMPDIR + rName[0][0:9] + rName[1]
            self.gp.clip_management(RasterName, coords, clippedName)
            self.paths.inputs.units = clippedName
            RasterName = self.paths.inputs.cellAreas
            rName = os.path.splitext(os.path.basename(RasterName))
            clippedName = self.paths.TMPDIR + rName[0][0:9] + rName[1]
            self.gp.clip_management(RasterName, coords, clippedName)
            self.paths.inputs.cellAreas = clippedName
        
        clippedLayerList = []
        
        for RasterName in self.paths.inputs.LayerList:
            rName = os.path.basename(RasterName)
            clippedName = self.paths.TMPDIR + rName
            if coords is None or coords == '#':
                self.gp.copy_management(RasterName, clippedName)
            else:
                self.gp.clip_management(RasterName, coords, clippedName)
            
            clippedLayerList.append(clippedName)
        
        self.paths.inputs.LayerList = clippedLayerList
                
    # Verify if rasters exist
    def VerifyRasters(self, ListOfRasters, gui):
        flag = True
        for RasterName in ListOfRasters:
            if type(RasterName) == list:
                self.VerifyRasters(RasterName, gui)
            else:
                if (not self.gp.Exists(RasterName)):
                    gui.Error('Raster does not exist: ' + RasterName)
                    raise Exception('Raster validation', 'Raster does not exitst')
                    flag = False
        return flag

    # Delete all rasters in a list
    def DeleteRasters(self, ListOfRasters):
        for RasterName in ListOfRasters:
            if type(RasterName) == list:
                self.DeleteRasters(RasterName)
            else:
                self.gp.delete_management(RasterName)

    # Delete all files from a directory
    def DeleteDir(self, dir):
        if os.path.exists(dir):
            shutil.rmtree(dir)
