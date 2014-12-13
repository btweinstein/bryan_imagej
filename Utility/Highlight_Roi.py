import ij
from ij import IJ
import ij.plugin
import ij.gui
import ij.measure

from ij.plugin.filter import ParticleAnalyzer as PA

# Make the background black...I'm not sure why it doesn't do this automatically!
IJ.run("Options...", "iterations=1 black count=1")

options = PA.FOUR_CONNECTED + \
	PA.INCLUDE_HOLES + \
	PA.SHOW_OUTLINES
rt = ij.measure.ResultsTable()

analyzer = PA(options, PA.AREA, rt, 0, 10**9)
image = IJ.getImage()
analyzer.analyze(image)

#IJ.run("Analyze Particles...", "include add slice");