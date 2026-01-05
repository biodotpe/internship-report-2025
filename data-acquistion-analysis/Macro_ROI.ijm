// -------- USER SETTINGS --------
dir_in  = "C:/Users/ppadi/OneDrive/Desktop/Internship/data/data-24h-21-aug/selected_tiffs/bf-equatorial/";
dir_out = "C:/Users/ppadi/OneDrive/Desktop/Internship/data/data-24h-21-aug/selected_tiffs/bf-equatorial-ROI/";
minArea_str = "350-Infinity"; // interpreted as µm^2 if image is calibrated in µm
circMin = 0.30;
circMax = 1.00;
// --------------------------------

requires("1.53");
File.makeDirectory(dir_out);
setOption("ScaleConversions", true);

// measurements to record
run("Set Measurements...", "area mean mode perimeter shape feret's redirect=None decimal=3");

list = getFileList(dir_in);
for (i = 0; i < list.length; i++) {
    name = list[i];
    if (!(endsWith(name, ".tif") || endsWith(name, ".tiff"))) continue;

    // clear any previous Results at the top of the loop
    if (isOpen("Results")) { selectWindow("Results"); run("Clear Results"); }
    if (isOpen("Summary")) { selectWindow("Summary"); run("Close"); }
    roiManager("Reset");

    path = dir_in + name;
    print("Processing: " + path);
    open(path);

    // processing
    run("8-bit");
    run("Bandpass Filter...", "filter_large=40 filter_small=3 suppress=None tolerance=5 autoscale");
    setAutoThreshold("Otsu dark no-reset");
    setOption("BlackBackground", true);
    run("Convert to Mask");
    run("Erode");
    run("Fill Holes");

    // analyze particles (Summary + Results will be generated)
    apCmd = "size=" + minArea_str + " circularity=" + circMin + "-" + circMax + " add exclude clear summarize display";
    run("Analyze Particles...", apCmd);

    // base name (no extension)
    dot = lastIndexOf(name, ".");
    if (dot < 0) dot = lengthOf(name);
    base = substring(name, 0, dot);

    // save ROI set (if any)
    count = roiManager("count");
    if (count > 0) {
        roi_out = dir_out + "ROI_" + base + ".zip";
        roiManager("Save", roi_out);
    }
    roiManager("Reset");

    // save Results table (per particle measurements)
    if (isOpen("Results")) {
        selectWindow("Results");
        if (nResults > 0) saveAs("Results", dir_out + base + "_results.csv");
        run("Close");
    }

    // save Summary table
    if (isOpen("Summary")) {
        selectWindow("Summary");
        saveAs("Text", dir_out + base + "_summary.csv");
        run("Close");
    }

    close(); // close current image
}

// final cleanup
roiManager("Reset");
run("Close All");
print("Batch finished.");