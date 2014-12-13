from ij import IJ
import sys
import os
from java.lang.System import getProperty
# Add the path of all of my scripts
fijiDir = getProperty("fiji.dir")
myPluginsTop = os.path.join(fijiDir, 'plugins');
myPluginsTop = os.path.join(myPluginsTop, 'Bryan');
walker = os.walk(myPluginsTop)
for root, dirs, files in os.walk(myPluginsTop, topdown=False):
	for name in dirs:
		sys.path.append(os.path.join(root, name))

# Continue importing 
import EnhanceContrastStack_ as enhanceContrastStack

###### Begin Main Function ####

image = IJ.getImage()

# Information we need: the sectors, i.e. where things are fluorescing.

# STEP 1: Remove unwanted features
IJ.run(image, "Subtract Background...", "rolling=300 sliding stack");
# STEP 2: Make features you want stand out
# The way to do this appears to be enhancing the local contrast!
IJ.run(image, "Enhance Local Contrast (CLAHE)", "blocksize=20 histogram=256 maximum=5 mask=*None*");
# STEP 3: Based on features you have identified, smooth out noise
IJ.run(image, "Subtract Background...", "rolling=300 sliding stack");
IJ.run(image, "Median...", "radius=5 stack");
# Step 4: Convert to 8-bit
#IJ.run(image, "8-bit");

# This does a decent job, but I think I can use edge detection somehow.
# Let's later take a look at what Melanie and Korelov did. They may have
# some useful tricks.