// All units in mm except when otherwise noticed

// ***** Variables to set *****
var minimumCancerRadius = 0.3;
var backgroundRadius = 30;
var medianSmoothing = 25;
var lineWidth = 10;
var closeNum = 5;

var batchUse = true;

// ***** Everything Else *****
var minimumCancerArea = PI * pow(minimumCancerRadius,2);
var main_id;
var path;
var plateIdentity;

/*
 * Run in hopes of program automatically getting the correct radius.
 * If not, when paused, measure it yourself.
 */
macro "Get_Elliptical_Radius" {    
	// Prepare to run. It only works if both are closed 
	// at the beginning -_-.
	closeAllWindows();
	
	run("Set Measurements...", "area fit shape limit display redirect=None decimal=3");

	//Deal with Directories
    	dir = getDirectory("Choose an Input Directory ");
    	out_dir = getDirectory("Choose an output Directory ");
    	list = getFileList(dir);

	// Don't run in batch mode so that the user can interactively decide
	// if the measurment is good
	// setBatchMode(true);
	
    	for (i=0; i<list.length; i++) {
        	path = dir+list[i];
        	//Get Plate Identity using shennanigans
        	findString = replace(list[i], "_[A-Z][0-9][0-9]_", "FOUND");
        	startIndex = indexOf(findString, "FOUND") + 1;
        	endIndex = startIndex + 3;
		plateIdentity = substring(list[i], startIndex, endIndex);
        	
        	showProgress(i, list.length);
        	if (!endsWith(path,"/")) {
        		setBatchMode(batchUse);
        		// Test whether to open using bioformats or if the file is a tiff
        		open_correctType(); 
        		main_id = getImageID();
        		find_tumor();
        		measure_radius();
        		save_results();
        	}
		// Reset everything for the next image since my batch
		// macro thing is not working right now...
		closeAllWindows();
	        closeAllImages();
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

function closeAllImages() {
	while (nImages>0) { 
		selectImage(nImages); 
		close(); 
	}
}

function find_tumor() {
	// Assumes picture scaling is mm and not um!
	run("Subtract Background...", "rolling=" + backgroundRadius + " sliding stack");
	run("Median...", "radius=" + medianSmoothing);
	run("Auto Threshold", "method=MaxEntropy white");
	// Set background to white so things are removed correctly
	setForegroundColor(255, 255, 255);
	remove_small();	
	run("Options...", "iterations=" + closeNum + " count=1 black edm=Overwrite do=Close");
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

function createOverlay() {
	// Assumes that the currently selected image is the thresholded one
	run("Analyze Particles...", "size="+minimumCancerArea+"-infinity circularity=0.00-1.00 show=Nothing add");
	open_correctType();
	current_id = getImageID();
	run("RGB Color");
	setForegroundColor(255, 201, 0);
	setBackgroundColor(0, 0, 0);
	run("Line Width...", "line=" + lineWidth);
	// roiManager("Draw");
	roiManager("Label");
}

function save_results() {
	// Save measurement output
	print(plateIdentity);
	saveAs("results", out_dir + plateIdentity + "_results.txt");
	// waitForUser("waiting");
	run("Select None");
	saveAs("tiff", out_dir + plateIdentity + "_outline.tif");
	//Open original file so we can display the overlay
	createOverlay();
	saveAs("tiff", out_dir + plateIdentity + "_overlay.tif");
}

function open_correctType() {
	fileType = substring(path, indexOf(path, '.'));
	if (fileType != '.zvi')
		open(path);
	else 
		run("Bio-Formats", "open=" + path + " autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");     			
}
