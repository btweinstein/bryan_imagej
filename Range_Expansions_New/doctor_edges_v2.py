import ij
from ij import IJ
import ij.plugin
import ij.gui
import ij.Macro

image = IJ.getImage()
num_channels = image.getImageStackSize()

# Parse options
options = ij.Macro.getOptions()
if options is not None:
	option_keywords = options.split(' ')
else:
	option_keywords = None
# Create a shortcut for the command "highlight_roi" to speed this up

# Split image into three; assumes you are inputting binary
# If you input the input image path, automatically use that as the overlay
overlay_path = None
if options is not None:
	for k in option_keywords:
		key_then_arg = k.split('=')
		if key_then_arg[0] == 'overlay_path':
			overlay_path = key_then_arg[1]

# Open the overlay image; there will be an option to pass in this value
if overlay_path is not None:
	overlay_image = IJ.openImage(overlay_path)
else:
	overlay_image = IJ.openImage()
overlay_image.setTitle('overlay_image')

for i in range(num_channels):
	image.setSlice(i + 1)
	overlay_image.setSlice(i+1)
	overlay_image.show()
	# Add the correct image to the overlay
	IJ.run(image, 'Add Image...', 'x=0 y=0 image=overlay_image opacity=90')
	overlay_image.hide()
	wait_dialog = ij.gui.WaitForUserDialog('Make the edges correct.')
	wait_dialog.show()
	IJ.run("Remove Overlay");

if options is not None:
	for k in option_keywords:
		key_then_arg = k.split('=')
		if key_then_arg[0] == 'save_path':
			save_path = key_then_arg[1]
			IJ.run(image, "Bio-Formats Exporter", "save=" + save_path + " compression=Uncompressed");