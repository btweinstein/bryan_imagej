var path;
var current_name;

macro "Resize_Plate_Pics" {
    	
    	dir = getDirectory("Choose an Input Directory ");
    	out_dir = getDirectory("Choose an output Directory ");
    	list = getFileList(dir);

	setBatchMode(true);
    	for (i=0; i<list.length; i++) {
    		currentName = list[i];
        	path = dir + currentName;        	
        	showProgress(i, list.length);        	
        	
        	if (!endsWith(path,"/")) {
        		// Test whether to open using bioformats or if the file is a tiff
        		open_correctType();
        		resize();
        		save_results();
        	}
    	}
}

function open_correctType() {
	fileType = substring(path, indexOf(path, '.'));
	if (fileType != '.zvi')
		open(path);
	else 
		run("Bio-Formats", "open=" + path + " autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");     			
}

function resize() {
	run("Scale...", "x=0.25 y=0.25 width=347 height=260 interpolation=Bicubic average create");
	run("8-bit");
}

function save_results() {
	saveAs("tiff", out_dir + currentName);
}