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

# Have the user select the circle, perhaps multiple times for error analysis purposes
num_repetitions  = 3

binary_list = []
for i in range(num_repetitions):
	image.show()
	dial = WaitForUserDialog('Please fit a circle to the homeland.')
	dial.show()
	IJ.run(image, 'Create Mask', '')
	IJ.selectWindow('Mask')
	mask_image = IJ.getImage()
	mask_image.hide()
	binary_list.append(mask_image)
	IJ.run(image, "Select None", '')

# Combine images into one stack
IJ.run(image, '8-bit', '');

image_stack = image.createEmptyStack()

for i in range(num_repetitions):
	cur_image = binary_list[i]
	cur_ip = cur_image.getProcessor()
	image_stack.addSlice(cur_ip)
	image.setStack(image_stack)

image.show()

# Save the image if there is an input
options = ij.Macro.getOptions()
if options is not None:
	options = options.split('=')
	if options[0] == 'save_path':
		save_path = options[1]
		IJ.run(image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed")