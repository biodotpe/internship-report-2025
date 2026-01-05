// ===== USER SETTINGS =====
dir_imgs = "C:/Users/ppadi/OneDrive/Desktop/Internship/data/data-24h-28-aug/selected_tiffs_1FOV/yf-equatorial/";
dir_rois = "C:/Users/ppadi/OneDrive/Desktop/Internship/data/data-24h-28-aug/selected_tiffs_1FOV/bf-equatorial-ROI/";
dir_out  = "C:/Users/ppadi/OneDrive/Desktop/Internship/data/data-24h-28-aug/selected_tiffs_1FOV/yf-equatorial-results-15px/";

bg_subtract_value = 15;   // set to 0 to disable or to 10 for the original config
roi_offset = -1;          // ROIs are 2 less than the fluorescence index
name_file = "ROI_single_bac.28Aug2025_20.33.33_"
// =========================

requires("1.53");
File.makeDirectory(dir_out);
setOption("ScaleConversions", true);

// Configure measurements
run("Set Measurements...", "area mean standard min center perimeter integrated median skewness kurtosis redirect=None decimal=3");

// Get fluorescence image list
listI = getFileList(dir_imgs);
for (i=0; i<listI.length; i++) {
    nameI = listI[i];
    if (!(endsWith(nameI, ".tif") || endsWith(nameI, ".tiff"))) continue;

    // Extract numeric part (last 6 digits before extension)
    dot = lastIndexOf(nameI, ".");
    num_str = substring(nameI, dot-6, dot);  // e.g. "000002"
    idx = parseInt(num_str);

    // Compute matching ROI index
    roi_idx = idx + roi_offset;
    roi_str = d2s(roi_idx,0);    // to string, no decimals
    while (lengthOf(roi_str)<6) roi_str = "0"+roi_str;  // zero-pad
    roi_name = name_file + roi_str + ".zip";

    // Skip if ROI file does not exist
    if (!File.exists(dir_rois + roi_name)) {
        print("Skipping " + nameI + " — no ROI " + roi_name);
        continue;
    }

    // Clear previous
    if (isOpen("Results")) { selectWindow("Results"); run("Clear Results"); }
    if (isOpen("Summary")) { selectWindow("Summary"); run("Close"); }
    roiManager("Reset");

    // Open fluorescence image
    pathI = dir_imgs + nameI;
    open(pathI);
    run("8-bit");
    if (bg_subtract_value > 0) run("Subtract...", "value=" + bg_subtract_value);

    // Load matching ROI
    run("ROI Manager...");
    roiManager("Open", dir_rois + roi_name);

    // Measure all ROIs
    nROIs = roiManager("count");
    for (r=0; r<nROIs; r++) {
        roiManager("Select", r);
        roiManager("Measure");
    }

    // Save Results table
    base = substring(nameI, 0, dot);
    if (isOpen("Results") && nResults > 0) {
        selectWindow("Results");
        saveAs("Results", dir_out + base + "_results.csv");
        run("Close");
    }

    // Cleanup
    roiManager("Reset");
    close(); // image
}
run("Close All");
print("Done!");
