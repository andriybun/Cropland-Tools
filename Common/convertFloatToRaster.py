import arcgisscripting
import sys

if __name__ == "__main__":
	gp = arcgisscripting.create()
	gp.OverWriteOutput = 1
	gp.FloatToRaster_conversion(sys.argv[1], sys.argv[2])
