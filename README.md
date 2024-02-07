# Biologic_live_data_plotter
This is a Python-based GUI for live monitoring of cyclic voltammetry (CV) data in the proprietary .mpr files format. The tool was initially developed due to Biologic's severely lackluster plotting options. The scipt only reads the files and this actions does not interfere with the dala collection and saving performed by Biologic.

Requirements:
- The Galvani package (https://github.com/echemdata/galvani). Used for decyphering the binary proprietary data format .mpr which Biologic saves in.
- The mprReader package which is merely a small homemade script for data handling and wrangling.

The folder 'EC data' contains a few working examples which can be loaded using the GUI.