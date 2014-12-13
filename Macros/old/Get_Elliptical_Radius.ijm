// All units in mm except when otherwise noticed

// ***** Variables to set *****
var minimumCancerRadius = 0.25;

// ***** Everything Else *****
var minimumCancerArea = PI * pow(minimumCancerRadius,2);
var imageCount = 1;
var main_id;

macro "Get_Elliptical_Radius" {    
	// Prepare to run. It only works if both are closed 
	// at the beginning -_-.
	closeAllWindows();
	
	run("Set Measurements...", "area fit shape limit display redirect=None decimal=3");

	//Deal with Directories
    	dir = getDirectory("Choose an Input Directory ");
    	out_dir = getDirectory("Choose an output Directory ");
    	list = getFileList(dir);

	setBatchMode(true);
	
    	for (i=0; i<list.length; i++) {
        	path = dir+list[i];
        	showProgress(i, list.length);
        	if (!endsWith(path,"/")) {
        		run("Bio-Formats", "open=" + path + " autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");
        		//Rename the image so that things are consistent
        		rename_success = File.rename(path, dir + imageCount + ".zvi");
        		if (rename_success != 1)
        			print("I couldn't rename the input file...I wonder why?");
        		main_id = getImageID();
        		find_tumor();
        		measure_radius();
        		//waitForUser("test");
        		save_results();
        		imageCount++;
        	}
		// Reset everything for the next image since my batch
		// macro thing is not working right now...
		closeAllWindows();
	        while (nImages>0) { 
			selectImage(nImages); 
  			close(); 
		}
    	}
}

function closeAllWindows() {
  	if (isOpen("ROI Manager")) {
  		selectWindow("ROI Manager");
     		run("Close");
  	}
  	if (isOpen("Results")) {
  		selectWindow("Results");
     		run("Close");
  	}
}

function find_tumor() {
	// Assumes picture scaling is mm and not um!
	run("Enhance Contrast...", "saturated=0.4 normalize equalize");
	run("Find Edges");
	run("Auto Threshold", "method=Default white");
	// Set background to white so things are removed correctly
	setForegroundColor(255, 255, 255);
	remove_small();	
	run("Options...", "iterations=5 count=1 black edm=Overwrite do=Close");
	run("Fill Holes");
}

function remove_small() {
	// Parameters necessary to create the new picture
	width=getWidth(); 
	height=getHeight(); 
	// I am not certain if the include holes thing is correct
	run("Analyze Particles...", "size=0-"+minimumCancerArea+" circularity=0.00-1.00 include clear show=Nothing add");

	//Create an image containing the small particloes
	newImage("smallParticles", "8-bit Black", width, height, 1);
  	roiManager("Fill");
  	roiManager("reset");
  	//Subtract it off
  	imageCalculator("Subtract", main_id,"smallParticles");

  	//Close the image
  	selectImage("smallParticles");
  	close();
}

function measure_radius() {
	run("Analyze Particles...", "size="+minimumCancerArea+"-infinity circularity=0.00-1.00 show=Nothing add");
	roiManager("Measure");
	roiManager("reset");
}

function save_results() {
	// Save measurement output
	saveAs("results", out_dir + imageCount + "_results.txt");
	// waitForUser("waiting");
	run("Select None");
	saveAs("tiff", out_dir + imageCount + "_outline.tif");
	//Open original file so we can display the overlay
	run("Analyze Particles...", "size="+minimumCancerArea+"-infinity circularity=0.00-1.00 show=Nothing add");
	run("Bio-Formats", "open=" + dir + imageCount + ".zvi" + " autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");
	run("RGB Color");
	setForegroundColor(255, 201, 0);
	setBackgroundColor(0, 0, 0);
	run("Line Width...", "line=10");
	// roiManager("Draw");
	roiManager("Label");
	saveAs("tiff", out_dir + imageCount + "_overlay.tif");
}
