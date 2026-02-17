# Calistar and Calitower Z

Check out the [wiki](https://github.com/dirtdigger/fleur_de_cali/wiki) for a step-by-step guide to Calistar! Calitower Z functions just the same way.

# Calistar (formerly Fleur de Cali)

![Two examples](img/calistar/120x3_and_100x2.jpg?raw=true "120x3 and 100x2 example")

This is a free, open source, parametric tool used for adjusting the dimensional correctness and skew of your printer. This model performs a similar function to other prints such as Califlower, but has no relation to nor has been derived from any part of those. Turns out that the math behind printer skew calibration has been around since Euclid, and its application to 3D printers is well-documented on other open source project's websites like Klipper. Getting the best performance out of your printer shouldn't be behind a paywall.

Parameters you can control within the Cadquery source code:

- Number of measure points for each axis, up to 5 (default 3)
- Thickness of the grid separator pieces (default is 4mm)
- Total width of the print (default 120)
- Height of the print (default 4mm)

Features:

- Parametric design. Try this with other calibration prints: scale up the model by 20%. You'll find your print time and material used increase by up to 50% since the thickness of the print also increases. Using this design, load up a different stl to keep the thickness the same. Your print time and material used only increase by about 20%
- Bigger is better. No calipers are perfect. Printing larger calibration prints decreases the relative error of your measurements. Included is up to 180mm full size, but make sure you've got calipers that can go that large before printing.
- Multiple measurement points. Measure as many locations as you want up to three times. If you get bored of measuring, stop. If you only want to measure two outermost points since they give the highest signal-to-noise ratio, do that. The spreadsheet is smart enough to figure it out. Just make sure for every outer measurement you have a corresponding inner measurement to offset incorrect flow calibration.
- Know when to stop. Along with offsets, error estimation based on the variance of your measurements and the error in your calipers are provided. If you're probably fixing noise, the spreadsheet will tell you.

Stl and step files that are included are all 4mm tall and have varying thickness depending on the size of the print. The files are named calistar_{print width}x{number of measurements per axis}.stl.

Note about Enders and other budget printers: the movement on the x-axis is non-linear, [see here](https://klipper.discourse.group/t/correct-dimensional-accuracy/6093/5) for discussion on the matter. Calistar works on the principle that movement in each axis is linear, and therefore cannot be used to calibrate the dimensional accuracy of such printers. However, it _can_ be used to calculate and fix your printer's skew.

# Calitower Z - an addition to Calistar

<img src="img/calitower_z/calitower_z_120x3_example.jpg?raw=true" alt="Calitower Z example" height="500">

Just as Calistar, Calitower Z is a free, open source, and parametric tool used to adjust a 3D printer's dimensional accuracy. While Calistar calibrates the x- and y-axis, Calitower Z sets out to do exactly that, just for the 3D printer's z-axis. Calitower Z was inspired by Calistar and is designed based on Calistar's core principles. Simply transfer the knowledge gained about Calistar to Calitower Z and you will be good to go to get your 3D printer's z-axis dialed in. Note that Calitower Z does not support a z-axis scew calibration.

__Notes on Printing__

- Use a layer height of 0.2 mm (or 0.1 mm). Otherwise, the nominal distance values between two measurement points are not guaranteed to be 120 mm, 80 mm, and 40 mm!
- Use the correct Calitowre Z version for the type of printed filament.
    - Rather stiff polymers (PLA, PETG, ABS, ASA, PC, Nylon, etc.) can easily be printed without any stiffening support structure. The correct files are the "calitower_z_stiff_<...>.<file_type>".
    - Flexible polymers (TPU, PEBA, etc.) require stiffening support structure. The correct files are the "calitower_z_flex_<...>.<file_type>".

__Notes on measuring__

- While the outer measurements are likely to represent the 3D printer's calibration quite accurately, the inner measurements might not. Even though bridging sections are kept at a minimum distance, their measurements are likely not 100 % accurate. The reasons are two-fold:
    - The droop will be ever so slight.
    - The extruded filament does not get squished against an underlying layer, but can radially extend almost equally in all directions.
    - Nevertheless, when handling these measurements diligently and taking one or two more samples per pair of measurment points, the results should be quite precise. That is at least what empirically showed.

__Notes on provided files__

- Calitower Z is currently only available in a 120x3 version. So a nominal 120 mm measurement height (144 mm print height required) with three distances for outer and inner measurements, respectively
- All the .step and .stl files provided in this repository can also be found on [printables.com](https://www.printables.com/model/1600089-calitower-z-an-addition-to-the-open-source-calista). Additionally, .3mf project as well as .bgcode presliced print files are available there.
- Regarding the calibration worksheets for Calitower Z kindly refer to the section [Browser-based calibration worksheet](#browser-based-calibration-worksheet).

# Browser-based calibration worksheet

The web-based calibration worksheet is Markdown that has been written to be compiled with [Material for Mkdocs](https://squidfunk.github.io/mkdocs-material/). A compiled version is available on [Printables](https://www.printables.com/model/778188-calistar-parametric-open-source-alternative-to-cal), simply unzip `calistar_browser.zip` and open `index.html` in a web browser.  

Note for the Calitower Z: Currently, only the "Parametric Skew Calibration.xlsx" has been modified to include dedicated input sections and output values for the z-axis. However, the browser-based version can be used just as well. Simply enter the z-measurements into either the x or y value sections and leave the rest empty. The results shown for the corresponding axis now refer to the z-axis.


# Excel-based calibration worksheet

An Excel-based calibration worksheet is included in the repo. It was created in Google Sheets, and has been tested in Excel and LibreOffice Calc. Using it with any other spreadsheet tool is unsupported and may result in errors that will not be addressed.

# License

Calistar source code and stls are distributed under GPL3 license. 

[jSpreadsheets](https://github.com/jspreadsheet/ce), [jSuites](https://github.com/jsuites/jsuites), and [Plotly Javascript](https://plotly.com/javascript/is-plotly-free/) libraries are also included in the repository, and are re-distributed under the MIT license.
