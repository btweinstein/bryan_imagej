from ij import IJ
from ij.plugin.filter import ParticleAnalyzer
from ij.plugin.frame import RoiManager
from ij.measure import Calibration
from loci.plugins import BF
from ij.io import FileSaver
from ij.measure import Measurements
from ij.process import ImageStatistics as IS
from java.awt import Color
# Python imports
import os
import math
import sys
import socket

#### Variables to set ####
hostname = socket.gethostname()
print hostname
inputDirectory = None
thumbnailDirectory = None
if hostname == 'dawnofhope':
	inputDirectory = '/home/bryan/Desktop/queried_images'
	thumbnailDirectory = '/home/bryan/Desktop/queried_images/thumbnails'
elif hostname == 'Chompert':
	inputDirectory = 'C:/Users/chompy_local/Desktop/queried_images'
	thumbnailDirectory = 'C:/Users/chompy_local/Desktop/queried_images/thumbnails'
else:
	inputDirectory = '/tmp/queried_images'
	thumbnailDirectory = '/home/bweinstein/apps/OMERO/thumbnails'
outputFile = 'Areas.txt' # Goes in the input directory
minimumCancerArea = 0.03
maxCancerArea = 1
circularityCutoff = .65 # Dimensionless
backgroundRadius = 30 # in pixels
medianSmoothing = 5 # in pixels

############# Auxillary Functions #########
def locateTumors(imp):
	'''Locates the tumors in an image; white is location, black is not'''
	# Determine if the tumor is black on a white background or white
	# on a black background
	ip = imp.getProcessor()
	stats = IS.getStatistics(ip, IS.MEAN, imp.getCalibration())
	mean = stats.mean
	if mean >= 20: # Black tumor on white background
		IJ.run(imp, 'Subtract Background...', 'rolling=' + str(backgroundRadius) + ' light sliding stack');
		IJ.run(imp, "Invert", "stack")
	else:
		IJ.run(imp, 'Subtract Background...', 'rolling=' + str(backgroundRadius) + ' sliding stack');
	IJ.run(imp, 'Median...', 'radius=' + str(medianSmoothing))
	IJ.run(imp, 'Auto Threshold', 'method=MaxEntropy white stack')
	# Remove small
	IJ.setForegroundColor(0, 0, 0);
	IJ.run(imp, 'ParticleRemoverPy ', 'enter=' + str(minimumCancerArea));
	IJ.run(imp, "Close-", "stack")
	# Make sure black background binary is set!
	IJ.run(imp, "Options...", "iterations=1 count=1 black edm=Overwrite");
	IJ.run(imp, 'Fill Holes', "stack")
	IJ.run(imp, 'Watershed', "stack")
	IJ.run(imp, 'ParticleRemoverPy ', 'enter=' + str(minimumCancerArea));
	
def measureTumor(original, locations):
	'''Returns the area from the original image with the 
	highest kurtosis which generally corresponds to the most
	in focus image. Also saves an image corresponding to a mask
	of the measurement.'''
	# Prevent ROI manager from appearing
	roiM = RoiManager(True)
	ParticleAnalyzer.setRoiManager(roiM)
	# Locate particles above a minimum size and with a desired circularity
	IJ.run(locations, "Analyze Particles...", "size=" + str(minimumCancerArea) +"-" + str(maxCancerArea) +" circularity=" + str(circularityCutoff) + "-1.00 show=Nothing exclude add stack");
	# Choose ROI with the highest kurtosis
	maxKurtosis = None
	area = None
	selectedROI = None
	for roi in roiM.getRoisAsArray():
		original.setRoi(roi)
		stats = original.getStatistics(Measurements.KURTOSIS, Measurements.AREA)
		currentKurtosis = stats.kurtosis
		if currentKurtosis > maxKurtosis:
			maxKurtosis = stats.kurtosis
			area = stats.area
			selectedROI = roi
	original.killRoi() # Remove the remaining ROI
	roiM.runCommand("Reset")
	return (area, selectedROI)

def createOverlay(image, selectedROI):
	overlayImage = image.duplicate()
	# Convert to RGB
	IJ.run(overlayImage, "RGB Color", "")
	overlayImage.setOverlay(selectedROI, Color(246, 27, 27), 3, None)
	roiSliceNumber = selectedROI.getPosition()
	totalNumSlices = overlayImage.getStackSize()
	count = 0
	roiPassed = False
	for i in range(totalNumSlices):
		count += 1
		if not roiPassed:
			overlayImage.setSlice(1)
			if count == roiSliceNumber:
				roiPassed = True
			else:
				IJ.run(overlayImage, "Delete Slice", "")
		else:
			overlayImage.setSlice(2)
			IJ.run(overlayImage, "Delete Slice", "")
	return overlayImage

############## Main Process ###############

# Check if output file exists
outputFilePath = inputDirectory + '/' + outputFile
if os.path.isfile(outputFilePath):
	os.remove(outputFilePath)
outputFile = open(outputFilePath, 'a')

for fileName in os.listdir(inputDirectory):
	print 'Processing Image ' , fileName
	if '.tif' in fileName:
		#print 'Opening image...'
		imps = BF.openImagePlus(os.path.join(inputDirectory, fileName))
		originalImage = imps[0]
	
		# Resize the image
		numSlices = originalImage.getStackSize()
		IJ.run(originalImage, "Size...", "width=347 height=260 depth=" + str(numSlices) +" constrain average interpolation=Bicubic");
		
		# Make 8 bit
		IJ.run(originalImage, '8-bit', '')
		tumorLocations = originalImage.duplicate()
		print 'Locating tumors...'
		locateTumors(tumorLocations)
		(area, selectedROI) = measureTumor(originalImage, tumorLocations)
		print 'Area:' , area
		print 'Creating thumbnail of overlay:'
		if selectedROI is not None:
			overlayImage = createOverlay(originalImage, selectedROI)
		else:
			overlayImage = originalImage.duplicate() # I didn't feel like deleting the stack again
		overlayFileName = thumbnailDirectory + '/' + originalImage.getShortTitle() + '.png'
		FileSaver(overlayImage).saveAsPng(overlayFileName)
		# Finally write what the area is
		outputFile.write(originalImage.getTitle() + '\t' + str(area) + '\n')
# Close the original file
outputFile.close()
print 'Done!'