from ij import IJ
from ij.io import DirectoryChooser
import os

inputFolder = DirectoryChooser('Set input directory.').getDirectory()
outputFolder = DirectoryChooser('Set output directory.').getDirectory()

for filename in os.listdir(inputFolder):
	IJ.run("Bio-Formats", "open=" + inputFolder + filename +" autoscale color_mode=Grayscale view=Hyperstack stack_order=XYCZT");
	image = IJ.getImage()
	IJ.run('Make Composite', '')
	IJ.run('Flatten', '')
	# Save as png
	filename_plus_png = filename.split('.')[0] + '.png'
	IJ.run("Bio-Formats Exporter", "save=" + outputFolder + filename_plus_png + " compression=Uncompressed")
	image.close()