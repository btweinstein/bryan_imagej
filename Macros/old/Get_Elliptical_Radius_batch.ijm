// All units in mm except when otherwise noticed

// ***** Variables to set *****
var minimumCancerRadius = 0.25;

// ***** Everything Else *****
var minimumCancerArea = PI * pow(minimumCancerRadius,2);

macro "Get_Elliptical_Radius" {    
	run("Clear Results");
	run("Set Measurements...", "area fit shape limit display redirect=None decimal=3");

        find_tumor();
        measure_radius();
	saveAs("results");
}

function find_tumor() {
	// Assumes picture scaling is mm and not um!
	run("Enhance Contrast...", "saturated=0.4 normalize equalize");
	run("Find Edges");
	run("Auto Threshold", "method=Default white");
	// Set background to black so things are removed correctly
	setForegroundColor(0, 0, 0);
	run("Particle Remover", "size=0-" + minimumCancerArea + " circularity=0.00-1.00 show=Nothing");
	run("Select None");
	roiManager("Deselect");
	//run("Make Binary"); // My remove small macro should likely be changed so that the output is binary
	run("Options...", "iterations=5 count=1 black edm=Overwrite do=Close");
	run("Fill Holes");
}

function measure_radius() {
	run("Analyze Particles...", "size="+minimumCancerArea+"-infinity circularity=0.00-1.00 show=Nothing add");
	roiManager("Measure");
	roiManager("Delete");
}