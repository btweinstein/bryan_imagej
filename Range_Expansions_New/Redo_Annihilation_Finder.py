import ij
from ij.io import OpenDialog
import ij.macro
from ij import IJ
from ij.gui import WaitForUserDialog
import re
import csv

# Choose file
file_chooser = OpenDialog('Choose input file')
image_path = file_chooser.getPath()
file_name = file_chooser.getFileName()
directory_name = file_chooser.getDirectory()

# Determine annihilation & coalescence folder names
base_name = file_name.split('.')[0]
annih_name = base_name + '_annih.txt'
coal_name = base_name + '_coal.txt'

annih_path = directory_name + annih_name
coal_path = directory_name + coal_name

# Read in annihilations and coalescences

f = open(annih_path)
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

f = open(coal_path)
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
IJ.run(image, "Subtract Background...", "rolling=400 sliding stack");
# Make the image composite
IJ.run(image, 'Make Composite', '')
IJ.run(image, 'Flatten', '')

#### Do Annihilations ####

# Ask to find annihilations; don't label number to prevent bias
IJ.run("Point Tool...", "type=Hybrid color=Black size=Small");
points = ij.gui.PointRoi(annih_x, annih_y, len(annih_x))
image.setRoi(points, True)