'''Finds the sector boundaries, giving us the 
chirality of range expansions.'''

###### Import Stuff #######
import sys
import os
from java.lang.System import getProperty
from ij import IJ

# Add the path of all of my scripts
fijiDir = getProperty("fiji.dir")
myPluginsTop = os.path.join(fijiDir, 'plugins');
myPluginsTop = os.path.join(myPluginsTop, 'Bryan');
walker = os.walk(myPluginsTop)
for root, dirs, files in os.walk(myPluginsTop, topdown=False):
	for name in dirs:
		sys.path.append(os.path.join(root, name))
# Continue
import GlobalRangeVariables_ as globalRangeVariables

radiusToFillIncrease = 1.10

def run(original):
	'''Assumes that there are 3 images. The first two are
	fluorescence, the last one is brightfield.'''

	# Adjust the scale of the original image so that the scale of the unit is of order 1
	adjustScale(original)

	fluorescence, brightfield = separateChannels(original)			
	edges = findRegionEdges(fluorescence)
	# Edges are not pronounced in the homeland: we usually don't
	# have to remove it
	centerX, centerY = getColonyCenter(brightfield)
	diameter = getHomelandDiameter(fluorescence)
	removeHomeland(edges, (centerX, centerY), diameter)
	IJ.run(edges, 'Auto Threshold', 'method=Default white stack');	
	overlay = createEdgeOverlay(fluorescence, edges)

	exportData(edges, (centerX, centerY), original)

def adjustScale(original):
	'''Assuming that the units outported by the Zeiss microscope are mm or \mu-m,
	adjust the units so they are in mm.'''
	pixelWidth = original.getCalibration().pixelWidth
	if pixelWidth > 1:
		newScale = 1000*(1.0/pixelWidth)
		IJ.run("Set Scale...", "distance=" + str(newScale) + " known=1 pixel=1 unit=mm")	

def separateChannels(original):
	'''Separate channels into fluoresence and brightfield.'''
	
	fluorescence = original.duplicate()
	fluorescence.getStack().deleteLastSlice()
	fluorescence.setTitle("Fluorescence")

	brightfield = original.duplicate()
	IJ.run(brightfield, "Delete Slice", "delete=channel")	
	IJ.run(brightfield, "Delete Slice", "delete=channel");
	brightfield.setTitle("Brightfield")
		
	return (fluorescence, brightfield)

def getColonyCenter(brightfield):
	'''Returns the center of the colony based on the brightfield image.
	This will be automated in the future when we have better images. '''
	
	brightfield.show()
	IJ.setTool("point")
	WaitForUserDialog("Please select the center of the homeland. Click OK when done.").show()
	brightfield.hide()
	point = brightfield.getRoi()
	boundingRectangle = point.getBounds()
	xCoord = boundingRectangle.getX()
	yCoord = boundingRectangle.getY()
	return (xCoord, yCoord)

def getHomelandDiameter(fluorescence):
	'''Determine the homeland diameter based on the fluorescence data.'''
	
	fluorescence.show()
	IJ.setTool("line")
	WaitForUserDialog("Please select the diameter of the homeland. Click OK when done.").show()
	fluorescence.hide()
	diameter = fluorescence.getRoi().getLength()
	# Make it uncalibrated for the next step
	pixelWidth = fluorescence.getCalibration().pixelWidth
	uncalibratedDiameter  = diameter/pixelWidth

	return uncalibratedDiameter

def removeHomeland(image, (xCoord, yCoord), diameter):
	'''Select the center and radius of the homeland. In the future
	this will be done automatically.'''
	
	# Adjust the radius slightly so we cover more than just the homeland
	radius = radiusToFillIncrease*(diameter/2.0)
	
	# Create a circlular selection with the given diameter and center
	roi = OvalRoi(int(xCoord - radius), int(yCoord - radius), int(2*radius), int(2*radius))
	image.setRoi(roi)
	IJ.run(image, "Fill", "stack")
	image.killRoi()
	image.show()

def findRegionEdges(image):
	''' Returns the sector boundaries given in the image'''	
	noiseRemoved = image.duplicate()
	IJ.run(noiseRemoved, "Bandpass Filter...", "filter_large=200 filter_small=0 suppress=None tolerance=5 process")
	IJ.run(noiseRemoved, "FeatureJ Edges", "compute smoothing=3 suppress lower=[] higher=[]")
	# Annoyingly, a new edge image is created with featureJ
	edges = IJ.getImage()
	edges.hide()
	IJ.run(edges, '8-bit', '')
	IJ.run(edges, "EnhanceContrastStack ", "saturation=0.75");
	IJ.run(edges, 'Auto Threshold', 'method=Default white stack');

	# Skeletonize the stack, locating the regions.
	IJ.run(edges, "Skeletonize", "stack");
	return edges

def createEdgeOverlay(original, edges):
	biggerEdges = edges.duplicate()
	IJ.run(biggerEdges, "Options...", "iterations=2 count=1 black edm=Overwrite do=Dilate stack");
	
	roiM = RoiManager(True)
	
	IJ.run(biggerEdges, "Create Selection", "")
	IJ.run(biggerEdges, "Make Inverse", "");
	roiM.addRoi(biggerEdges.getRoi())
	
	overlayImage = original.duplicate()
	overlayImage.setTitle("Overlay")
	IJ.run(overlayImage, "Make Composite", "")
	IJ.run(overlayImage, "Stack to RGB", "")
	roiM.runCommand("Fill")
	
	overlayImage.hide()
	return overlayImage

def exportData(edges, (centerX, centerY), original):
	'''Exports all of the sectors x y positions.'''
	# Note that this should be the terminal step, i.e. after
	# this should just be analysis of sectors, i.e. no linking! All linking
	# or preprocessing should be done in ImageJ, in my opinion.'''
	# Only export data for one set of edges right now
	
	roiM = RoiManager(True)
	ParticleAnalyzer.setRoiManager(roiM)
	IJ.run(edges, "Analyze Particles...", "size=0-Infinity circularity=0.00-1.00 show=Nothing include add slice");

	# Open the location where output files will be written
	originalTitle = original.getShortTitle()	
	outputFilePath = globalRangeVariables.chiralityFolder + '/' + originalTitle + '.txt'		
	if os.path.isfile(outputFilePath):
		os.remove(outputFilePath)
	outputFile = open(outputFilePath, 'a')

	unit = original.getCalibration().getUnit()
	outputFile.write(unit + '\n')
	
	# The label -1 corresponds to the center!
	outputFile.write('-1' + '\t' + str(centerX) + '\t' + str(centerY) + '\n')

	labelCount = 0
	for roi in roiM.getRoisAsArray():
		polygon = roi.getPolygon()
		xpoints = polygon.xpoints
		ypoints = polygon.ypoints
		for x, y in zip(xpoints, ypoints):
			outputFile.write(str(labelCount) + '\t' + str(x) + '\t' + str(y) + '\n')		
		labelCount += 1
	outputFile.close()
######### Actually run the program #######

image = IJ.getImage()
run(image)