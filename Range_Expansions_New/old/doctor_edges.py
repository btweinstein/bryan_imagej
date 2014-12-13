import ij
from ij import IJ
import ij.plugin
import ij.gui


# Create a shortcut for the command "highlight_roi" to speed this up

# Split image into three; assumes you are inputting binary
image = IJ.getImage()
num_channels = image.getImageStackSize()

# Open the overlay image; there will be an option to pass in this value
overlay_image = IJ.openImage()
image.hide()
# Assumes that the last image is brightfield.

splitter = ij.plugin.ChannelSplitter()
overlay_list = splitter.split(overlay_image)
binary_list = splitter.split(image)
print len(binary_list)
image.close()
num_images = len(binary_list)

for i in range(num_images):
	cur_binary = binary_list[i]
	cur_binary.show()
	cur_overlay = overlay_list[i]
	cur_overlay.show()
	cur_overlay.setTitle('overlay_image')
	
	# Add the correct image to the overlay
	IJ.run(cur_binary, 'Add Image...', 'x=0 y=0 image=overlay_image opacity=90')
	cur_overlay.hide()
	wait_dialog = ij.gui.WaitForUserDialog('Make the edges correct.')
	wait_dialog.show()
	cur_binary.hide()

concat = ij.plugin.Concatenator()
doctored_image = concat.concatenate(binary_list, False)

doctored_image.show()