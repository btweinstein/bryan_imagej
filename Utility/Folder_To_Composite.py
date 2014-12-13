from ij import IJ
from ij.io import DirectoryChooser
import os

inputFolder = DirectoryChooser('Set input directory.').getDirectory()
outputFolder = DirectoryChooser('Set output directory.').getDirectory()

for filename in os.listdir(inputFolder):
	image = IJ.openImage(inputFolder + '/' + filename);
	print image.getImageStackSize()
	if image.getStackSize() > 1:
		IJ.run(image, 'Make Composite', '')
		image.show()
		IJ.run(image, 'Stack to RGB','')
		image.show()
		image.close()
		newImage = IJ.getImage()
		newImage.show()
		IJ.save(newImage, outputFolder + '/' + filename);
		newImage.close()
	else:
		IJ.run(image, 'RGB Color','')
		IJ.save(image, outputFolder + '/' + filename);
		image.close()