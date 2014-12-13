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
public class Get_Elliptical_Radius2 implements PlugIn {

	//***** Variables to Set *******
	private double minimumCancerRadius = 0.3;
	private double backgroundRadius = 30;
	private double medianRadius = 25;
	private double lineWidth = 10;
	private double closeNum = 5;

	//***** Everything Else ********
	private double minimumCancerArea = Math.PI * Math.pow(minimumCancerRadius, 2);
	private String inputDirectory;
	private String outputDirectory;

	private ResultsTable results = new ResultsTable();
	private Analyzer analyzer;

	private String current_plate;
	private String current_file;

	private int fileCounter = 0;
	
	public void run(String arg) {
		//***** Set Correct Measurements ******
		initialize_Analyzer();
		
		//***** Get Input and Output Directories *****
		inputDirectory = IJ.getDirectory("Input");
		outputDirectory = IJ.getDirectory("Output");
		
		// Iterate over all Input Images
		File folder = new File(inputDirectory);
		File[] listOfFiles = folder.listFiles();
		for (int i = 0; i < listOfFiles.length; i++) {
			File current_file = listOfFiles[i];
			IJ.showProgress(i, listOfFiles.length);
			if (current_file.isFile()) {
				try {
					String fileName = current_file.getName();
					String path = current_file.getPath();

					//*****Get the Plate Identity******
					current_plate = getPlateIdentity(fileName);				
					
					//*****Open the File*****
					ImagePlus images[] = BF.openImagePlus(current_file.getPath());
					//Add more stuff here later to deal with multiple images...
					ImagePlus originalImage = images[0];
					ImagePlus thresholdedImage = originalImage.duplicate();
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
		analyzer.setMeasurement(analyzer.CIRCULARITY, true);
		analyzer.setMeasurement(analyzer.ELLIPSE, true);
		analyzer.setMeasurement(analyzer.SHAPE_DESCRIPTORS, true);
		analyzer.setMeasurement(analyzer.LABELS, true);
		analyzer.setPrecision(3);
	}
	public void findTumor(ImagePlus image){
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
