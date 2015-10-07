from ij import IJ
from ij.gui import WaitForUserDialog

# Draw a line
dial = WaitForUserDialog('Draw a line that will be rotated to horizontal.')
dial.show()

cur_image = IJ.getImage()

cur_roi = cur_image.getRoi()
cur_angle =  cur_roi.getAngle()
print cur_angle

# Angles must be between 90 and -90 degrees...currently are not but it's fine as my
# system has inversion symmetry along the y-axis

IJ.run(cur_image, "Rotate... ", "angle=" +str(cur_angle) + " grid=0 interpolation=Bicubic")