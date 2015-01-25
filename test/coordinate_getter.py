import ij
import ij.IJ as IJ

image = IJ.getImage()

print image.getRoi().getPolygon().xpoints
print image.getRoi().getPolygon().ypoints

# THIS EXPLAINS EVERYTHING! :(