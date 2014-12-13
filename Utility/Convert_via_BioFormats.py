from ij import IJ
from ij.io import DirectoryChooser
import os
from loci.plugins import BF
from loci.plugins.in import ImporterOptions

inputFolder = DirectoryChooser('Set input directory.').getDirectory()
outputFolder = DirectoryChooser('Set output directory.').getDirectory()
for filename in os.listdir(inputFolder):
	if '.zvi' in filename:
		
		id = inputFolder +'/'+ filename;
		options = ImporterOptions();
		options.setId(id);
		options.setAutoscale(True);
		options.setColorMode(ImporterOptions.COLOR_MODE_GRAYSCALE);
		
		image = BF.openImagePlus(options)[0];
		nameWithoutExt = os.path.splitext(filename)[0]
		# Export the image
		save_path =  outputFolder +'/' + nameWithoutExt + '.ome.tif'
		IJ.run(image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed");
		image.close()