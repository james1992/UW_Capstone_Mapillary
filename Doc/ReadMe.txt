Tool: Mapillary to ESRI (GeoJSON to Shapefile)
Date Created: 2017-07-27
Authors: Jay Dahlstrom, Christian Matthews, Tommy Nguyen
Contact: jaydahlstrom92@gmail.com, cmatthews@tutamail.com, tnguyen@tutamail.com
Purpose: This tool was created for the University of Washington GIS Workshop course as a partnership between Mapillary and graduate students.
Instructions: This tool takes a Mapillary GeoJSON file and an object class key (e.g. construction--flat--bike-lane) and converts the GeoJSON data
	      into an ESRI Shapefile for use in future analysis.  This tool should be run first to prep the data for analysis in the next two scripts.
Outputs: An ESRI Shapefile with fields for the unique photo key that is assigned by Mapillary and a user named field that contains the segmentation data
	 for the object class.  In addition, you will define the output spatial reference.

Tool: Priority Ranking and Heat Map Generation (Analyze Mapillary Photos)
Date Created: 2017-07-30
Authors: Jay Dahlstrom, Christian Matthews, Tommy Nguyen
Contact: jaydahlstrom92@gmail.com, cmatthews@tutamail.com, tnguyen@tutamail.com
Purpose: This tool was created for the University of Washington GIS Workshop course as a partnership between Mapillary and graduate students.
Instructions: Using ArcGIS Desktop, open a new MXD and add the three necessary layers (boundary, input Mapillary features, input known features),
	      the open the tool script and load the required layers.
Outputs: (1) Heat map of the input data (Mapillary's photos). This heat map represents a density of the photos taken 	
	 (2) A priority ranked grid. This grid represents areas where Mapillary users should target when targetting specific features.
	     This ranking is a MCE of the number of current photos for a specific feature and the area where possible photos of these
	     features can be taken.
Recommended Symbolization: 
	(1) Heat map
		Symbology = Classified
		Classification = 8 Classes (Natural Breaks (Jenks)), change the first Break Value to 0
		Color Ramp = Cold to Hot Diverging, change the 0 value to "No Color"
	(2) Priority Ranking Grid
		Symbology = Quantities\Graduated colors
		Classification = 7 Classes (Natural Breaks (Jenks))
		Color Ramp = Cold to Hot Diverging

Tool: Image to Object Distance Calculation (Calculate Distance)
Date Created: 2017-08-5
Authors: Jay Dahlstrom, Christian Matthews, Tommy Nguyen
Contact: jaydahlstrom92@gmail.com, cmatthews@tutamail.com, tnguyen@tutamail.com
Purpose: This tool was created for the University of Washington GIS Workshop course as a partnership between Mapillary and graduate students.
Instructions: This tool takes a feature class that was created from a Mapillary GeoJSON file for a particular object class and compares the photo locations
	      to the location of points in a known dataset for the same object class.  The distance between each photo and the closest known object is returned.
	      If the known object class consists of points the script will convert the lines to points at a user define interval along each line segment (the
	      distance value uses the unit of measure of the spatial reference).  The script will also set the spatial reference to that of the Mapillary feature 
	      class to ensure that both use the same units.
Outputs: An updated feature class with a distance field that includes the distance to the closest known object (straight line distance) in the units of the
         spatial reference in use.  This information can then be used along with the semantic segmentation for the object class to identify potential false positives.

Tool: Data to ArcGIS Online (Publish Service)
Date Created: 2017-07-14
Authors: Jay Dahlstrom, Christian Matthews, Tommy Nguyen
Contact: jaydahlstrom92@gmail.com, cmatthews@tutamail.com, tnguyen@tutamail.com
Purpose: This tool was created for the University of Washington GIS Workshop course as a partnership between Mapillary and graduate students.
Instructions: This tool converts the contents of an Existing MXD file into a hosted feature service in ArcGIS Online.  To use this script you will need to open 
	      ArcMap and sign into your ArcGIS Online Organizational Account (File > Sign In) before you run the script.
Outputs: A hosted feature service that contains layers for all of the contents of the MXD with the symbology that was set in the MXD.


