from ij import IJ
import ij.gui
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
import os
import sys
import ij
import ij.Macro
from ij.process import ImageProcessor
from ij.io import DirectoryChooser
import glob

base_folder = DirectoryChooser('Set input directory.').getDirectory()
tif_folder = base_folder + 'tif/'
image_list = glob.glob(tif_folder + '*.tif')
image_list = [os.path.basename(k) for k in image_list]

image_list.sort()

radius_folder = base_folder + 'circle_radius/'

if not os.path.exists(radius_folder):
	print 'Making', radius_folder
	os.makedirs(radius_folder)

# Loop over files in the radius folder and open & act on them
for image_name in image_list:
	file_path = tif_folder + image_name
	IJ.run("Bio-Formats", "open=" + file_path +" autoscale color_mode=Grayscale view=Hyperstack stack_order=XYCZT");
	IJ.run('Fast Radius Finder')
	# Save the file
	output_path = radius_folder + image_name
	IJ.run(image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed")