<p align="center">
  <img src="https://github.com/earajr/MARTIN/blob/master/resources/MARTINlogo_small.png?raw=true">
</p>

# MARTIN

MARTIN is a graphical user interface developed as part of the Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather Information and Forecasting Techniques) project. MARTIN was originally written by Alexander Roberts (NCAS and University of Leeds). MARTIN allows users to open imagery and navigate backward and fowrard in time through forecast and analysis imagery for a wide variety of variables. An annotation layer allows users to draw directly into the GUI to highlight particular features while allowing the background image to the changed to a different variable, model initialisation or forecast lead time. Imagery with transparent backgrounds (such as streamlines) can also be added to the annotation layer to produce figures with multiple variables. When all annotations have been completed the reusltant image can be saved as a single image.
The imagery that MARTIN was developed for is that produced by the GCRF African SWIFT GFS plotting suite that produces forecast imagery from the Global Forecast System (GFS) Model. The plotting suite can be found here (https://github.com/earajr/GFS_plotting doi: 10.5281/zenodo.3678537). This document is an overview of the features and way in which the MARTIN software can be used. While the GFS imagery is produced by the plotting suite is the primary use case, other imagery can be viewed and annotated using MARTIN as long as the correct directory structure and naming convecntions are adhered to.

## Github repository

To use MARTIN it is important to first know that there is no need to clone this repository or run the python code. The code is included here in order to facilitate any modification of the code required by users. However if no modification is required then it is advised that you download the executables included in the "dist" directory. The executables included are for Windows and Linux (Mac users will need to clone the repository and compile thier own executable). 

## Required directory structure and file naming convention

📂**MARTIN**  
├── 📜**MARTIN_executable**  
├──📂**Model**  
:├──📂**Domain**  
::├──📂**Initialisation Date**  
:::├──📂**Variable**  
::::├──📜**Image files**  
