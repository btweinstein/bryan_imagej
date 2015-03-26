# Stitches an image with bioformats.
from ij import IJ
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
import os
import sys
import ij
import ij.Macro
import plugin.Stitching_Grid as Stiching_Grid
import shutil
import tempfile

num_dims = 2
# Assumes snake from top-right downwards, 20% overlap

input_file_path = IJ.getFilePath('Choose an input file.')
# Get file name
filename_without_extension = os.path.basename(input_file_path).split('.')[0]
output_dir_path = IJ.getDirectory('Choose output directory.')

IJ.run("Bio-Formats Importer", "open="+ input_file_path +" autoscale color_mode=Grayscale open_all_series view=Hyperstack stack_order=XYCZT");
# Grab the window with Tile# in it, save it in a temp folder
temp_folder = tempfile.gettempdir() + '/stitching/'

# Check if folder is created. If so, clear it. Otherwise, create it.
if os.path.isdir(temp_folder):
	shutil.rmtree(temp_folder)
os.makedirs(temp_folder)

num_images = num_dims**2
for i in range(num_images):
	cur_image = IJ.getImage()
	# Save it in the temp folder
	IJ.run(cur_image, "Bio-Formats Exporter", "save=/tmp/stitching/" +str(num_images - i)+ ".ome.tif")
	if i < num_images - 1: # keep the last image open for metadata purposes
		cur_image.close()
# Stitch the images in the temporary folder
IJ.run("Grid/Collection stitching", "type=[Grid: snake by rows] order=[Right & Down                ] grid_size_x=2 grid_size_y=2 tile_overlap=20 first_file_index_i=1 directory=/tmp/stitching file_names={i}.ome.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=3 absolute_displacement_threshold=7 compute_overlap subpixel_accuracy computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");

# Save and get metadata
fused_image = IJ.getImage()

# Set the scale globally based on the original image
fused_image.setCalibration(cur_image.getCalibration())

cur_image.setImage(fused_image) # Since we set the global scale, everything works ok
fused_image.close()
cur_image.setTitle(filename_without_extension)

save_path = output_dir_path + filename_without_extension + '.ome.tif'
IJ.run(cur_image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed")