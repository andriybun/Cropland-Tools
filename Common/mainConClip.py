#===============================================================================
# Conditional clip
#===============================================================================
import sys
from common import *

if __name__ == "__main__":
    inConditionalLayer = sys.argv[1]
#    inValueLayer       = sys.argv[2]
    inValueLayerVector = (sys.argv[2].replace("'","")).split(";")
    
    numRasters         = len(inValueLayerVector)    
    
    condition          = sys.argv[3]
    outLayer           = sys.argv[4]
    
    outLayerVector     = []
    
    if numRasters > 1:
        resultDir = os.path.dirname(outLayer)
        for raster in inValueLayerVector:
            outLayerVector.append(resultDir + "\\cl_" + os.path.basename(raster))
        ConClip(inConditionalLayer, inValueLayerVector, condition, outLayerVector)
    else:
        outLayerVector.append(outLayer)
        ConClip(inConditionalLayer, inValueLayerVector, condition, outLayerVector)

    