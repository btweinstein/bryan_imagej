import ij
from ij.io import DirectoryChooser
from ij import IJ
from ij.gui import WaitForUserDialog
import glob
import os
from ij.gui import DialogListener
import ij.plugin.frame.ThresholdAdjuster
from loci.plugins import BF
from loci.plugins.in import ImporterOptions

def closeAllImages():
	count = ij.WindowManager.getImageCount()
	while count > 0: 
		image = ij.WindowManager.getImage(count)
		image.close()
		count -= 1

class Range_Expansions():

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
		self.command_to_folder['Edge Finder'] = self.edge_folder
		self.command_to_shortcut['Edge Finder'] = 'fe'
		
		self.circle_radius_folder = self.base_folder + 'circle_radius/'
		self.command_to_folder['Circle Finder'] = self.circle_radius_folder
		self.command_to_shortcut['Circle Finder'] = 'fc'

		self.edges_doctored_folder = self.base_folder + 'edges_doctored/'
		self.command_to_folder['Doctor Edges'] = self.edges_doctored_folder
		self.command_to_shortcut['Doctor Edges'] = 'de'

		self.mask_folder = self.base_folder + 'masks/'
		self.command_to_folder['Mask Finder'] = self.mask_folder
		self.command_to_shortcut['Mask Finder'] = 'mf'

		self.annihilation_folder = self.base_folder + 'annihilation_and_coalescence/'
		self.command_to_folder['Annihilation Finder'] = self.annihilation_folder
		self.command_to_shortcut['Annihilation Finder'] = 'af'
		
		# Reverse command_to_shortcut for utility
		self.shortcut_to_command = dict((v,k) for k,v in self.command_to_shortcut.iteritems())

		# Initialize the gui
		self.done_list = None # Responsible for keeping track of changes
		self.gui = self.create_gui()
		self.gui.showDialog()
		self.respond_to_changes()		

	def respond_to_changes(self):
		# Figure out what different things are ticked now
		checkboxes = self.gui.getCheckboxes()

		images_to_analyze = []
		commands_to_apply = []
		
		for current_box in checkboxes:
			label = current_box.label
			command = label[-2:]
			name = label[:-3]
			image_name = name.replace(' ', '_')

			cur_command = self.shortcut_to_command[command]
			current_state = current_box.state

			if current_state != self.done_list[image_name, cur_command]:
				images_to_analyze.append(image_name)
				commands_to_apply.append(cur_command)

		for image, command in zip(images_to_analyze, commands_to_apply):
			self.act_on_command(image, command)

	def act_on_command(self, image_path, command):
		file_path = '[' + self.tif_folder + image_path + ']'

		IJ.run("Bio-Formats", "open=" + file_path +" autoscale color_mode=Grayscale view=Hyperstack stack_order=XYCZT");
		
		if command == 'Edge Finder':
			command_folder = self.command_to_folder[command]
			IJ.run(command, 'save_path=' + command_folder + image_path)

		if command == 'Doctor Edges':
			options = 'save_path=' + command_folder + image_path
			options += ' overlay_path=' + self.tif_folder + image_path
			IJ.run(command, options)
		
		if command == 'Mask Finder':
			command_folder = self.command_to_folder[command]
			options = 'save_path=' + command_folder + image_path
			IJ.run(command, options)

		if command == 'Circle Finder':
			command_folder = self.command_to_folder[command]
			options = 'save_path=' + command_folder + image_path
			IJ.run(command, options)

		if command == 'Annihilation Finder':
			command_folder = self.command_to_folder[command]
			options = 'save_path=' + command_folder + image_path
			text_file_path =  command_folder + image_path.split('.')[0]			
			options += ' text_file_path=' + text_file_path
			IJ.run(command, options)

		current_image = IJ.getImage()
		current_image.changes=False
		closeAllImages()
		
	def create_gui(self):
		gui = ij.gui.GenericDialog('Range Expansion Code')

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

		self.done_list = {}
		for cur_image in self.image_list:
			for cur_command in commands:
				cur_folder = self.command_to_folder[cur_command]
				cur_folder_image_list = glob.glob(cur_folder + '*.tif')
				cur_folder_image_list = [os.path.basename(k) for k in cur_folder_image_list]
				if cur_image in cur_folder_image_list:
					self.done_list[cur_image, cur_command] = True
				else:
					self.done_list[cur_image, cur_command] = False
		
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
				defaultValues.append(self.done_list[cur_image, cur_command])
						
		num_rows = len(self.image_list) 
		num_columns = len(headings)
						
		gui.addCheckboxGroup(num_rows, num_columns, labels, defaultValues, headings)
				
		return gui
	
Range_Expansions()

# Previous attempts to use swing components & other threads were an utter disaster.
# Do things sequentially...or else things get way too annoying.
