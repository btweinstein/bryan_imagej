from ij import IJ
from ij.io import DirectoryChooser
import os

inputFolder = DirectoryChooser('Set input directory.').getDirectory()
outputFolder = DirectoryChooser('Set output directory.').getDirectory()

for filename in os.listdir(inputFolder):
	IJ.run("Bio-Formats", "open=" + inputFolder + filename +" autoscale color_mode=Grayscale view=Hyperstack stack_order=XYCZT");
	image = IJ.getImage()
	IJ.run(image, "Subtract Background...", "rolling=800 sliding stack");
	IJ.run("Bio-Formats Exporter", "save=" + outputFolder + filename + " compression=Uncompressed")
	image.close()