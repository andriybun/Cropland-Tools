# Date:   20/12/2011
# Author: Andriy Bun
# Name:   ...

import sys
import os
import subprocess
import shutil
import arcgisscripting
commonDir = os.path.dirname(sys.argv[0]) + '\\..\\Common'
sys.path.append(commonDir)

from common import *
from rasterAgreementTable import invertPriorities, rasterAgreementTable

def ones(size):
    xRes = []
    for xIdx in range(size):
        xRes.append(1)
    return xRes
    
#def invertPriorities(priorityVector):
#    maxVal = max(priorityVector) + 1
#    res = []
#    for val in priorityVector:
#        res.append(maxVal - val)
#    return res    

def vectorToStr(vec):
    return str(vec).replace('[', '').replace(']', '').replace(',', '')

if __name__ == "__main__":
    
    workingDir = os.path.dirname(sys.argv[0])
    os.chdir(workingDir)

    runFileName = "probabilityLayer.exe"

    # Parse command line arguments:
    num_args = len(sys.argv)
    
    # Parse results' names:
    resultProb = os.path.splitext(sys.argv[7].replace("'",""))[0]
    resultNameTuple = os.path.splitext(resultProb)
    descriptionFileName = resultNameTuple[0] + ".txt"
    resultAvg       = resultNameTuple[0] + "_avg"
    resultMinAvg    = resultNameTuple[0] + "_minavg"
    resultMin       = resultNameTuple[0] + "_min"
    resultMaxAvg    = resultNameTuple[0] + "_maxavg"
    resultMax       = resultNameTuple[0] + "_max"

    resultDir        = os.path.dirname(resultProb)
    tmpDir           = resultDir + "\\tmp_" + os.getenv('COMPUTERNAME')
    deleteTmpDir = False
    if not os.path.exists(tmpDir):
        os.mkdir(tmpDir)
        deleteTmpDir = True

    # Parse and clip inputs
    cellAreas = sys.argv[1].replace("'","")
    countries = sys.argv[2].replace("'","")
    clippedCountries = tmpDir + "\\clippedCountries"
    clippedCellAreas = tmpDir + "\\clippedCellAreas"
    
    # Get clipping bounds
    gp = arcgisscripting.create()
    
    zonalCondition = sys.argv[3]
    ConClip(countries, countries, zonalCondition, clippedCountries + ".img")
    
    desc = gp.Describe(countries)
    coords = desc.Extent

    # Clip inputs
    ConClip(countries, cellAreas, zonalCondition, clippedCellAreas + ".img")
    
    croplandLayerList = (sys.argv[4].replace("'","")).split(";")
    numRasters = len(croplandLayerList)
    passCroplandLayerList = ''
    for i in range(numRasters):
        if (croplandLayerList[i][0] == '\''):
            croplandLayerList[i] = croplandLayerList[i][1:-1]
        clippedCroplandLayerName = tmpDir + "\\crp_%02d" % i
        ConClip(countries, croplandLayerList[i], zonalCondition, \
            clippedCroplandLayerName + ".img")
        passCroplandLayerList = passCroplandLayerList + '"%s" ' \
            % (clippedCroplandLayerName)
    passCroplandLayerList = passCroplandLayerList[0:-1]

    # Parse priorities
    prior = sys.argv[5].replace("'","")
    if prior == '#':
        priorityValues = ones(numRasters)
    else:
        priorityList = prior.split(";")
        priorityValues = []
        for priorityStr in priorityList:
            priorityValues.append(int(priorityStr))
    prior = sys.argv[6].replace("'","")
    if prior == '#':
        priorityValues2 = ones(numRasters)
    else:
        priorityList2 = prior.split(";")
        priorityValues2 = []
        for priorityStr in priorityList2:
            priorityValues2.append(int(priorityStr))
    
    # Invert priority vectors    
    priorityValues = invertPriorities(priorityValues)
    priorityValues2 = invertPriorities(priorityValues2)
    
    # Process priorities:
    print descriptionFileName
    agreementTable = rasterAgreementTable(priorityValues, priorityValues2)
    descriptionFile = open(descriptionFileName, 'w')
    agreementTable.PrintToFile(descriptionFile, croplandLayerList)
    descriptionFile.close()
    
    executeCommand = '"%s" "%s" "%s" "%s" "%s" "%s" %d %s %s %s %s "%s" "%s" "%s" "%s" "%s" "%s"' % ( \
        runFileName, \
        workingDir, \
        resultDir, \
        tmpDir, \
        clippedCellAreas, \
        clippedCountries, \
        numRasters, \
        passCroplandLayerList, \
        vectorToStr(priorityValues), \
        vectorToStr(priorityValues2), \
        vectorToStr(agreementTable.weights), \
        resultProb, \
        resultAvg, \
        resultMinAvg, \
        resultMin, \
        resultMaxAvg, \
        resultMax)

#    print '==============='
#    print executeCommand
#    print '==============='
#    raise Exception('111')

    os.chdir(workingDir)

    callResult = subprocess.call(executeCommand)

    if deleteTmpDir:
        shutil.rmtree(tmpDir)
    
    if not(callResult == 0):
        raise Exception('Error! Function returned error code %d!' % callResult)
