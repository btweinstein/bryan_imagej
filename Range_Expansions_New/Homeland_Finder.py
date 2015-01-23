from ij import IJ
import ij.gui
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
import os
import sys
import ij
import ij.Macro
from ij.process import ImageProcessor

# Get  the last slice; assume it is always brightfield
image = IJ.getImage()

stack = image.getStack()
stack.deleteLastSlice()

# Have the user select the circle corresponding to where they want to cutoff 
# the homeland...but first make it easy to tell where to do it
IJ.run('Make Composite', '')
IJ.run('Flatten', '')

image.show()
dial = WaitForUserDialog('Please fit a circle to where you want to cutoff the homeland.')
dial.show()
IJ.run(image, 'Create Mask', '')
IJ.selectWindow('Mask')
mask_image = IJ.getImage()
image.close()

# Save the image if there is an input
options = ij.Macro.getOptions()
if options is not None:
	options = options.split('=')
	if options[0] == 'save_path':
		save_path = options[1]
		IJ.run(mask_image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed")