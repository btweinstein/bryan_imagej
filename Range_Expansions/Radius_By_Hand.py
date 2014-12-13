# Java imports
from ij import IJ
from ij.gui import WaitForUserDialog
from loci.plugins import BF
from ij.io import FileSaver
from ij.measure import Measurements
from ij.process import ImageStatistics as IS
from java.awt import Color
from ij import WindowManager
from ij import ImageStack

# Python imports
import socket
import os

# Close results window if it already exists
if WindowManager.getWindow('Results') is not None:
	IJ.selectWindow('Results')
	IJ.run('Close')

image = IJ.getImage()

# If there are multiple slices to the image, take the last one
# as that will be the original. That is our plan here to quickly
# deal with problems!

numSlices = image.getStackSize()
stack = image.getStack()
if numSlices > 1:
	for i in range(numSlices - 1):
		stack.deleteSlice(1)
image.setStack(stack)


IJ.run("Set Measurements...", "  redirect=None decimal=3");

numTimesToMeasure = 5
# Draw the radius N times and record the result
centerList = []
radiusList = []

for i in range(numTimesToMeasure):
	IJ.run("Select None")
	IJ.setTool('line')
	WaitForUserDialog('Draw the radius.').show()
	# Get the center and the radius selected
	currentROI = image.getRoi()
	cx, cy = currentROI.x1, currentROI.y1
	rx, ry = currentROI.x2, currentROI.y2
	# Always assumes you draw from center to radius! If you do
	# not, bad things happen.
	centerList.append([cx, cy])
	radius = ((cx-rx)**2 + (cy-ry)**2)**0.5
	radiusList.append(radius)
	
	IJ.run('Measure')

cx_list = [f[0] for f in centerList]
cy_list = [f[1] for f in centerList]

mean_cx = sum(cx_list)/float(numTimesToMeasure)
mean_cy = sum(cy_list)/float(numTimesToMeasure)
print 'Average Center:' , mean_cx, mean_cy

mean_radius = sum(radiusList)/float(numTimesToMeasure)
print 'Average Radius:' , mean_radius

# Create the overlay image
overlayImage = image.duplicate()
IJ.run(overlayImage, "RGB Color", "")
IJ.run(overlayImage, 'Specify...', 'width=' + str(2*mean_radius) + \
					' height=' + str(2*mean_radius) + \
					' x=' + str(mean_cx) + \
					' y=' + str(mean_cy) + ' oval centered');

roi = overlayImage.getRoi()
overlayImage.setOverlay(roi, Color(246, 27, 27), 10, None)
overlayImage = overlayImage.flatten();

# Now add the overlay image as the first stack

newStack = image.createEmptyStack()
newStack.addSlice(overlayImage.getProcessor())
newStack.addSlice(image.getProcessor())

image.setStack(newStack)

directory = IJ.getDirectory('image')
print directory
name = image.getShortTitle()
print name
# Now save results table. Then done.
IJ.saveAs('Measurements', directory + name + '.txt')
print 'Done saving measurement table!'
# Now overwrite the original image
IJ.saveAsTiff(image, directory + name + '.tif')