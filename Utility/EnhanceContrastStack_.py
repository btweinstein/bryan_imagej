'''Enhances the contrast of every image in the stack.'''

from ij import IJ

def run(image, options):
	originalSlice = image.getSlice()
	numSlices = image.getStackSize()
	for i in range(numSlices):
		image.setSliceWithoutUpdate(i + 1) # Indexed from 1
		IJ.run(image, "Enhance Contrast...", options) 
	image.setSlice(originalSlice)

saturationPercent = IJ.getNumber("Saturation Percentage:" , 0.4)
run(IJ.getImage(), 'saturated=' + str(saturationPercent))
