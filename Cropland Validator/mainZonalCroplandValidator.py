'''
# Name:     Python launcher for cropland validator C++ code
# Created:  10/12/2011
# Author:   Andriy Bun, andr.bun@gmail.com
# Modified: 
'''

import sys
import os
commonDir = os.path.dirname(sys.argv[0]) + '\\..\\Common'
sys.path.append(commonDir)

import shutil
import subprocess
import arcgisscripting

from common import *
from utils import IsSameExtent, RasterData

if __name__ == "__main__":
    workingDir = os.path.dirname(sys.argv[0])
    os.chdir(workingDir)
    # runFileName = workingDir + "\\croplandValidator.exe"
    runFileName = "croplandValidator.exe"
    
    areaGrid         = sys.argv[1]
    statisticsLevel0 = sys.argv[2]
    statisticsLevel1 = sys.argv[3]
    statisticsLevel2 = sys.argv[4]
    probabilityGrid  = sys.argv[5]
    statLayer        = sys.argv[6]
    output           = os.path.splitext(sys.argv[9])[0]
    
    resultDir        = os.path.dirname(output)
    tmpDir           = resultDir + "\\tmp_" + os.getenv('COMPUTERNAME')
    clippedDir       = resultDir + "\\clipped_" + os.getenv('COMPUTERNAME')
    deleteTmpDir = False
	
    if not os.path.exists(tmpDir):
        os.mkdir(tmpDir)
        deleteTmpDir = True
    if not os.path.exists(clippedDir):
        os.mkdir(clippedDir)
    
    clippedAreaGrid         = RasterData(clippedDir + "\\area" + ".img")
    clippedStatisticsLevel0 = RasterData(clippedDir + "\\stat0" + ".img")
    clippedStatisticsLevel1 = RasterData(clippedDir + "\\stat1" + ".img")
    clippedStatisticsLevel2 = RasterData(clippedDir + "\\stat2" + ".img")
    clippedProbabilityGrid  = RasterData(clippedDir + "\\prob" + ".img")
    clippedStatLayer        = RasterData(clippedDir + "\\minavgmax" + ".img")

    gp = arcgisscripting.create()

    conditionalRaster = sys.argv[7]
    zonalCondition = sys.argv[8]
    inRasterList  = [areaGrid, \
                     statisticsLevel0, \
                     statisticsLevel1, \
                     statisticsLevel2, \
                     probabilityGrid]
    clippedRasterList = [clippedAreaGrid.getFullPath(), \
                     clippedStatisticsLevel0.getFullPath(), \
                     clippedStatisticsLevel1.getFullPath(), \
                     clippedStatisticsLevel2.getFullPath(), \
                     clippedProbabilityGrid.getFullPath()]
    ConClip(conditionalRaster, inRasterList, zonalCondition, clippedRasterList)
    desc = gp.Describe(clippedStatisticsLevel0.getFullPath())
    coords = desc.Extent
	
    statList = []
    outputList = []
    if statLayer == "#":
        statTypes = ["min", "minavg", "avg", "maxavg", "max"]
        numStatistics = len(statTypes)
        # no raster specified, running for all types of statistics
        for statType in statTypes:
            statList.append(os.path.splitext(probabilityGrid)[0] + "_" + statType)
            outputList.append(os.path.splitext(probabilityGrid)[0] + "_" + statType + "_cropland")
        gp.AddWarning("Warning! The output file name will be ignored. " \
            "Autogenerated file names will be used instead.")
    else:
        # statistics raster specified, running only for it
        statList = [os.path.splitext(statLayer)[0]]
        outputList = [output]
        numStatistics = 1

    for idx in range(0, numStatistics):
        ConClip(conditionalRaster, [statList[idx] + ".img"], zonalCondition, [clippedStatLayer.getFullPath()])
        
        executeCommand = '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % ( \
            runFileName, \
            workingDir, \
            resultDir, \
            tmpDir, \
            clippedAreaGrid.getPath(), \
            clippedStatisticsLevel0.getPath(), \
            clippedStatisticsLevel1.getPath(), \
            clippedStatisticsLevel2.getPath(), \
            clippedProbabilityGrid.getPath(), \
            clippedStatLayer.getPath(), \
            outputList[idx])
    
        os.chdir(workingDir)
        callResult = subprocess.call(executeCommand)

    if deleteTmpDir:
        shutil.rmtree(tmpDir)
        
    if not(callResult == 0):
        raise Exception('Error! Function returned error code %d!' % callResult)