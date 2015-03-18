from ij import IJ
from ij.io import DirectoryChooser
import os

inputFolder = DirectoryChooser('Set input directory.').getDirectory()
outputFolder = DirectoryChooser('Set output directory.').getDirectory()

for filename in os.listdir(inputFolder):
	IJ.run("Bio-Formats", "open=" + inputFolder + filename +" autoscale color_mode=Grayscale view=Hyperstack stack_order=XYCZT");
	image = IJ.getImage()
	if image.getImageStackSize() > 1:
		IJ.run(image, 'Make Composite', '')
		IJ.run(image, 'Flatten', '')
	else:
		# Save as png...we no longer need 16 bit, as this makes the output more annoying
		IJ.run("8-bit")
	image.changes=False

	filename_plus_png = filename.split('.')[0] + '.png'
	IJ.run(image, "Bio-Formats Exporter", "save=" + outputFolder + filename_plus_png + " compression=Uncompressed")
	image.close()