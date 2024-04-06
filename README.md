# Calistar wiki

Check out the [wiki](https://github.com/dirtdigger/fleur_de_cali/wiki) for a step-by-step guide to Calistar!

# Calistar (formerly Fleur de Cali)

![Two examples](img/120x3_and_100x2.jpg?raw=true "120x3 and 100x2 example")

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

