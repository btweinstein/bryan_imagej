from ij import IJ
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
import os
import sys
import ij
import ij.Macro

# Delete the last slice; assume it is always brightfield
image = IJ.getImage()

# Run a fft on the image to reduce background...assumes we are working with the stiched images
#IJ.run(image, "Bandpass Filter...", "filter_large=1000 filter_small=0 suppress=None tolerance=5 autoscale saturate process");

stack = image.getStack()
stack.deleteLastSlice()

# Split the channels
channel_images = ChannelSplitter.split(image)
image.hide()

# Cycle through each image, threshold
for current_image in channel_images:
	current_image.show()
	IJ.run(current_image, 'Threshold...', 'Default Dark')
	dial = WaitForUserDialog('Threshold please. Probably use CLAHE beforehand, \nblocksize=25, histbins=2048, slope=20, select region. ')
	dial.show()
	IJ.resetMinAndMax()
	current_image.hide()

# Combine images into one stack
IJ.run(image, '8-bit', '');

image_stack = image.getStack()

num_channels = len(channel_images)
for i in range(num_channels):
	cur_image = channel_images[i]
	cur_ip = cur_image.getProcessor()
	image_stack.setProcessor(cur_ip, i + 1)
	image.setStack(image_stack)

image.show()

# Save the image if there is an input
options = ij.Macro.getOptions()
if options is not None:
	options = options.split('=')
	if options[0] == 'save_path':
		save_path = options[1]
		IJ.run(image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed")