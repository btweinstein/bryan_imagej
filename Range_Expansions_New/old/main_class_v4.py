from ij.io import DirectoryChooser
import ij
from ij import IJ
from ij.gui import WaitForUserDialog
import glob
import os
from ij.gui import DialogListener
from java.awt.event import ItemEvent
import java.awt
import ij.plugin.frame.ThresholdAdjuster
from threading import Thread

class Range_Expansions(DialogListener):

	def __init__(self):
		# The input folder should be the TIF folder
		self.base_folder = DirectoryChooser('Set input directory.').getDirectory()
		self.tif_folder = self.base_folder + 'tif/'
		self.image_list = glob.glob(self.tif_folder + '*.tif')
		self.image_list = [os.path.basename(k) for k in self.image_list]

		self.image_list.sort()
		
		# Create a map of link between folder and command
		self.command_to_folder = {}
		self.command_to_shortcut = {}
		
		self.edge_folder = self.base_folder + 'edges/'
		self.command_to_folder['Find Edges'] = self.edge_folder
		self.command_to_shortcut['Find Edges'] = 'fe'
		
		self.circle_radius_folder = self.base_folder + 'circle_radius/'
		self.command_to_folder['Find Circle'] = self.circle_radius_folder
		self.command_to_shortcut['Find Circle'] = 'fc'

		# Reverse command_to_shortcut for utility
		self.shortcut_to_command = dict((v,k) for k,v in self.command_to_shortcut.iteritems())
		
		# Create a GUI with available options
		self.gui = self.create_gui()
		self.gui.showDialog()

	def dialogItemChanged(self, dialog, event):
		'''The purpose of this is to determine which command to run on which image.
		We MUST run the commands in a different thread, however, or else disaster will strike.'''
		# We need to get the heading & label of the checkbox; that's it!
		if (event is not None) and event.stateChange == ItemEvent.SELECTED:
			item_name = event.item
			item_shortcut = item_name[-2:]
			command_to_run = self.shortcut_to_command[item_shortcut]
			
			image_name = item_name[:-3]
			# Annoyingly, all underscores are removed. So add them back in...
			image_name = image_name.replace(' ', '_')

			# Make sure the modality settings are correct...or else everything will crash
			
			# Open the image

			# Run the appropriate command on it
			# If we want the program to work in this way, we need to run this piece in a new thread...
			# or else user input won't work and everything will explode. So is it worth it?
			if command_to_run == 'Find Edges':
				Find_Edges(image_name).execute()

		
	def create_gui(self):
		gui = ij.gui.NonBlockingGenericDialog('Range Expansion Code')

		gui.setModal(False)
		gui.setModalityType(java.awt.Dialog.ModalityType.MODELESS)

		# Create a list of where each image has been processed: show graphically
		# Then click on which test you want to apply to each image
		#command_keys = self.command_to_folder.keys()
		# Number of rows = number of keys
		#num_rows = len(command_keys)
		#gui.addRadioButtonGroup('Commands', command_keys, num_rows, 1, command_keys[0])

		# Make a list of which commands have been applied to which image. Do this via checkboxes.

		commands = self.command_to_folder.keys()
		folders = self.command_to_folder.values()
		
		num_commands = len(self.command_to_folder)
		num_images = len(self.image_list)

		done_list = {}
		for cur_image in self.image_list:
			for cur_command in commands:
				cur_folder = self.command_to_folder[cur_command]
				cur_folder_image_list = glob.glob(cur_folder + '*.tif')
				cur_folder_image_list = [os.path.basename(k) for k in cur_folder_image_list]
				if cur_image in cur_folder_image_list:
					done_list[cur_image, cur_command] = True
				else:
					done_list[cur_image, cur_command] = False
		
		# Take the list of what has been done and turn it into a checkbox group
		labels = []
		headings = commands
		defaultValues = []

		for cur_image in self.image_list:
			for cur_command in commands:
				# Put a specific label on every checkbox to make understanding which
				# command to do easy
				cur_label = cur_image + '_' + self.command_to_shortcut[cur_command]
				labels.append(cur_label)
				defaultValues.append(done_list[cur_image, cur_command])
						
		num_rows = len(self.image_list) 
		num_columns = len(headings)
						
		gui.addCheckboxGroup(num_rows, num_columns, labels, defaultValues, headings)

		# Add the dialog listener
		gui.addDialogListener(self)
		
		return gui
	
class  Find_Edges(SwingWorker):

	def __init__(self, image_name):
		self.image_name = image_name
		SwingWorker.__init__(self)
	
	def process(self):
	
		image = IJ.openImage(self.tif_folder + image_name)
		image.show()
	
		stack = image.getStack()
		stack.deleteLastSlice()
		
		# Cycle through each image
		for i in range(1, stack.getSize() + 1):
			ip = stack.getProcessor(i)
			ip.blurGaussian(2)
			ip.findEdges()
		
		image.updateAndDraw()
		# Now cycle through and apply a threshold to each
		
		# Convert to 8-bit, regretably. Not sure if I have to do this.
		IJ.run(image, "8-bit", "")
		
		# Annoyingly, we will have to binarize each slice individually, as ImageJ
		# does not like to do it all at once
		adjuster = ij.plugin.frame.ThresholdAdjuster()
		IJ.resetMinAndMax()
		WaitForUserDialog('potato').show()
	
	def done(self):
		try:
			self.get()  #raise exception if abnormal completion
		except ExecutionException, e:
	       		raise SystemExit, e.getCause()

Range_Expansions()

# This is far too annoying...