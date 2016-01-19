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
image_name = image.getTitle()

# Create a duplicate image to compare with
duplicate_image = image.duplicate()

# Filter out noise, keep edges
IJ.run("Median...", "radius=5")
# Find edges
IJ.run("Find Edges");
# Threshold...conservatively!
duplicate_image.show()
IJ.run(image, 'Threshold...', 'Default Dark')
dial = WaitForUserDialog('Threshold all but domains you want. Do not worry about small particles or holes.')
dial.show()

# Select all the particles, deal with ROI's

IJ.run("Make Binary");
IJ.run("ParticleRemoverPy ", "enter=.025");\
IJ.run("Make Binary");
IJ.run("Fill Holes");
IJ.run("Options...", "iterations=4 count=4 black pad do=Close");
IJ.run("Make Binary");

# Now we need to deal with making the same domain have the same color...

IJ.run("Find Connected Regions", "allow_diagonal display_one_image regions_for_values_over=100 minimum_number_of_points=1 stop_after=-1");

image.changes = False
image.close()
duplicate_image.close()

dial = WaitForUserDialog('Use eyedropper to fill same domain with same color.')
dial.show()

connected_image = IJ.getImage()
connected_image.setTitle(image_name)
IJ.run("8-bit");