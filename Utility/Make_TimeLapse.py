from ij import IJ
from ij import WindowManager
from ij.process import ImageStatistics as IS
import os
import glob
import math

# This will work easier if you choose the images, have them all open.  Then 
# resize so they are at the same scale, and then create a montage. Assumes all
# images have the same pixel dimensions!

imageIDs = WindowManager.getIDList()

# Resize all images so that they are the same scale. Keep biggest at original scale,
# add black padding to smaller ones and then resize

maxArea = 0
maxWidth = 0
maxHeight = 0
for curID in imageIDs:
	curImage = WindowManager.getImage(curID)
	ip = curImage.getProcessor()
	curCalibration = curImage.getCalibration()
	stats = IS.getStatistics(ip, IS.AREA, curCalibration)
	currentArea = stats.area
	if currentArea > maxArea:
		maxArea = currentArea
		maxWidth = curImage.getWidth()
		maxHeight = curImage.getHeight()
		maxWidthScaled = maxWidth * curCalibration.pixelWidth
		maxHeightScaled = maxHeight * curCalibration.pixelHeight
		
		maxPixelWidth = curCalibration.pixelWidth
		maxPixelHeight = curCalibration.pixelHeight

# Now resize the images
print 'Resizing images...'
for curID in imageIDs:
	curImage = WindowManager.getImage(curID)
	ip = curImage.getProcessor()
	curCalibration = curImage.getCalibration()
	stats = IS.getStatistics(ip, IS.AREA, curCalibration)
	currentArea = stats.area
	# Resize the canvas so same area is occupied in total
	originalWidth = curImage.getWidth()
	originalHeight = curImage.getHeight()

	widthScaled = originalWidth * curCalibration.pixelWidth
	heightScaled = originalHeight * curCalibration.pixelHeight

	rescaleWidth = maxWidthScaled/widthScaled
	rescaleHeight = maxHeightScaled/heightScaled
	
	newWidth = int(originalWidth * rescaleWidth)
	newHeight = int(originalHeight * rescaleHeight)

	
	IJ.run(curImage, 'Canvas Size...', 'width=' + str(newWidth) + ' height=' + str(newHeight) + ' position=Center zero');
	# Now shrink down to the correct number of pixels, i.e. original, so we can
	# compare images directly by pixel.
	IJ.run(curImage, "Size...", "width=" + str(maxWidth) + " height=" + str(maxHeight)  +" depth=1 constrain average interpolation=Bicubic");
print 'Done resizing!'
print 'Making a montage...'
IJ.run("Images to Stack", "name=Montage title=[] use");
print 'Setting the scale on the montage...'
IJ.run("Set Scale...", "distance=1 known=" + str(maxPixelWidth) + " pixel=1 unit=mm");