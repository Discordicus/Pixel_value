from ij import IJ, ImagePlus
from ij.measure import ResultsTable
from ij.process import ImageProcessor
from ij.plugin.frame import RoiManager
from ij.io import DirectoryChooser
import sys
import os

sourceDir = DirectoryChooser("Choose a root folder").getDirectory()
pixValues = []


# This function calculates the pixel value from the currently loaded image. Returns pixel value as a float "pixel"
def getPixelValue(imp):
	ip = imp.getProcessor() # get ImageProcessor
	imp2 = ImagePlus(imp.getTitle() + " Copy", ip) # make a copy of image to preserve original
	
	
	IJ.run(imp2, "Enhance Contrast", "saturated=0.35"); # enhance contrast of image

	## the following function iteratively creates an ROI around a picket, finds the local maxima,
	## averages them and adds them to a list 'centers'. The average distance between the three pickets is returned as 'diff'
	IJ.run("Remove Overlay", "");
	rm = RoiManager.getRoiManager();
	centers = []
	for i in range(0,3):
		imp2.setRoi((25 + 425*i),50,125,900);
		IJ.run(imp2, "Add Selection...", "");
		rm.select(i);
		IJ.run(imp2, "Find Maxima...", "prominence=10 strict exclude light output=List");
		IJ.run("Summarize", "");
		res = ResultsTable.getResultsTable()
		xcood = res.getColumn(0)
		centers.insert(i, xcood[len(xcood) - 4])
		IJ.run("Close");
	
	rm.close()

	
	avgDiff = sum([(centers[1]- centers[0]), (centers[2]- centers[1]), ((centers[2] - centers[0])/2.)])/len(centers)
	pixel = 105/avgDiff
	return pixel


# This function is a helper function that takes a file path and arbitrary function as arguments, 
# and appends the value returned from the given arbitrary function to the global list pixValues
def loadAndProcess(sourcepath, fn):  
	global pixValues
	imp = IJ.openImage(sourcepath) 
	pixValues.append(fn(imp))
	imp.close()


	

for root, directories, filenames in os.walk(sourceDir):  
	for filename in filenames:
		if (filename.endswith(".dcm")):
			loadAndProcess(os.path.join(root, filename), getPixelValue)
		else:
			IJ.showMessage("Warning!", filename + " is not a Dicom image. \nPlease ensure all folders and subfolders contain only \".dcm\" files." +
				"\nThis plugin will now exit.")
			sys.exit()

IJ.run("Close All")

pixVal = sum(pixValues)/len(pixValues)


IJ.showMessage("Calculation Complete", "Calculated Pixel Value is: " + str(pixVal))