import ij
from ij import IJ
from ij.gui import WaitForUserDialog
import re

image = IJ.getImage()

# Make the image composite
IJ.run('Make Composite', '')
IJ.run('Flatten', '')

# Ask to find annihilations
IJ.run("Point Tool...", "type=Hybrid color=White size=Small label");
IJ.setTool('point')
dial = WaitForUserDialog('Please select annihilations.')
dial.show()

x_coords = image.getRoi().getXCoordinates()
y_coords = image.getRoi().getYCoordinates()
IJ.run("Add Selection...");

IJ.run("Point Tool...", "type=Hybrid color=Black size=Small label");
IJ.setTool('point')
dial = WaitForUserDialog('Please select coalescences.')
dial.show()

x_coords = image.getRoi().getXCoordinates()
y_coords = image.getRoi().getYCoordinates()
IJ.run("Add Selection...");


# Save the image if there is an input, also save the output text file
options = ij.Macro.getOptions()
if options is not None:
	option_keywords = options.split(' ')
	for k in option_keywords:
		key_then_arg = k.split('=')
		if key_then_arg[0] == 'save_path':
			save_path = key_then_arg[1]
			print save_path
			IJ.run(image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed")
		if key_then_arg[0]=='text_file_path':
			text_file_path = key_then_arg[1]
			print 'wakakakakkaa'