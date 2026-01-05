# 2025 Internship Report - Integration and Validation of Modular Open-Source Platform for Droplet Microfluidics

This repository contains the code, data, and documentation from the internship project focused on integration of modular open-source components ([strobe-enhanced microscopy stage](https://wenzel-lab.github.io/strobe-enhanced-microscopy-stage/) and [3D-printed syringe pumps](https://wenzel-lab.github.io/syringe-pumps-and-controller/)) within the context of droplet microfluidics and single-cell analysis.

The project includes tools for instrument control, data acquisition, image processing, and analysis of microscopy data, particularly for studying cellular behavior in microenvironments, with a focus on fluorescence imaging and quantitative analysis.

## Repository Structure

### 1. notebooks-api/
Contains Jupyter notebooks and Python APIs for microscope and syringe pump control:
- [UI-integrated.ipynb](/notebooks-api/UI-integrated.ipynb): Integrated user interface notebook
- [strobe-microscope-ui.ipynb](/notebooks-api/strobe-microscope-ui.ipynb): Microscope control interface
- [syringe-pump-ui.ipynb](/notebooks-api/syringe-pump-ui.ipynb): Syringe pump control interface
- [microscope_api.py](/notebooks-api/microscope_api.py): Python API for microscope control
- [syringe_pump_api.py](/notebooks-api/syringe_pump_api.py): Python API for syringe pump control

### 2. data-acquisition-analysis/
Includes files related to microscope data acquisition and analysis:
- Configuration files: [BF-YF-1offset-20FOVs.xml](/data-acquisition-analysis/BF-YF-1offset-20FOVs.xml), [BF-YF-1offset-5FOVs.xml](/data-acquisition-analysis/BF-YF-1offset-5FOVs.xml)
- ImageJ macros: [Macro_ROI.ijm](/data-acquisition-analysis/Macro_ROI.ijm), [Macro_YF_analysis.ijm](/data-acquisition-analysis/Macro_YF_analysis.ijm)
- Documentation: [pipeline.jpg](/data-acquisition-analysis/pipeline.jpg), [scale_epi_temika.jpg](/data-acquisition-analysis/scale_epi_temika.jpg)

### 3. YFP-results/
Contains analysis results and visualization scripts for YFP (Yellow Fluorescent Protein) data:
- Example images: [25-um-example.png](/YFP-results/25-um-example.png), [30-um-example.png](/YFP-results/30-um-example.png)
- Intensity data: [intensity_25um.csv](/YFP-results/intensity_25um.csv), [intensity_30um.csv](/YFP-results/intensity_30um.csv)
- Visualization: [intensity_plot.png](/YFP-results/intensity_plot.png), [intensity_plot_hours.png](/YFP-results/intensity_plot_hours.png)
- Analysis script: [plot-intensity.py](/YFP-results/plot-intensity.py)

## Setup and Usage

### Prerequisites
- Python 3.x
- Jupyter Notebook
- Required Python packages (install via `pip install -r requirements.txt`)

### Installation
1. Clone this repository
2. Install required dependencies
3. Launch Jupyter Notebook to access the interactive notebooks

## Usage

1. For instrument control:
   - For the microscopy stage, stop the pi_webapp process first (if running) and run the [microscope API](notebooks-api/microscope_api.py).
   - Use the notebooks in the [notebooks-api/](notebooks-api/) directory.
   - Configure the IP address for the microscope controller in the notebook before starting. Use 0.0.0.0 if you are using the stand-alone configuration and a specific IP address if a hybrid setup is used.
   - Start with [strobe-microscope-UI](notebooks-api/strobe-microscope-UI.ipynb) for microscope control. 
   - The syringe pump control can be accessed via [syringe-pump-ui.ipynb](notebooks-api/syringe-pump-ui.ipynb).
   - Then [UI-integrated.ipynb](notebooks-api/UI-integrated.ipynb) for the complete interface.

2. Data acquistion:
    - For imaging acquisiton, used the custom scripts in [data-acquisition-analysis](data-acquisition-analysis/)
    - **NOTE:** These shared files are only compatible with the custom-built, open-frame inverted microscope with a glass heater from [Cicuta Group](https://people.bss.phy.cam.ac.uk/~pc245/). This microscope is equipped with a Nikon 40x CFI Plain Fluor air objective lens (numerical aperture 0.75) and a Teledyne FLIR BFS-U3–70S7M-C camera with a 7.1 MP Sony IMX428 monochrome image sensor (Kals et al., 2024). 

3. For image analysis:
   - Use the ImageJ macros in [data-acquisition-analysis](data-acquisition-analysis/)
   - Run [plot-intensity.py](YFP-results/plot-intensity.py) for generating intensity plots

## Contributing

Please feel free to submit issues and enhancement requests.

## License

The source codes located in the repository are released under the [GPL-3.0 license](https://www.gnu.org/licenses/gpl-3.0.en.html) and the data and documentation are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Contact

Pierre Padilla-Huamantinco @biodotpe - pgpadilla@uc.cl

## Acknowledgements

I would like to thank the [Cicuta Group](https://people.bss.phy.cam.ac.uk/~pc245/) at the University of Cambridge for their contributions to the experimental design, resources support, and high-throughput imaging pipeline, and the [Wenzel Lab](https://wenzel-lab.github.io/en/) for providing the open-source instruments used in this project and the continuous support throughout this internship and the Thesis project.

I also acknowledge the support from the Institute for Biological and Medical Engineering and Pontificia Universidad Católica de Chile for funding this internship project.

## Citation

If you use this work in your research, please cite it as:

Padilla-Huamantinco, P. (2025). *Integration and Validation of Modular Open-Source Platform for Droplet Microfluidics*. Internship Report, Pontificia Universidad Católica de Chile.

@misc{padillahuamantinco2025,
  author       = {Padilla-Huamantinco, Pierre},
  title        = {{Integration and Validation of Modular Open-Source Platform for Droplet Microfluidics}},
  year         = {2025},
  publisher    = {Pontificia Universidad Católica de Chile},
  url          = {https://github.com/biodotpe/internship-report-2025},
  note         = {Internship Report, https://github.com/biodotpe/internship-report-2025},
  howpublished = {\url{https://github.com/biodotpe/internship-report-2025}}
}