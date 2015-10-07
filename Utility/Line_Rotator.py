from ij import IJ
from ij.gui import WaitForUserDialog

# Draw a line
dial = WaitForUserDialog('Draw a line that will be rotated to horizontal.')
dial.show()

cur_image = IJ.getImage()

cur_roi = cur_image.getRoi()
cur_angle =  cur_roi.getAngle()
print cur_angle

# Angles must be between 90 and -90 degrees...

angle_to_rotate = -cur_angle
IJ.run(cur_image, "Rotate... ", "angle=" +str(angle_to_rotate) + " grid=0 interpolation=Bicubic")