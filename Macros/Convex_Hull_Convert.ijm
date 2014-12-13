macro "Convex_Hull_Convert" 
{
	imageID = getImageID();
	totalSlices = nSlices;
	
	if(getArgument == "")
		minSize = getNumber("Enter minimum particle size for Convex Hull:", 5);
	else
		minSize = parseFloat(getArgument);
	
	setBatchMode(true);
	 
	 //Assumes you have done pre-image cleaning up and such
	
	 // OPTIONS FOR PARTICLE ANALYSIS:
	
	// Begin Hardcore Code:
	
	width=getWidth(); 
	height=getHeight(); 
	
	for (i=1; i <= totalSlices; i++)
	{
		selectImage(imageID);
		setSlice(i);
		// I am not certain if the include holes thing is correct
		run("Analyze Particles...", "size="+minSize+"-infinity circularity=0.00-1.00 include show=Nothing add");
		ConvexHull();
	}
	
	function ConvexHull()
	 {  
	  count=roiManager("count");
	  for(i=0;i<count;i++)
	   {
	    roiManager("Select", 0);
	    run("Convex Hull");
	    roiManager("Add");
	    roiManager("Select", 0);
	    roiManager("Delete"); 
	   } 
	  roiManager("Select All");
	  roiManager("Fill");
	  roiManager("Delete");
	 }
	 
	setBatchMode(false);
}