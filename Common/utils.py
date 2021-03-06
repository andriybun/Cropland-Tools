from os import path

# Floating point operations tolerance
EPSILON = 1e-6
propertyNames = ['TOP', \
                 'BOTTOM', \
                 'LEFT', \
                 'RIGHT', \
                 'CELLSIZEX', \
                 'CELLSIZEY']
					 
# Ceck a list of rasters for having the same extent
def GetRasterExtent(gp, raster):
    numProperties = len(propertyNames);
    extent = [0] * numProperties
    for i in range(numProperties):
        extent[i] = gp.GetRasterProperties_management(raster.getFullPath(), propertyNames[i])
    
    return extent
    
def IsSameExtent(gp, rasterList):
    firstRaterExtent = GetRasterExtent(gp, rasterList[0])    
    numProperties = len(firstRaterExtent)
    for raster in rasterList[1:]:
        if raster.getPath() == "#":
            continue
        for i in range(numProperties):
            currentRasterExtent = GetRasterExtent(gp, raster)
            if (abs(firstRaterExtent[i] - currentRasterExtent[i]) > EPSILON):
                gp.AddMessage("Rasters '%s' and '%s' have different extents: %s %f vs %f" % (\
                    rasterList[0].getName(), raster.getName(), propertyNames[i], \
                    firstRaterExtent[i], currentRasterExtent[i]))
                return False
    return True
    
class RasterData:
    dirName = ""
    name = ""
    ext = ""
    
    def __init__(self, rasterPath):
        self.dirName = path.dirname(path.splitext(rasterPath)[0])
        self.name = path.basename(path.splitext(rasterPath)[0])
        self.ext = path.splitext(rasterPath)[1][1:]
    
    def getFullPath(self):
        if self.getName() == "#":
            return "#"
        else:
            return self.getPath() + "." + self.ext
        
    def getPath(self):
        if self.getName() == "#":
            return "#"
        else:
            return self.getDirPath() + "\\" + self.getName()
        
    def getDirPath(self):
        if self.getName() == "#":
            return "#"
        else:
            return self.dirName
        
    def getName(self):
        return self.name
            
def AddSuffixToName(name, suffix):
    return path.splitext(name)[0] + suffix + os.path.splitext(name)[1]

#===============================================================================
#  Method to replace all values in a raster with 'weight', and zeros or noData
#  with 0
#===============================================================================
def MakeRasterOfValues(gp, rast, order, weight, weight2, out):
    onesRast = AddSuffixToName(out, "_count")
    gp.Con_sa(rast, 1, onesRast, 0, "VALUE > 1e-6")
    gp.BuildRasterAttributeTable_management(onesRast, "OVERWRITE")
    gp.Times_sa(onesRast, order, out)
    gp.Times_sa(onesRast, weight, AddSuffixToName(out, "_one"))
    gp.Times_sa(onesRast, weight2, AddSuffixToName(out, "_two"))

#===============================================================================
# Find a value in a sorted list
#===============================================================================
def findFirst(lst, val):
    lo = 0
    hi = len(lst)
    while lo < hi:
        mid = (lo + hi) // 2
        midval = lst[mid]
        if midval < val:
            lo = mid+1
        elif midval > val: 
            hi = mid
        else:
            while mid > 0 and lst[mid-1] == val:
                mid = mid - 1
            return mid
    return -1            
            
##-------------------------------------------------------------------------
## utils class definition
##-------------------------------------------------------------------------
#class utils:
#    paramsStruct = iterableStruct()
#    inputsNotClipped = iterableStruct()
#    inputsClipped = iterableStruct()
#    outputs = iterableStruct()
#    tmp = iterableStruct()
#
#    # constructor
#    def __init__(self, gui, inputsNotClipped = None, output = None):
#        # initialize arcgisscripting object
#        self.gp = arcgisscripting.create()
#        self.gp.CheckOutExtension("Spatial")
#        self.gp.OverWriteOutput = 1 # allow overwriting rasters:
#        # initialize roots and parameters
#        self.paramsStruct = self.initParams(output)
#        gui.PrintText("Homedir: " + str(self.paramsStruct.homeDir))
#        # initialize paths to all the rasters
#        rasterNames = self.defineRasterPaths()
#        if inputsNotClipped is None:
#            self.inputsNotClipped = rasterNames.inputsNotClipped
#        else:
#            self.inputsNotClipped = inputsNotClipped
#        self.inputsClipped = rasterNames.inputsClipped
#        self.outputs = rasterNames.outputs
#        self.logFileName = rasterNames.logFileName
#
#        if output is not None:
#            self.outputs.resultStat = output
#        self.tmp = rasterNames.tmp
##        try:
##            shutil.rmtree("%s\\Local Settings\\Temp\\" % (os.getenv('USERPROFILE')))
##        except:
##            pass            
#
#    # define roots, parameters
#    def initParams(self, output = None):
#        paramsStruct = iterableStruct()
#        if output is None:
#            paramsStruct.homeDir = os.getcwd() + "\\"
#        else:
#            paramsStruct.homeDir = os.path.dirname(output) + "\\"
##            paramsStruct.homeDir = "C:\\ProgramFiles\\Cropland Validation\\TmpRasters\\"
#            if not os.path.exists(paramsStruct.homeDir):
#                os.mkdir(paramsStruct.homeDir)
#        paramsStruct.inputDir = "..\\input_new\\"   # move all the rasters and all data to this directory:
#        paramsStruct.resultDir = "test_results_to_be_deleted_" + os.getenv('COMPUTERNAME') + "\\" # result will be saved to this directory:
#        paramsStruct.tmpDir = paramsStruct.homeDir + "tmp_" + os.getenv('COMPUTERNAME') + "\\"
#        paramsStruct.clippedInputs = paramsStruct.homeDir + "clipped_" + os.getenv('COMPUTERNAME') + "\\"
##        paramsStruct.resultDir = "test_results_to_be_deleted\\" # result will be saved to this directory:
##        paramsStruct.tmpDir = paramsStruct.homeDir + "tmp\\"
##        paramsStruct.clippedInputs = paramsStruct.homeDir + "clipped\\"
#    
#        # Reading configuration file
#        if os.path.exists("settings.txt"):
#            settings = open("settings.txt")
#            i = 0
#            while i < 4:
#                line = settings.readline()
#                while line[0] == '#':
#                    line = settings.readline()
#                if i == 0:
#                    paramsStruct.inputDir = line.rstrip()
#                elif i == 1:
#                    paramsStruct.resultDir = line.rstrip()
#                elif i == 2:
#                    paramsStruct.minClass = int(line.rstrip())
#                elif i == 3:
#                    paramsStruct.maxClass = int(line.rstrip())
#                i = i + 1;
#    
#        # Creating directories if necessary
#        if not os.path.exists(paramsStruct.homeDir + paramsStruct.resultDir):
#            os.mkdir(paramsStruct.homeDir + paramsStruct.resultDir)
#        
#        if not os.path.exists(paramsStruct.tmpDir):
#            os.mkdir(paramsStruct.tmpDir)
#            
#        if not os.path.exists(paramsStruct.clippedInputs):
#            os.mkdir(paramsStruct.clippedInputs)
#        
#        return paramsStruct        
#
#    # define all paths:
#    def defineRasterPaths(self):
#        paramsStruct = self.paramsStruct
#        inputsNotClipped = iterableStruct()
#        inputsClipped = iterableStruct()
#        outputs = iterableStruct()
#        tmp = iterableStruct()            
#        
#        extension = ".img"
#        
#        #-------------------------------------------------------------------------------
#        # Input rasters:
#        #-------------------------------------------------------------------------------
#        inputsNotClipped.mark_high_32     = paramsStruct.homeDir + paramsStruct.inputDir + "mark_high32"
#        inputsNotClipped.countries        = paramsStruct.homeDir + paramsStruct.inputDir + "national"
#        inputsNotClipped.subnationalUnits = paramsStruct.homeDir + paramsStruct.inputDir + "level1_img"
#        inputsNotClipped.subregionalUnits = paramsStruct.homeDir + paramsStruct.inputDir + "level2"
#        inputsNotClipped.cell_area        = paramsStruct.homeDir + paramsStruct.inputDir + "a_0083_1000"
#        inputsNotClipped.statLayer        = paramsStruct.homeDir + paramsStruct.inputDir + "max_5maps-20n"
#    
#        inputsClipped.levelStatisticsName = []
#        inputsClipped.levelStatisticsName.append("cl_level0" + extension) # countries
#        inputsClipped.levelStatisticsName.append("cl_level1" + extension) # subnational units - regions
#        inputsClipped.levelStatisticsName.append("cl_level2" + extension) # subregional units
#        inputsClipped.mark_high_32name = "cl_prob"
#        inputsClipped.mark_high_32     = paramsStruct.clippedInputs + inputsClipped.mark_high_32name + extension
#        inputsClipped.countries        = paramsStruct.clippedInputs + inputsClipped.levelStatisticsName[0]
#        inputsClipped.subnationalUnits = paramsStruct.clippedInputs + inputsClipped.levelStatisticsName[1]
#        inputsClipped.subregionalUnits = paramsStruct.clippedInputs + inputsClipped.levelStatisticsName[2]
#        inputsClipped.cell_area        = paramsStruct.clippedInputs + "cl_a_0083" + extension
#        inputsClipped.statLayer        = paramsStruct.clippedInputs + "cl_mean" + extension
#        inputsClipped.cell_area_min    = paramsStruct.clippedInputs + "cl_a_min" + extension
#    
#        #-------------------------------------------------------------------------------
#        # Resulting rasters:
#        #-------------------------------------------------------------------------------
#        # results of level analysis
#        outputs.resultLevel = []
#        outputs.resultForCalibratedLevel = ['dummy']
#        outputs.resultLevel.append(paramsStruct.homeDir + paramsStruct.resultDir + "resLevel_0" + extension)
#        outputs.resultLevel.append(paramsStruct.homeDir + paramsStruct.resultDir + "resLevel_1" + extension)
#        outputs.resultLevel.append(paramsStruct.homeDir + paramsStruct.resultDir + "resLevel_2" + extension)
#        outputs.resultForCalibratedLevel.append(paramsStruct.homeDir + paramsStruct.resultDir + "resCalibr_1" + extension)
#        outputs.resultForCalibratedLevel.append(paramsStruct.homeDir + paramsStruct.resultDir + "resCalibr_2" + extension)
#        outputs.combinedResult = [ outputs.resultLevel[0] ]
#        outputs.combinedResult.append(paramsStruct.homeDir + paramsStruct.resultDir + "resCombi_1" + extension)
#        outputs.combinedResult.append(paramsStruct.homeDir + paramsStruct.resultDir + "resCombi_2" + extension)
#        outputs.resultStat = outputs.combinedResult[2] + "st" + extension
#        outputs.result_area = paramsStruct.homeDir + paramsStruct.resultDir + "result_ar" + extension
#        outputs.result_sum = paramsStruct.homeDir + paramsStruct.resultDir + "result_sm" + extension
#    
#        #-------------------------------------------------------------------------------
#        # Temporary rasters:
#        #-------------------------------------------------------------------------------
#        tmp.closest       = paramsStruct.tmpDir + "cl_close" + extension
#        tmp.combined      = paramsStruct.tmpDir + "combine" + extension
#        tmp.OutRaster1    = paramsStruct.tmpDir + "tmp1" + extension
#        tmp.OutRaster2    = paramsStruct.tmpDir + "tmp2" + extension
#        tmp.OutRaster3     = paramsStruct.tmpDir + "tmp3" + extension
#        tmp.OutClass       = paramsStruct.tmpDir + "class_%d" + extension
#        tmp.differName = "differ" + extension
#        tmp.differ = paramsStruct.clippedInputs + tmp.differName
#        tmp.zones = paramsStruct.tmpDir + "zones" + extension
#        tmp.areaUnits = paramsStruct.tmpDir + "unit" + extension
#        tmp.sumLevel1 = paramsStruct.tmpDir + "sum_l1" + extension
#        tmp.sumLevel2 = paramsStruct.tmpDir + "sum_l2" + extension
#
#        output = iterableStruct()
#        output.inputsNotClipped = inputsNotClipped
#        output.inputsClipped = inputsClipped
#        output.outputs = outputs
#        output.tmp = tmp
#        output.logFileName = paramsStruct.tmpDir + 'progress_log.txt'
#        
#        return output
#
#    # verify if rasters exist
#    def verifyRasters(self, listOfRasters, gui):
#        for rasterName in listOfRasters:
#            if (not self.gp.Exists(rasterName)):
#                gui.PrintText('Error: Raster does not exist: ' + rasterName);
#                gui.Error('Raster does not exist: ' + rasterName)
#                return 1
#
#    # clip an area from input raster and convert result to integer
#    def clipRasterInt(self, inputRaster, outputRaster, coords):
#        OutRaster1 = self.tmp.OutRaster1
#        if coords is None or coords == '#':
#            self.gp.copy_management(inputRaster, OutRaster1)
#        else:
#            self.gp.clip_management(inputRaster, coords, OutRaster1)
#        self.gp.Int_sa(OutRaster1, outputRaster)
#        self.gp.BuildRasterAttributeTable_management(outputRaster, "OVERWRITE")
#
#    # clip an area from input raster    
#    def clipRaster(self, inputRaster, outputRaster, coords):
#        if coords is None or coords == '#':
#            self.gp.copy_management(inputRaster, outputRaster)
#        else:
#            self.gp.clip_management(inputRaster, coords, outputRaster)
#        #self.gp.BuildRasterAttributeTable_management(outputRaster, "OVERWRITE")
#
#    # Ceck a list of rasters for having the same extent
#    def GetRasterExtent(self, raster):
#        propertyNames = ['TOP', \
#                         'BOTTOM', \
#                         'LEFT', \
#                         'RIGHT', \
#                         'CELLSIZEX', \
#                         'CELLSIZEY']
#        numProperties = len(propertyNames);
#        extent = [0] * numProperties
#    
#        for i in range(numProperties):
#            extent[i] = self.gp.GetRasterProperties_management(raster, propertyNames[i])
#        
#        return extent
#        
#    def IsSameExtent(self, gp, rasterList):
#        firstRaterExtent = self.GetRasterExtent(rasterList[1])
#        for raster in rasterList[1:]:
#            if not (max(abs(firstRaterExtent - self.GetRasterExtent(raster))) > EPSILON):
#                return False
#        return True
#
#    # converting inputs to proper units
#    def prepareRasters(self):
#        inputsClipped = self.inputsClipped
#        tmp = self.tmp
#        self.gp.Float_sa(inputsClipped.cell_area, tmp.OutRaster2)
#        self.gp.Divide_sa(tmp.OutRaster2, 10, inputsClipped.cell_area)
#        self.gp.Float_sa(inputsClipped.statLayer, tmp.OutRaster2)
#        self.gp.Divide_sa(tmp.OutRaster2, 100, tmp.OutRaster1)
#        self.gp.Times_sa(tmp.OutRaster1, inputsClipped.cell_area, inputsClipped.cell_area_min)
#        
#    # processing results
#    def processResults(self):
#        self.gp.Con_sa(self.outputs.combinedResult[2], self.inputsClipped.statLayer, 
#                       self.outputs.resultStat, "#", "VALUE > 0")
#                       
#    # delete temp rasters
#    def cleanUp(self, list):
#        for rasterName in list:
#            if (self.gp.Exists(rasterName)):
#                self.gp.delete_management(rasterName)
#                
#    # Delete all files from a directory
#    def DeleteDir(self, dir):
#        if os.path.exists(dir):
#            shutil.rmtree(dir)