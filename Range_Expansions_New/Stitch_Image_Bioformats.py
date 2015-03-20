# Stitches an image with bioformats.

from ij import IJ
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
import os
import sys
import ij
import ij.Macro
import plugin.Stitching_Grid as Stiching_Grid

num_dims = 2
# Assumes snake from top-right downwards

IJ.run("Bio-Formats Importer", "open=/home/bryan/btweinstein@gmail.com/Research_Data_Fixed/Nelson/2015_03_11_three_colors/2015_03_19/2015_03_19_threecolor_bioAlpha_rep01-0005.zvi autoscale color_mode=Grayscale open_all_series view=Hyperstack stack_order=XYCZT");
# Grab the window with Tile# in it, save it in a temp folder
temp_folder = '/tmp/stitching/'

# Check if folder is created. If so, clear it. Otherwise, create it.
num_images = num_dims**2
for i in range(num_images):
	cur_image = IJ.getImage()
	# Save it in the temp folder
	IJ.run(cur_image, "Bio-Formats Exporter", "save=/tmp/stitching/" +str(num_images - i)+ ".ome.tif")
	cur_image.close()
# Stitch the images in the temporary folder

# We have to specify these seperately for some reason
IJ.run("Grid/Collection stitching", "type=[Grid: snake by rows] order=[Right & Down                ] grid_size_x=2 grid_size_y=2 tile_overlap=20 first_file_index_i=1 directory=/tmp/stitching file_names={i}.ome.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap subpixel_accuracy computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");
