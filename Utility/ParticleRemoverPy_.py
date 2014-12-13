# Java Imports
from ij import IJ
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer
import os
import sys


#### Utility #####

def particleRemover(image, minArea):
	'''Send in a thresholded image, remove the small spots'''
	numSlices = image.getImageStackSize()
	particleRoiM = RoiManager(True)
	ParticleAnalyzer.setRoiManager(particleRoiM)
	IJ.run(image, "Analyze Particles...", "size=0-" + str(minArea) + " circularity=0.00-1.00 include show=Nothing add stack");
	# Set the fill color to black before filling
	IJ.setForegroundColor(0, 0, 0);
	particleRoiM.runCommand("Fill");
	particleRoiM.runCommand("Reset");

def run():
	image = IJ.getImage()
	minArea = IJ.getNumber("Enter area cutoff: " , 1)
	particleRemover(image, minArea)

##### Main Function ###
run()