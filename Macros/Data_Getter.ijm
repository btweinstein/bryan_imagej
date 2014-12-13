macro "Data_Getter" {
	
	imageID = getImageID();
	totalSlices = nSlices;
	
	//You  must select what measurements you want before running this code!
	//Each particle will be analyzed.
	
	//Close ROI Manager
	if (isOpen("ROI Manager")) {
		selectWindow("ROI Manager");
		run("Close");
	}
	
	//Options for Particle Analysis: what is the minimum particle size
	//that we should look at?
	
	if(getArgument == "")
			minSize = getNumber("Enter minimum particle size to be counted:", 0);
		else
			minSize = parseFloat(getArgument);
	
	// Begin Hardcore Code:
	setBatchMode(true);
	
	// Deal with Width & Height
	width=getWidth(); 
	height=getHeight(); 
	
	for (i=1; i <=totalSlices; i++)
	{
		selectImage(imageID);
		setSlice(i);
		// I am not certain if the include holes thing is correct
		run("Analyze Particles...", "size="+minSize+"-infinity include circularity=0.00-1.00 show=Nothing add");
		if (roiManager("count") != 0){
			roiManager("Measure");
			roiManager("Delete");	
		}
	}
	setBatchMode(false);
	roiManager("Reset");
}