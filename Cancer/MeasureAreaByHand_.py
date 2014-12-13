'''To be run on the server with an X11 window and a FAST connection,
preferably on Harvard campus.'''

# Java imports
from ij import IJ
from ij.gui import WaitForUserDialog
from loci.plugins import BF
from ij.io import FileSaver
from ij.measure import Measurements
from ij.process import ImageStatistics as IS
from java.awt import Color

# Python imports
import socket
import os

#### Variables to set ####
hostname = socket.gethostname()
print 'Computer name is' , hostname
inputDirectory = None
thumbnailDirectory = None
if hostname == 'dawnofhope':
	inputDirectory = 'TODO'
	thumbnailDirectory = 'TODO'
elif hostname == 'Chompert':
	inputDirectory = 'TODO'
	thumbnailDirectory = 'TODO'
else:
	inputDirectory = '/tmp/queried_images'
	thumbnailDirectory = '/home/bweinstein/apps/OMERO/thumbnails'
outputFile = 'Areas.txt' # Goes in the input directory

#### Utility Functions ####
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
	
#### Main Stuff #####

outputFilePath = inputDirectory + '/' + outputFile
if os.path.isfile(outputFilePath):
	os.remove(outputFilePath)
outputFile = open(outputFilePath, 'a')

for fileName in os.listdir(inputDirectory):
	print 'Processing Image ' , fileName
	if '.tif' in fileName:
		#print 'Opening image...'
		imps = BF.openImagePlus(os.path.join(inputDirectory, fileName))
		image = imps[0]
		image.show()
		# Select tumor
		WaitForUserDialog("Select the tumor by hand.").show()
		# Measure Area
		currentROI = image.getROI()
		image.setRoi(currentRoi)
		stats = image.getStatistics(Measurements.AREA)
		currentArea = stats.area
		image.killRoi()

		# Create an overlay
		if currentROI is not None:
			overlayImage = createOverlay(image, selectedROI)
		else:
			overlayImage = image.duplicate() # I didn't feel like deleting the stack again
		overlayFileName = thumbnailDirectory + '/' + image.getShortTitle() + '.png'
		FileSaver(overlayImage).saveAsPng(overlayFileName)
				
		outputFile.write(image.getTitle() + '\t' + str(currentArea) + '\n')
outputFile.close()
print 'Done!'