from ij import IJ
import ij.gui
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
import os
import sys
import ij
import ij.Macro
from ij.process import ImageProcessor

IJ.run("Median...", "radius=10")
IJ.run("Sample Variance", "block_radius_x=5 block_radius_y=5")
IJ.run("Auto Threshold", "method=Triangle white")
dial = WaitForUserDialog('Clean up if necessary.')
dial.show()
IJ.run("Make Binary")
IJ.run("Fill Holes")

IJ.run("ParticleRemoverPy ", "enter=3");
dial = WaitForUserDialog('Clean up if necessary.')
dial.show()
# If we run this again it often flips black & white, likely because it doesn't know what
# the background is
# IJ.run("Make Binary") 

# Done! Now do whatever you have to do.
