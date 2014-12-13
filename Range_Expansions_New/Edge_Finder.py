from ij import IJ
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
import os
import sys
import ij
import ij.Macro

# Delete the last slice; assume it is always brightfield
image = IJ.getImage()
stack = image.getStack()
stack.deleteLastSlice()

# Cycle through each image
IJ.run(image, "Bandpass Filter...", "filter_large=20 filter_small=0 suppress=None tolerance=5 process");
IJ.run(image, "Median...", "radius=7 stack");
IJ.run(image, "Find Edges", "stack");
# Convert to 8-bit, regretably. Not sure if I have to do this.
IJ.run(image, "8-bit", "")
image.updateAndDraw()

# Annoyingly, we will have to binarize each slice individually, as ImageJ
# does not like to do it all at once
for i in range(1, image.getStackSize() + 1):
	IJ.setSlice(i)
	curImage = IJ.getImage()
	IJ.run(curImage, 'Threshold...', 'Default Dark')
	dial = WaitForUserDialog('Threshold please')
	dial.show()
	IJ.resetMinAndMax()

# Now binarize
IJ.run(curImage, 'Make Binary', 'method=Default background=Dark black stack')

# Save the image if there is an input

options = ij.Macro.getOptions()
if options is not None:
	options = options.split('=')
	if options[0] == 'save_path':
		save_path = options[1]
		IJ.run(image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed")