macro "Remove_Large"
{
	// The eyedropper must be white/color of stuff that made 
	// it through the threshold!
	imageID = getImageID();
	totalSlices = nSlices;
	
	setBatchMode(true);
	
	 // OPTIONS FOR PARTICLE ANALYSIS:
	 
	if(getArgument == "")
		maxSize = getNumber("Enter max particle size to be removed:", 30);
	else
		maxSize = parseFloat(getArgument);
	// Begin Hardcore Code:
	
	if (isOpen("ROI Manager")) 
	{
		selectWindow("ROI Manager");
		run("Close");
	}
	
	width=getWidth(); 
	height=getHeight(); 
	for (i=1; i <= totalSlices; i++)
	{
		selectImage(imageID);
		setSlice(i);
		activeImage = getImageID();
		// I am not certain if the include holes thing is correct
		run("Analyze Particles...", "size="+maxSize+ "-Infinity circularity=0.00-1.00 include clear show=Nothing add");
		// Create a new image with these spots selected
	
		//Create an image containing the small particloes
		newImage("smallParticles", "8-bit Black", width, height, 1);
	  	roiManager("Fill");
	  	roiManager("reset");
	  	//Subtract it off
	  	imageCalculator("Subtract", activeImage,"smallParticles");
	
	  	//Close the image
	  	selectImage("smallParticles");
	  	close();
	}
	roiManager("reset");
}