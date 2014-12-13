// This macro batch measures a folder of images.
// Use the Analyze>Set Measurements command
// to specify the measurement parameters. Check 
// "Display Label" in the Set Measurements dialog
// and the file names will be added to the first 
// column of the "Results" table.

macro "Batch Measure" 
{    
    run("Clear Results");
    
    //Deal with Directories
    dir = getDirectory("Choose an Input Directory ");
    list = getFileList(dir);
    
    if (getVersion>="1.40e")
        setOption("display labels", true);
    
    //Determine whether you are measuring particles or whole quantities

    //Number of frames to skip (spacing)

    frameSpacing = getNumber("Spacing between frames:", 100);
    measureParticles = getBoolean("Measure Particles?");
    
    if (measureParticles){
    	minSize = getNumber("Minimum particle size to measure:" , 0);
    }
    setBatchMode(true);

    //Number of frames that have to actually be dealt with
    framesToProcess = floor(list.length/frameSpacing);
    
    for (i=0; i<framesToProcess; i++) {
    	//We want to take a frame every frameSpacing
        path = dir+list[frameSpacing*i];
        showProgress(i, framesToProcess);
        if (!endsWith(path,"/"))
        { 
        	open(path);
        }	
        if (nImages>=1) {
        	if (!measureParticles)
        	{        	
            		run("Measure");
            		close();
        	}
    		else
    		{
    			run("Analyze Particles...", "size="+minSize+"-infinity include circularity=0.00-1.00 show=Nothing add");
			roiManager("Measure");
			roiManager("reset");
			close();
    		}
        }
    }
    setBatchMode(false);
    saveAs("Measurements","");
}