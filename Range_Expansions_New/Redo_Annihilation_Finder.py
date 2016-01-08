import ij
from ij.io import OpenDialog
import ij.macro
from ij import IJ
from ij.gui import WaitForUserDialog
import re
import csv
import os

# Choose file
file_chooser = OpenDialog('Choose input file')
image_name = file_chooser.getFileName()
directory_name = file_chooser.getDirectory()
annih_image_path = file_chooser.getPath()
# The parent folder doesn't work correctly if we don't get rid of / at the end
image_path = os.path.dirname(directory_name[:-1]) + '/tif/' + image_name

# Determine annihilation & coalescence folder names
base_name = image_name.split('.')[0]
annih_name = base_name + '_annih.txt'
coal_name = base_name + '_coal.txt'

annih_path = directory_name + annih_name
coal_path = directory_name + coal_name

# Read in annihilations and coalescences

f = open(annih_path, 'rb')
annih_reader = csv.reader(f, delimiter='\t')
annih_x = []
annih_y = []
count = 0
for row in annih_reader:
	if count != 0:
		annih_x.append(int(row[0]))
		annih_y.append(int(row[1]))
	count += 1
f.close()

f = open(coal_path, 'rb')
coal_reader = csv.reader(f, delimiter='\t')
coal_x = []
coal_y = []
count = 0
for row in coal_reader:
	if count != 0:
		coal_x.append(int(row[0]))
		coal_y.append(int(row[1]))
	count += 1
f.close()

#### Image preprocessing ##### 

IJ.run("Bio-Formats", "open=" + image_path +" autoscale color_mode=Grayscale view=Hyperstack stack_order=XYCZT")

image = IJ.getImage()

# Delete the brightfield channel
stack = image.getStack()
stack.deleteLastSlice()
# Remove the background from each channel
#IJ.run(image, "Subtract Background...", "rolling=800 sliding stack");
# Make the image composite
IJ.run(image, 'Make Composite', '')
IJ.run(image, 'Flatten', '')

#### Do Annihilations ####

# Ask to find annihilations; don't label number to prevent bias
IJ.run("Point Tool...", "type=Hybrid color=Black size=Small");
if len(annih_x) != 0:
	points = ij.gui.PointRoi(annih_x, annih_y, len(annih_x))
	image.setRoi(points, True)

IJ.setTool('multipoint')
dial = WaitForUserDialog('Please select annihilations.')
dial.show()

annih_x_coords_new = image.getRoi().getPolygon().xpoints
annih_y_coords_new = image.getRoi().getPolygon().ypoints
IJ.run("Add Selection...");

# Don't label to prevent bias
IJ.run("Point Tool...", "type=Hybrid color=White size=Small");
if len(coal_x) != 0:
	points = ij.gui.PointRoi(coal_x, coal_y, len(coal_x))
	image.setRoi(points, True)

IJ.setTool('multipoint')
dial = WaitForUserDialog('Please select coalescences.')
dial.show()

coal_x_coords_new = image.getRoi().getPolygon().xpoints
coal_y_coords_new = image.getRoi().getPolygon().ypoints
IJ.run("Add Selection...");

# Collapse the selection onto the image
IJ.run(image, 'Flatten', '')
# This creates a new image, annoyingly
new_image = IJ.getImage()
# Set the old image equal to the new image
image.setImage(new_image)
image.updateAndDraw()
image.updateAndRepaintWindow()
image.updateImage()

new_image.close()

image = IJ.getImage()

# Since we are redoing, automatically save the image in the correct location
# as well as the output txt files.

# Delete the input image...otherwise *bizarre* things happen...
os.remove(annih_image_path)
IJ.run(image, "Bio-Formats Exporter", "save=" + annih_image_path + " compression=Uncompressed")

print 'Saving text data...'

# Save annihilations

f= open(annih_path, 'wb') 
f.write('c\tr\n')
for x, y in zip(annih_x_coords_new, annih_y_coords_new):
	f.write(str(x)+'\t'+str(y)+'\n')
f.close()
f= open(coal_path, 'wb')
f.write('c\tr\n')
for x, y in zip(coal_x_coords_new, coal_y_coords_new):
	f.write(str(x)+'\t'+str(y)+'\n')
f.close()