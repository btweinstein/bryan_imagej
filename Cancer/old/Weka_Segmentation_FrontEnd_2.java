import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import java.io.File;
import trainableSegmentation.*;
import java.util.ArrayList;

/**
 * Assumes you have a weka model set up already with at least one image trained.
 * I can't seem to initialize it properly otherwise -_-
 */
public class Weka_Segmentation_FrontEnd_2 implements PlugIn {
	
	// ****** Folder Structure *******
	static String topLevel = "C:/Users/chompy_local/Documents/Cluzel_Pictures/Weka_Classification";
	static String modelPath = topLevel + "/classifier.model";
	static String dataPath = topLevel+ "/data.arff";
	static String training_directory = topLevel + "/training";
	static String trained_directory = topLevel + "/trained";

	// ***** Internal Variables ******
	private WekaSegmentation wekaTrainer;
	
	public void run(String arg) {
		// Create Dialog
		GenericDialog dialog = new GenericDialog("Choices");
		dialog.addMessage("What do you want to do?");
		String choices[] = {"Train", "Chill"};
		dialog.addChoice("Choices", choices, "Train");
		dialog.showDialog();

		// Get what the user wants to do
		String choice = dialog.getNextChoice();
		if (choice.equals("Train")){
			train();
			moveTrainingPictures();
		}
		else {
			IJ.log("Done!");
		}
	}

	/**
	 *  The weka trainer works best if you instantiate it with an image...
	 *  do that or else bizarre things happen.
	 */
	public void train() {
		wekaTrainer = new WekaSegmentation();
		
		// Iterate over all training images
		File folder = new File(training_directory);
		File[] listOfFiles = folder.listFiles();
		int numFilesToTrain = 0;
		for (int i = 0; i < listOfFiles.length; i++) {
			File file = listOfFiles[i];
			if (file.isFile())
			{
				String fileName = file.getName();
				// If the file does not have binary in its name,
				// load the picture and the matching binary one!
				if (!fileName.contains("binary") &&
				     (fileName.contains("zvi") ||
				     fileName.contains("tif"))
				     ){
				     	// Open file and its binary counterpart
					ImagePlus original = IJ.openImage(file.getPath());

					// If it's the first iteration, instantiate the segmentor
					if (i == 0) {
						initialize_weka(original);
					}
					
					int periodIndex = fileName.indexOf('.');
					String binaryName = fileName.substring(0, periodIndex);
					binaryName += "_binary.tif"; 

					String binaryPath = training_directory + "/" + binaryName;
					File binaryFile = new File(binaryPath);
					if ( binaryFile.exists() ) {
						ImagePlus binary = IJ.openImage(binaryPath);
						// Add to the WEKA segmenter
						wekaTrainer.setTrainingImage(original);
						wekaTrainer.addBinaryData(original, binary, "Tumor", "Not a Tumor");
						numFilesToTrain++;
					}
					else {
						IJ.error("Could not open binary file " + binaryName);
					}
				}
			}
		}
		if (numFilesToTrain > 0) {
			wekaTrainer.trainClassifier();
			// Save Results
			wekaTrainer.saveClassifier(modelPath);
			wekaTrainer.saveData(dataPath);
		}
		else IJ.error("No Images were input to train with!");

		
	}

	public void moveTrainingPictures() {
		File folder = new File(training_directory);
		File[] listOfFiles = folder.listFiles();
		for (int i = 0; i < listOfFiles.length; i++) {
			File file = listOfFiles[i];
			File newFile = new File(trained_directory + "/" + file.getName());
			if ( !file.renameTo(newFile) ) {
				IJ.log("File " + file.getName() + " could not be moved!");
			}
		}
	}

	public void initialize_weka(ImagePlus image) {
		wekaTrainer.setTrainingImage(image);
		// Load classifier if it already exists
		File wekaPath = new File(modelPath);
		if ( wekaPath.exists() ) {
			wekaTrainer.loadClassifier(modelPath);
		}
		else IJ.error("I could not find an existing classifier...");
		
		File dataFile = new File(dataPath);
		if ( dataFile.exists() ) {
			wekaTrainer.loadTrainingData(dataPath);
		}
		else IJ.error("I could not find any existing classification data...");
	}
}
