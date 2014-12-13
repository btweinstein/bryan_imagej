from ij import IJ
from ij.plugin.filter import ParticleAnalyzer
from ij.plugin.frame import RoiManager
from ij.measure import Calibration
from loci.plugins import BF
from ij.io import FileSaver
from ij.measure import Measurements
from ij.process import ImageStatistics as IS
from java.awt import Color
from ij.io import DirectoryChooser
# Python imports
import os
import math
import sys

# Choose a folder that you want the images resized to the same scale
input_dc = DirectoryChooser("Choose a folder with images to be rescaled.")
inputDir = input_dc.getDirectory()

output_dc = DirectoryChooser("Choose output folder.")
outputDir = output_dc.getDirectory()

# What we need to do is crop EQUAL AREAS. First find the smallest
# image area.

# Find the minimum area per pixel
minArea = 999999
for filename in os.listdir(inputDir):
	if '.tif' in filename:
		print 'Opening ' , filename , '...'
		image = IJ.openImage(inputDir + '/' + filename)
		ip = image.getProcessor()
		
		stats = IS.getStatistics(ip, IS.AREA, image.getCalibration())
		currentArea = stats.area
		if currentArea < minArea:
			minArea = currentArea

# Cut smaller than the minArea so that your cut does not run into 
# any barriers
minArea = minArea/4

# Now loop and crop the images
for filename in os.listdir(inputDir):
	if '.tif' in filename:
		print 'Cropping ' , filename , '...'
		image = IJ.openImage(inputDir + '/' + filename)

		# Get the calibration
		cal = image.getCalibration()
		# Assumes pixel width and height are the same
		pixelWidth = cal.pixelWidth
		pixelHeight = cal.pixelHeight
		# Locate the center
		imageWidth = image.getWidth()
		imageHeight = image.getHeight()
		centerX = imageWidth/2.0
		centerY = imageHeight/2.0

		# Figure out the coordinates to cut to get the area you want.
		# Make an equal sized cut in both dimensions.
		cutLength = math.sqrt(minArea)
		
		cutLengthX = cutLength/pixelWidth
		cutLengthY = cutLength/pixelHeight
		
		leftX = centerX - cutLengthX/2.0
		topY = centerY - cutLengthY/2.0

		image.setRoi(int(leftX), int(topY), int(cutLengthX), int(cutLengthY))
		IJ.run(image, "Crop", "")
		# Crop the image
		image.show()
		pathToSave = outputDir + '/' + image.getShortTitle() + '.tif'
		FileSaver(image).saveAsPng(pathToSave)