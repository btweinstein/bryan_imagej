from ij import IJ
import ij.gui
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
import os
import sys
import ij
import ij.Macro
from ij.process import ImageProcessor
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer
from ij.measure import Measurements

# Parameters are tuned for the plate reader downstairs.

image = IJ.getImage()
original_image = image.duplicate()

x_centroid_list = []
y_centroid_list = []

def filter_original():
	# Filter out noise, keep edges
	IJ.run("Median...", "radius=4")
	# Enhance contrast
	IJ.run("Enhance Local Contrast (CLAHE)", "blocksize=19 histogram=256 maximum=3 mask=*None*");
	# Find edges
	IJ.run("Find Edges");
	# Threshold...conservatively!
	IJ.run('Threshold...', 'Default Dark')
	dial = WaitForUserDialog('Please threshold conservatively.')
	dial.show()
	
	# Now run the hough circles
	IJ.run("Hough Circles", "minimum=8 maximum=9 increment=1 number=0 threshold=0")
	image.changes = False
	image.close()
	
	# Select the hough space image
	dial = WaitForUserDialog('Select the hough space image.')
	dial.show()
	
	# Filter out all but the small points
	#IJ.run("Bandpass Filter...", "filter_large=7 filter_small=4 suppress=None tolerance=5 autoscale saturate")
	
	# Threshold the centers of the points
	IJ.run('Threshold...', 'Default Dark')
	dial = WaitForUserDialog('Please threshold circle centers. Should be near max.')
	dial.show()
	
	# Select all the particles, deal with ROI's
	
	IJ.run("Analyze Particles...", "size=0-Infinity include add");

def filter_hough():
	new_image = IJ.getImage()
	# Get the roi manager
	roi_manager = RoiManager.getInstance()
	roi_array = roi_manager.getRoisAsArray()

	for cur_roi in roi_array:
		new_image.setRoi(cur_roi)
		stats = new_image.getStatistics(Measurements.CENTROID)
		x_centroid_list.append(stats.xCentroid)
		y_centroid_list.append(stats.yCentroid)

	# Close the new image
	new_image.killRoi() # Remove the remaining ROI
	roi_manager.runCommand("Reset")
	roi_manager.runCommand("Close")
	new_image.changes = False
	new_image.close()

def show_and_select_colonies():
	original_image.show()
	IJ.run("Point Tool...", "type=Hybrid color=Red size=Small");
	if len(x_centroid_list) != 0:
		points = ij.gui.PointRoi(x_centroid_list, y_centroid_list, len(x_centroid_list))
		original_image.setRoi(points, True)
		
	IJ.setTool('multipoint')
	dial = WaitForUserDialog('Please select colonies.')

filter_original()
filter_hough()
show_and_select_colonies()