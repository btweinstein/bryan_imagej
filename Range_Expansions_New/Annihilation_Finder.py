import ij
from ij import IJ
from ij.gui import WaitForUserDialog
import re

image = IJ.getImage()

# Delete the brightfield channel
stack = image.getStack()
stack.deleteLastSlice()
# Remove the background from each channel
IJ.run(image, "Subtract Background...", "rolling=400 sliding stack");
# Make the image composite
IJ.run(image, 'Make Composite', '')
IJ.run(image, 'Flatten', '')


# Ask to find annihilations; don't label number to prevent bias
IJ.run("Point Tool...", "type=Hybrid color=Black size=Small");
IJ.setTool('multipoint')
dial = WaitForUserDialog('Please select annihilations.')
dial.show()

annih_x_coords = image.getRoi().getXCoordinates()
annih_y_coords = image.getRoi().getYCoordinates()
IJ.run("Add Selection...");

# Don't label to prevent bias
IJ.run("Point Tool...", "type=Hybrid color=White size=Small");
IJ.setTool('multipoint')
dial = WaitForUserDialog('Please select coalescences.')
dial.show()

coal_x_coords = image.getRoi().getXCoordinates()
coal_y_coords = image.getRoi().getYCoordinates()
IJ.run("Add Selection...");

# Collapse the selection onto the image
IJ.run(image, 'Flatten', '')
# This creates a new image, annoyingly
new_image = IJ.getImage()
# Set the old image equal to the new image
image.setImage(new_image)
image.updateAndDraw()

new_image.close()


# Save the image if there is an input, also save the output text file
options = ij.Macro.getOptions()
if options is not None:
	option_keywords = options.split(' ')
	for k in option_keywords:
		key_then_arg = k.split('=')
		if key_then_arg[0] == 'save_path':
			save_path = key_then_arg[1]
			IJ.run(image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed")
		if key_then_arg[0]=='text_file_path':
			print 'Saving text data...'
			text_file_path = key_then_arg[1]
			print text_file_path
			# Save the data
			f= open(text_file_path +'_annih.txt', 'wb') 
			f.write('r\tc\n')
			for x, y in zip(annih_x_coords, annih_y_coords):
				f.write(str(x)+'\t'+str(y)+'\n')
			f.close()
			f= open(text_file_path +'_coal.txt', 'wb')
			f.write('r\tc\n')
			for x, y in zip(coal_x_coords, coal_y_coords):
				f.write(str(x)+'\t'+str(y)+'\n')
			f.close()