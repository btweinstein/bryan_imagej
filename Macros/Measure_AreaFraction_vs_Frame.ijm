imageID = getImageID();
totalSlices = nSlices;

setBatchMode(true);
run("Set Measurements...", "stack area_fraction")

for (i=1; i <= totalSlices; i++)
{
	setSlice(i);
	run("Measure");
}
setBatchMode(false);