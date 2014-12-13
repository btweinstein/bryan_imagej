import ij.*;
import ij.process.*;
import ij.gui.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.plugin.filter.*;
import ij.measure.*;
import ij.io.*;

import java.io.IOException;
import loci.formats.FormatException;
import loci.plugins.BF;

import java.awt.*;
import java.lang.Math;
import java.util.regex.*;
import java.io.File;
import java.io.IOException;


/**
 * All units are in mm except when otherwise noted.
 */
public class Get_Elliptical_Area implements PlugIn {

	//***** Variables to Set *******
	private double minimumCancerRadius = 0.3;
	private double backgroundRadius = 30;
	private double medianRadius = 5;
	private double lineWidth = 10;
	private double closeNum = 5;

	private String queryDirectory = "/tmp/queried_images";
	
	//***** Everything Else ********
	private double minimumCancerArea = Math.PI * Math.pow(minimumCancerRadius, 2);

	private ResultsTable results = new ResultsTable();
	private Analyzer analyzer;

	private int fileCounter = 0;
	
	public void run(String arg) {
		//***** Set Correct Measurements ******
		initialize_Analyzer();
		
		//***** Get Input and Output Directories *****
		
		// Iterate over all Input Images
		File folder = new File(queryDirectory);
		File[] listOfFiles = folder.listFiles();
		for (int i = 0; i < listOfFiles.length; i++) {
			File current_file = listOfFiles[i];
			IJ.showProgress(i, listOfFiles.length);
			if (current_file.isFile()) {
				try {					
					//*****Open the File*****
					ImagePlus images[] = BF.openImagePlus(current_file.getPath());
					ImagePlus originalImage = images[0];
					
					//Resize the image
					String resizeTitle = "scaledImage.tiff";
					IJ.run(originalImage, "Scale...", "x=0.25 y=0.25 width=347 height=260 interpolation=Bicubic average process create title=" + resizeTitle);
					originalImage = WindowManager.getImage(resizeTitle);
					//Make 8-bit
					IJ.run(originalImage, "8-bit", "");
					
					//originalImage.show();
					
					ImagePlus thresholdedImage = originalImage.duplicate();
					thresholdedImage.show();
					findTumor(thresholdedImage);
					measureTumor(thresholdedImage);
					// Create an overlay
					ImagePlus overlayImage = createOverlay(originalImage, thresholdedImage);
					
					saveResults();
					
				}
				catch (FormatException exc) {
					IJ.error("Potato: " + exc.getMessage());
				}
				catch (IOException exc) {
					IJ.error("POTATO: " + exc.getMessage());
				}
			}
		}
	}

	public String getPlateIdentity(String fileName) {
		// Get Plate identity
		Pattern pattern = Pattern.compile("_[A-Z][0-9][0-9]_");
		Matcher matcher = pattern.matcher(fileName);
		matcher.find();
		String name = matcher.group();
		name = name.substring(1, 4);
		return name;
	}
	
	private void initialize_Analyzer() {
		analyzer = new Analyzer();
		analyzer.setResultsTable(results);
		analyzer.setMeasurement(analyzer.AREA, true);
		analyzer.setMeasurement(analyzer.MEAN, true);
		analyzer.setMeasurement(analyzer.CIRCULARITY, true);
		analyzer.setMeasurement(analyzer.ELLIPSE, true);
		analyzer.setMeasurement(analyzer.SHAPE_DESCRIPTORS, true);
		analyzer.setMeasurement(analyzer.LABELS, true);
		analyzer.setMeasurement(analyzer.KURTOSIS, true);
		analyzer.setPrecision(3);
	}
	/**
	 * Responsible for finding the tumor in the image passed in. Works on stacks.
	 */
	public void findTumor(ImagePlus image){
		// Determine if the tumor is black on a white background or white on a black background
		// based on the mean gray value
		ImageStatistics stats = image.getStatistics(Measurements.MEAN);
		IJ.log(Double.toString(stats.mean));
		
		IJ.run(image, "Subtract Background...", "rolling=" + String.valueOf(backgroundRadius) + " sliding stack");
		IJ.run(image, "Auto Threshold", "method=MaxEntropy white");
		// Set background to white so things are removed correctly
		IJ.setForegroundColor(0, 0, 0);
		IJ.run(image, "Particle Remover edited", "size=0-" + String.valueOf(minimumCancerArea)  
			+ " circularity=0.00-1.00 show=Nothing include");
		IJ.run(image, "Options...", "iterations=" + String.valueOf(closeNum) + " count=1 black edm=Overwrite do=Close");
		IJ.runPlugIn(image, "Binary", "Fill Holes");
		IJ.runPlugIn(image, "Binary", "Watershed");
		IJ.run(image, "Particle Remover edited", "size=0-" + String.valueOf(minimumCancerArea)  
			+ " circularity=0.00-1.00 show=Nothing include");
	}
	
	public void measureTumor(ImagePlus image) {
		IJ.run(image, "Analyze Particles...", "size=0-Infinity circularity=0.00-1.00 show=Nothing display include");
	}

	public ImagePlus createOverlay(ImagePlus original, ImagePlus thresholded) {
		ImagePlus overlayImage = original.duplicate();
		//Locate the particles
		IJ.run(thresholded, "Analyze Particles...", "size=0-Infinity circularity=0.00-1.00 show=Nothing add");
		//Prepare Image
		IJ.runPlugIn(overlayImage, "Converter", "RGB Color");
		IJ.setForegroundColor(255, 201, 0);
		IJ.setBackgroundColor(0, 0, 0);
		IJ.run("Line Width...", "line=" + lineWidth);
		IJ.runPlugIn("roiManager", "Label");
		
		return overlayImage;
	}
	
	public void saveResults() {
		
	}
}
